#!/usr/bin/env python3
"""Validate FCP sources and emit LSP-style diagnostics as JSON.

This script is invoked by the VS Code extension. It reads a JSON payload
from stdin with the shape: { "text": string, "path"?: string },
parses the document using the local fcp package, and writes a JSON
object to stdout: { "errors": Diagnostic[], "internalError"?: string }.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict


class Position(TypedDict):
    line: int
    character: int


class Range(TypedDict):
    start: Position
    end: Position


class Diagnostic(TypedDict):
    message: str
    range: Range
    severity: str


class Payload(TypedDict, total=False):
    text: str
    path: str


@dataclass(frozen=True)
class RepoRoot:
    path: Path


def _find_repo_root() -> Optional[RepoRoot]:
    """Discover the repo root that contains `src/fcp`.

    Looks for a directory where `src/fcp/__init__.py` exists so we can
    import the package straight from source. Search order:
    1) `FCP_VSCODE_REPO_ROOT` environment variable, if it exists.
    2) Walk up from this file's location and probe each ancestor.

    Returns a `RepoRoot` on success, or None if no matching root is found.
    Used as a fallback when the installed `fcp` package is unavailable.
    """
    env_root = os.environ.get("FCP_VSCODE_REPO_ROOT")
    if env_root:
        env_path = Path(env_root)
        if env_path.exists():
            return RepoRoot(env_path)

    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        candidate = parent / "src" / "fcp" / "__init__.py"
        if candidate.exists():
            return RepoRoot(parent)
    return None


def _ensure_src_on_path(root: RepoRoot) -> None:
    """Prepend the repo `src` directory to `sys.path` if missing."""
    src = str(root.path / "src")
    if src not in sys.path:
        sys.path.insert(0, src)


def _emit_response(
    *, errors: List[Diagnostic], internal_error: Optional[str] = None
) -> None:
    """Write an LSP-style JSON response to stdout.

    Keys:
    - `errors`: list of diagnostics ready for VS Code.
    - `internalError` (optional): textual details useful for debugging.
    """
    response: Dict[str, Any] = {"errors": errors}
    if internal_error:
        response["internalError"] = internal_error
    json.dump(response, sys.stdout)
    sys.stdout.write("\n")
    sys.stdout.flush()


def _safe_load_payload() -> Optional[Payload]:
    """Read and parse the JSON payload from stdin.

    Tolerates empty input (returns None) and emits a structured error on
    malformed JSON or unexpected shapes. Returns a `Payload` dict on success.
    """
    raw = sys.stdin.read()
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except Exception:
        _emit_response(
            errors=[_simple_error("Failed to decode payload from VS Code.")],
            internal_error=traceback.format_exc(),
        )
        return None

    if not isinstance(data, dict):
        _emit_response(
            errors=[_simple_error("Invalid payload shape (expected object).")]
        )
        return None

    # minimal validation; caller guards on access
    return data  # type: ignore


def _simple_error(message: str) -> Diagnostic:
    """Create a minimal diagnostic that points to the document start."""
    return {
        "message": message,
        "severity": "error",
        "range": {
            "start": {"line": 0, "character": 0},
            "end": {"line": 0, "character": 1},
        },
    }


def _sanitize_position(value: Optional[int], fallback: int) -> int:
    """Convert 1-based positions (parser) to 0-based (LSP).

    Falls back to `fallback` when `value` is not a valid positive int.
    """
    if isinstance(value, int) and value >= 1:
        return value - 1
    return fallback


def _convert_error(err: "FcpError") -> List[Diagnostic]:
    """Translate `fcp` parser errors to LSP diagnostics.

    Extracts ranges from node metadata when available; otherwise defaults
    to a single-character range at the document start.
    """
    diagnostics: List[Diagnostic] = []
    for entry in getattr(err, "msg", []):
        message, node, _ = entry
        start_line = 0
        start_char = 0
        end_line = 0
        end_char = 1

        meta = getattr(node, "meta", None)
        if meta is not None:
            start_line = _sanitize_position(getattr(meta, "line", None), start_line)
            start_char = _sanitize_position(getattr(meta, "column", None), start_char)
            end_line = _sanitize_position(getattr(meta, "end_line", None), start_line)
            end_char = _sanitize_position(
                getattr(meta, "end_column", None), start_char + 1
            )
            if end_line < start_line:
                end_line = start_line
            if end_char < start_char + 1:
                end_char = start_char + 1

        diagnostics.append(
            {
                "message": str(message),
                "severity": "error",
                "range": {
                    "start": {"line": start_line, "character": start_char},
                    "end": {"line": end_line, "character": end_char},
                },
            }
        )
    return diagnostics


class HybridFileSystemProxy:
    """Provide unsaved buffer for main file; fall back to disk for imports."""

    def __init__(self, main_path: Path, contents: str) -> None:
        self.main_path = main_path.resolve()
        self.contents = contents
        self.cache: Dict[Path, str] = {self.main_path: contents}

    def read(self, filename: Path) -> str:
        path = filename
        if not path.is_absolute():
            path = (self.main_path.parent / path).resolve()
        if path == self.main_path:
            return self.contents
        if path in self.cache:
            return self.cache[path]
        data = path.read_text()
        self.cache[path] = data
        return data


def _parse(text: str, path: Optional[str]) -> List[Diagnostic]:
    """Parse FCP text and return diagnostics.

    If `path` is provided, build a hybrid filesystem that serves the unsaved
    buffer for the main file and uses disk for imports; otherwise parse from
    the provided string only. Emits internal errors via `_emit_response`.
    """
    try:
        from fcp.parser import get_fcp_from_string, _get_fcp
        from fcp.error import Logger
    except Exception:
        _emit_response(
            errors=[_simple_error("Failed to import fcp parser modules.")],
            internal_error=traceback.format_exc(),
        )
        return []

    logger = Logger({})

    try:
        if isinstance(path, str) and path:
            main_path = Path(path).resolve()
            filesystem_proxy = HybridFileSystemProxy(main_path, text)
            result = _get_fcp(main_path, filesystem_proxy, logger)
        else:
            result = get_fcp_from_string(text, logger)

        if result.is_err():
            diags = _convert_error(result.err())
            return diags or [_simple_error("Unknown parsing error.")]
        return []
    except FileNotFoundError as exc:
        missing = exc.filename or str(exc)
        return [_simple_error(f"File not found: {missing}")]
    except Exception:
        _emit_response(
            errors=[_simple_error("Failed to evaluate parsing result.")],
            internal_error=traceback.format_exc(),
        )
        return []


def _ensure_fcp_importable() -> Optional[str]:
    """Ensure the `fcp` package is importable.

    Strategy:
    - First, try importing the installed package as-is.
    - If that fails, try to discover a local repo root and add its `src`.
    - Return None on success, or an error message string on failure.
    """
    try:
        import importlib
        import fcp  # type: ignore

        return None
    except Exception:
        # Fall back to local repo discovery
        root = _find_repo_root()
        if root is None:
            return "Unable to import 'fcp' and no local repo found."
        _ensure_src_on_path(root)
        try:
            import fcp  # type: ignore

            return None
        except Exception:
            return "Failed to import 'fcp' even after adding local src to path."


def main() -> None:
    """Entry point: read payload, ensure imports, parse, emit diagnostics."""
    import_error = _ensure_fcp_importable()
    if import_error is not None:
        _emit_response(errors=[_simple_error(import_error)])
        return

    payload = _safe_load_payload()
    if payload is None:
        return

    text: Any = payload.get("text", "")
    if not isinstance(text, str):
        _emit_response(
            errors=[_simple_error("Invalid payload: 'text' must be a string.")]
        )
        return

    path_val: Optional[str] = (
        payload.get("path") if isinstance(payload.get("path"), str) else None
    )
    diagnostics = _parse(text, path_val)
    _emit_response(errors=diagnostics)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        _emit_response(
            errors=[
                _simple_error("Unhandled exception while running FCP diagnostics.")
            ],
            internal_error=traceback.format_exc(),
        )
