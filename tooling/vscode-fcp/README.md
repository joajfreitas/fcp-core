# FCP VS Code Extension

Language support for `.fcp` schema files.

## Features
- Syntax highlighting via TextMate grammar.
- Snippets and completion items for common language constructs and in-file symbols.
- On-type diagnostics powered by the repository's Python parser (invoked in the background).

## Requirements
- Python 3 with access to the `fcp` package from this repository. When you open the workspace with the extension, it will automatically reuse the repo checkout, so no additional installation is needed.

## Extension Settings
- `fcp.pythonInterpreter`: optional absolute path to the Python interpreter the diagnostics runner should use. Leave blank to let the extension try `python3`/`python`.

## Development
- After editing the extension, reload VS Code (`Developer: Reload Window`) to pick up changes.
- Diagnostics rely on the Python modules under `src/fcp`; make sure your workspace uses the same checkout so imports succeed.

## Release Notes

### 0.0.1
- Syntax highlighting, completions, and diagnostics for FCP.
