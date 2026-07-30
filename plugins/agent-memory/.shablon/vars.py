#!/usr/bin/env python3
"""Render context for the agent-memory doc surfaces.

The facts come from scripts/memoryctl.py: the code that enforces a cap is
its single source, and this script only formats it for prose. Runs with
cwd at the plugin root (the directory containing .shablon/).
"""

from __future__ import annotations

import importlib.util
import json
import types
from pathlib import Path


def load_memoryctl() -> types.ModuleType:
    path = Path("scripts/memoryctl.py")
    spec = importlib.util.spec_from_file_location("memoryctl", path)
    assert spec is not None and spec.loader is not None, f"cannot import {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ctl = load_memoryctl()
print(
    json.dumps(
        {
            "caps": {
                "system_file": f"{ctl.MAX_SYSTEM_FILE_CHARS:,}",
                "injection": f"{ctl.MAX_INJECTION_CHARS:,}",
            },
            "defaults": {
                "root": ctl.DEFAULT_ROOT,
                "agent_id": ctl.DEFAULT_AGENT_ID,
            },
        }
    )
)
