#!/usr/bin/env python3
"""Smoke-test OneCode Cloud HTTP API (Bearer) against api.onecode.ninja.

Requires:
  export ONECODE_API='oc_…'   # key with data/read + data/write (and apps/exec optional)

Usage:
  cd /path/to/onecode && .venv/bin/python scripts/smoke_api.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    key = os.environ.get('ONECODE_API', '').strip()
    if not key:
        print('ERROR: set ONECODE_API to a Bearer API key from https://onecode.ninja/api-keys')
        print('       (attach rights: data/read, data/write)')
        return 1

    import httpx
    from onecode.api.utils import api_token, api_url
    from onecode.api.v1 import data as data_api

    print('API_URL:', api_url())
    print('Auth:', api_token()['Authorization'][:18] + '…')

    health = httpx.get('https://api.onecode.ninja/v1/health', timeout=30)
    print('health:', health.status_code, health.text.strip())
    health.raise_for_status()

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        src = td_path / 'smoke.txt'
        payload = 'onecode api smoke\n'
        src.write_text(payload, encoding='utf-8')
        remote = 'api-client-smoke/smoke.txt'

        print('upload →', remote)
        data_api.upload(str(src), remote, show_progress=False)

        out = td_path / 'dl'
        out.mkdir()
        print('download ← api-client-smoke/')
        files, max_reached = data_api.download(
            'api-client-smoke/', str(out), show_progress=False
        )
        print('files:', files, 'max_reached:', max_reached)
        got = list(out.rglob('smoke.txt'))
        if not got:
            raise SystemExit(f'FAIL: smoke.txt missing under {out}: {list(out.rglob("*"))}')
        text = got[0].read_text(encoding='utf-8')
        if text != payload:
            raise SystemExit(f'FAIL: content mismatch: {text!r}')
        print('OK: upload + download round-trip')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
