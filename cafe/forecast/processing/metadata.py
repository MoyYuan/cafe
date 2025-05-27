import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, Optional


def get_git_commit_hash() -> Optional[str]:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return None


def get_metadata(
    script: str,
    params: Dict[str, Any],
    api_endpoint: Optional[str] = None,
    record_count: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "script": script,
        "params": params,
        "cwd": os.getcwd(),
        "python_version": str(sys.version.split("\n")[0]),
        "git_commit": get_git_commit_hash(),
    }
    if api_endpoint:
        meta["api_endpoint"] = api_endpoint
    if record_count is not None:
        meta["record_count"] = int(record_count)
    if extra is not None:
        if isinstance(extra, dict):
            meta.update(extra)
    return meta
