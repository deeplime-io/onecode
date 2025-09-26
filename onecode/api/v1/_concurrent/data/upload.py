# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import mimetypes
from pathlib import Path
from typing import Dict

import httpx
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn
)

from .....base.decorator import check_type
from ....utils import api_timeout, api_token, api_url


class _StreamingFile:
    def __init__(
        self,
        file_path: Path,
        chunk_size: int,
        progress: Progress,
        task_id: int
    ):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.progress = progress
        self.task_id = task_id
        self.file = open(file_path, "rb")

    def __len__(self):
        return self.file_path.stat().st_size

    async def __aiter__(self):
        while True:
            chunk = self.file.read(self.chunk_size)
            if not chunk:
                break
            self.progress.update(self.task_id, advance=len(chunk))
            yield chunk
        self.file.close()


@check_type
async def async_upload(
    file: str,
    path_to: str,
    expiry: int = 600,
    chunk_size: int = 1024 * 1024,  # 1 MB
    show_progress: bool = True
):
    file_path = Path(file)
    file_size = file_path.stat().st_size

    mime_type = mimetypes.guess_type(file_path.name)[0]
    if not mime_type:
        mime_type = "application/octet-stream"  # fallback

    headers = {
        "Content-Length": str(file_size),
        "Content-Type": mime_type
    }

    async with httpx.AsyncClient(timeout=api_timeout()) as client:
        upload_res = await client.post(
            f'{api_url()}/data/write/upload',
            json={
                "path": path_to,
                "expiry": expiry
            },
            headers=api_token()
        )
        if not upload_res.is_success:
            raise Exception(
                f"{upload_res.status_code}: "
                f"{upload_res.json().get('error', 'Unknown error')}"
            )

        upload_data: Dict = upload_res.json()
        upload_url = upload_data.get("url")

        if show_progress:
            with Progress(
                TextColumn("[bold blue]Uploading..."),
                BarColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task_id = progress.add_task(f"[cyan]{file_path.name}", total=file_size)
                stream = _StreamingFile(file_path, chunk_size, progress, task_id)

                response = await client.put(
                    upload_url,
                    content=stream,
                    headers=headers,
                )

                response.raise_for_status()
                print("✅ Upload complete:", response.status_code)
        else:
            stream = _StreamingFile(file_path, chunk_size)
            response = await client.put(upload_url, content=stream, headers=headers)
            response.raise_for_status()
            print("✅ Upload complete (no progress):", response.status_code)
