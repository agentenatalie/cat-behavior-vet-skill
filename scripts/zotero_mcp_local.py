#!/usr/bin/env python3
"""Launcher for zotero-mcp that forces the local API endpoint to 127.0.0.1.

Reason: pyzotero hardcodes http://localhost:23119/api. On some macOS setups,
the Zotero 7+ local API returns 503 when reached via the `localhost` hostname
(IPv6/Host-header quirk) but works on 127.0.0.1. We monkeypatch the
endpoint at startup instead of editing the installed package.

Invoke with the zotero-mcp venv's python:
  ~/.local/pipx/venvs/zotero-mcp-server/bin/python zotero_mcp_local.py serve
"""
import pyzotero._client as _c

_orig_init = _c.Zotero.__init__


def _patched_init(self, *args, **kwargs):
    _orig_init(self, *args, **kwargs)
    ep = getattr(self, "endpoint", "")
    if isinstance(ep, str) and "localhost:23119" in ep:
        self.endpoint = ep.replace("localhost:23119", "127.0.0.1:23119")


_c.Zotero.__init__ = _patched_init

from zotero_mcp.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
