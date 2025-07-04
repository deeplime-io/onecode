# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Tuple

import httpx
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn
)

from ...base.decorator import check_type
from ...base.enums import ConfigOption, Env
from ...base.project import Project


@check_type
def download(
    prefix: str,
    path_to: str = os.getcwd(),
    expiry: int = 600,
    max_concurrent: int = 3,
    chunk_size: int = 1024 * 1024,  # 1 MB
    show_progress: bool = True
) -> Tuple[List[str], bool]:
    """
    Args:
        prefix: prefix path within the OneCode Cloud storage.
            Any file matching the prefix will be downloaded.
        path_to: local machine path where files will be downloaded.
            Defaults to current working directory.
        expiry: time in seconds after which the download expires.
            Defaults to 600 seconds.
        max_concurrent: maximum of concurrent downloads.
            Defaults to 3
        chunk_size: when downloading big files, write by chunk to limit memory usage.
            Defaults to 1 MB
        show_progress: whether the progress bar is displayed.
            Defaults to True

    Files matching `{path}*` in the storage will be downloaded, with a limit of 50 files.
    For instance:
     ```python
    files, max_reached = download('/uploads/test/polygon.')

    # would match
    # /uploads/test/polygon.shp
    # /uploads/test/polygon.dbx
    # /uploads/test/polygon.prj

    files, max_reached = download('/uploads/test/')

    # would match
    # /uploads/test/image.png
    # /uploads/test/assets/another_image.jpg
    # /uploads/test/polygon.shp
    # /uploads/test/polygon.dbx
    # /uploads/test/polygon.prj

    ```

    If the limit of 50 files is reached with more files to match, `max_reached` will be True.

    Returns:
        A tuple with the list of files downloaded and whether or not
        the max number of files was reached.

    Raises:
        ValueError: if response status is not 200 (OK).

    """

    res = asyncio.run(
        _run_downloads(
            prefix,
            path_to,
            expiry,
            max_concurrent,
            chunk_size,
            show_progress,
        )
    )
    return res


async def _run_downloads(
    prefix: str,
    path_to: str = os.getcwd(),
    expiry: int = 600,
    max_concurrent: int = 3,
    chunk_size: int = 1024 * 1024,  # 1 MB
    show_progress: bool = True
) -> Tuple[List[str], bool]:
    semaphore = asyncio.Semaphore(max_concurrent)
    download_urls: Dict = {}

    async with httpx.AsyncClient() as client:
        download_res = await client.post(
            f'{Project().get_config(ConfigOption.API_URL)}/data/read/download',
            json={
                "path": prefix,
                "expiry": expiry
            },
            headers={'ONECODE_API': os.environ.get(Env.ONECODE_API_TOKEN, '')}
        )
        download_res.raise_for_status()
        download_data: Dict = download_res.json()
        download_urls = download_data.get("urls")

        if show_progress:
            with Progress(
                TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                tasks = [
                    _download_streaming(
                        client,
                        url,
                        filename,
                        path_to,
                        chunk_size,
                        semaphore,
                        progress
                    )
                    for filename, url in download_urls.items()
                ]
                await asyncio.gather(*tasks)
        else:
            tasks = [
                _download_streaming(
                    client,
                    url,
                    filename,
                    path_to,
                    chunk_size,
                    semaphore
                )
                for filename, url in download_urls.items()
            ]
            await asyncio.gather(*tasks)

    return list(download_urls.keys()), download_data.get("max_reached")


async def _download_streaming(
    client,
    url: str,
    filename: str,
    path_to: Path,
    chunk_size: int,
    semaphore: asyncio.Semaphore,
    progress: Progress = None
):
    dest_folder = Path(path_to)
    dest_path = dest_folder / filename
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    async with semaphore:
        try:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", 0))
                task_id = None

                if progress:
                    task_id = progress.add_task(
                        "[cyan]Downloading...",
                        total=total,
                        filename=filename
                    )

                with open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        f.write(chunk)
                        if task_id is not None:
                            progress.update(task_id, advance=len(chunk))

                if task_id is not None:
                    progress.update(task_id, completed=total)
                print(f"✅ {filename}")

        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
