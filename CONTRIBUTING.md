# Contributing to raman_neo

Thanks for your interest in improving `raman_neo`.

## Development setup

```bash
git clone https://github.com/laumiulun/raman_neo.git
cd raman_neo
python -m venv .venv && source .venv/bin/activate
make install-dev        # editable install + dev tools + pre-commit hooks
```

## Workflow

1. Create a branch off `main`: `git checkout -b feature/my-change`.
2. Make your change with tests.
3. Run the checks locally:
   ```bash
   make format   # ruff format + autofix
   make lint     # ruff check + format --check
   make test     # pytest
   ```
   `pre-commit` runs the same lint/format hooks on every commit.
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a pull request. CI (lint + test matrix on Linux/macOS/Windows,
   Python 3.10–3.13) must pass before review.

## Style & conventions

- Formatting and linting are enforced by [ruff](https://docs.astral.sh/ruff/)
  (configured in `pyproject.toml`); do not hand-format.
- `raman_neo` mirrors the module and class structure of
  [EXAFS_Neo](https://github.com/laumiulun/EXAFS-Neo-Public); keep the mapping
  documented in the README intact when adding features (a new EXAFS concept
  should map to a clearly analogous Raman one).
- New physics/operators need unit tests under `tests/`; keep the fast synthetic
  end-to-end test (`tests/test_end_to_end.py`) passing.

## Releasing (maintainers)

1. Bump `version` in `pyproject.toml` and `raman_neo/_version.py`.
2. Move the `[Unreleased]` changelog section under the new version.
3. Tag and push: `git tag vX.Y.Z && git push --tags`.
4. Publish a GitHub Release for the tag — the `publish` workflow builds and
   uploads to PyPI via trusted publishing.
