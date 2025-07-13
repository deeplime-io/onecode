# SPDX-FileCopyrightText: 2023-2024 DeepLime <contact@deeplime.io>
# SPDX-License-Identifier: MIT

import asyncio
import os
from typing import List, Tuple

from ...base.decorator import check_type
from ._concurrent.data.download import async_downloads
from ._concurrent.data.upload import async_upload


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
    Download the specified file(s) from OneCode Cloud storage.

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
        async_downloads(
            prefix,
            path_to,
            expiry,
            max_concurrent,
            chunk_size,
            show_progress,
        )
    )
    return res


@check_type
def upload(
    file: str,
    path_to: str,
    expiry: int = 600,
    chunk_size: int = 1024 * 1024,  # 1 MB
    show_progress: bool = True
) -> Tuple[List[str], bool]:
    """
    Upload the specified file to OneCode Cloud storage.

    Args:
        file: local machine path of the file to upload.
        path_to: path within the OneCode Cloud storage.
        expiry: time in seconds after which the upload expires.
            Defaults to 600 seconds.
        chunk_size: when uploading big files, write by chunk to limit memory usage.
            Defaults to 1 MB
        show_progress: whether the progress bar is displayed.
            Defaults to True

    Raises:
        ValueError: if response status is not 200 (OK).

    """

    asyncio.run(
        async_upload(
            file,
            path_to,
            expiry,
            chunk_size,
            show_progress
        )
    )
