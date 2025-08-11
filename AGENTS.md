# Agent Guidelines

- Use Python 3.10.
- Place executables in `scripts/`, model backends in `backends/`, and docs in `docs/`.
- Run `python -m py_compile` on changed Python files before committing.
- Keep shell scripts portable by resolving paths relative to the script file.
- Ensure new backends expose a `generate` function returning JSON-serializable data.
