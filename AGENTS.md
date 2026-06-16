# Documents for both humans and coding agents

* [README.md](./README.md)

# Documents for coding agents

* [./.agents/docs/OVERVIEW.md](./.agents/docs/OVERVIEW.md) ... project overview.
* [./.agents/docs/ARCHITECTURE.md](./.agents/docs/ARCHITECTURE.md) ... library structure and design notes.
* [./.agents/docs/JOURNAL.md](./.agents/docs/JOURNAL.md) ... chronological findings, decisions, and work history.
* [./.agents/docs/LTM/INDEX.md](./.agents/docs/LTM/INDEX.md) ... long-term memory index for durable project knowledge under `./.agents/docs/LTM/`.
* [./.agents/docs/TODO.md](./.agents/docs/TODO.md) ... open to-do items for interpretation datasets, locales, API docs, and lookup coverage.
* [./.agents/skills/](./.agents/skills/) ... local memory-maintenance skills for consolidating `JOURNAL.md`, LTM documents, and canonical project docs.

# Rules and protocols

## General

* This repository is the home for `fortune-telling-core-interpreter`, a Python package that contributes interpretation contracts, locale resolution, locale-aware registries, and reference interpretation datasets to the `fortune_telling_core` namespace.
* This package depends on the sibling `fortune-telling-core` project at `../fortune-telling-core`. The core package owns structural readings, engines, traditions, symbols, serialization helpers, errors, and namespace package setup.
* This package extends the `fortune_telling_core` namespace through the core package's `pkgutil.extend_path` declarations. Do not add a top-level `src/fortune_telling_core/__init__.py` here.
* Keep namespace contributions narrow: this package ships root interpretation modules plus leaf `*/interpretation/` packages under existing traditions.
* Keep project knowledge in the agent docs as the implementation evolves.
* Prefer existing project patterns over introducing new frameworks or conventions.
* Keep interpretation data typed, deterministic, and testable. Lookup should operate on stable structural ids from core readings.
* Interpretation text is externalized as data, not held in code. Translatable strings live in JSON locale bundles under `<family>/interpretation/locales/<dataset>/<locale>.json` (schema and loader in `fortune_telling_core._interpretation_bundle`). Builders stay in code and derive structure (keys, keyword tokens, the set/order of signs/stems/cards) from core; bundles supply only `templates` and `vocab` strings. en-GB, fr-FR, and ja-JP are authored bundles; en-US is derived from en-GB by spelling normalization. Add a locale by adding bundle files, not code.
* Do not move structural engine logic, random draw mechanics, or tradition calculation code into this package. Those belong in `fortune-telling-core`.
* When a durable decision, pitfall, or investigation result matters to future work, append it to `.agents/docs/JOURNAL.md`.

## File Management

* Work summaries belong under `./.agents/docs`, not under `/tmp`.
* Temporary files belong under `./.agents-workspace/tmp`, not under `/tmp`.
* Never delete user files without permission. Only safe to delete: files you created in the current session under `./.agents-workspace/tmp/`.
* Keep generated scratch artefacts out of source directories unless they are part of the requested deliverable.
* Do not copy generated caches, wheels, or virtualenv files into agent docs or source directories.

## Building and Testing

* The project stack is Python 3.12+ with a `src/` package layout.
* The package depends on `fortune-telling-core` and should normally be installed with the sibling core checkout during local development.
* When fixing a bug, add a focused regression test whenever the codebase has a practical test harness.
* Do not report a change as complete until the relevant checks have been run, or until you explicitly state why they could not be run.

## Local Lint Gate

Before reporting a code change as done, run the project's canonical formatter, linter, type-checker, and tests once those commands exist. Record the current commands in this section when the stack is expanded.

Current stack: Python package with `pyproject.toml`, `src/fortune_telling_core`, and `tests`.

Always use this project's virtualenv at `./.venv` for Python tooling. The bare `python`/`pip` on `PATH` resolves to the pyenv-global interpreter, not this repo's venv, so activate the venv (`source .venv/bin/activate`) or call the venv binaries explicitly (`./.venv/bin/python`, `./.venv/bin/pip`). Never `pip install` into the global/pyenv interpreter. This package has its own `./.venv`; do not reuse the sibling core virtualenv.

Canonical setup:

* Create the virtual environment: `python3 -m venv .venv`
* Install for development: `./.venv/bin/pip install -e ../fortune-telling-core -e . ruff mypy pytest`

Canonical gate:

* Format: `./.venv/bin/ruff format src tests`
* Lint: `./.venv/bin/ruff check src tests`
* Type-check: `./.venv/bin/mypy src tests`
* Test: `./.venv/bin/pytest`

## Shell Pitfalls (prezto defaults)

The user's shell uses prezto, which sets aliases and options that can break non-interactive scripts:

* `cp src dst` may prompt interactively when `dst` exists. Prefer explicit overwrite-safe commands.
* `cat > file <<'EOF'` and `echo > file` can fail with `file exists` when the target exists. Use the repository editing tools rather than shell redirection for tracked files.
* `rm file` may prompt for confirmation. Never delete user files unless the task explicitly requires it.

## Git Workflow

* Never make discretionary commits. Commit only when the user asks.
* If commits are requested, sign them with `-S` unless the user gives different instructions.
* Preserve unrelated work in the tree. Do not revert changes you did not make.
* This repo and `../fortune-telling-core` may both be involved in namespace-package work. Keep changes scoped to the requested repo unless the task explicitly asks for sibling updates.

## Documentation

* Append new findings to `JOURNAL.md`; do not edit existing entries in place except through established memory-consolidation workflows.
* In repo-authored documentation (`AGENTS.md`, `README.md`, `.agents/docs/**`), never use full-width parentheses. Use half-width parentheses.
* Same for full-width colons. Use a half-width colon followed by a space.
