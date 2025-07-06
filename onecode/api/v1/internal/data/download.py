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

from .....base.decorator import check_type
from ....utils import api_token, api_url


@check_type
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
            f'{api_url()}/data/read/download',
            json={
                "path": prefix,
                "expiry": expiry
            },
            headers=api_token()
        )
        if not download_res.is_success:
            raise Exception(
                f"{download_res.status_code}: "
                f"{download_res.json().get('error', 'Unknown error')}"
            )

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


@check_type
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
