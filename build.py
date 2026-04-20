#!/usr/bin/env python3
"""CLI: build a Vista Social bulk CSV from a batch config.

Usage:
  python build.py batches/<batch_name>/config.py           # build only
  python build.py batches/<batch_name>/config.py --push    # build + git push
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

import vista_bulk


def load_config(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("batch_config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.CONFIG


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path, help="path to batch config.py")
    parser.add_argument("--push", action="store_true", help="git add/commit/push after build")
    args = parser.parse_args()

    config_path = args.config.resolve()
    repo_root = Path(__file__).parent.resolve()
    batch_dir = config_path.parent

    if not config_path.is_file():
        sys.exit(f"Config file not found: {config_path}")

    config = load_config(config_path)
    result = vista_bulk.build_batch(config, batch_dir=batch_dir, repo_root=repo_root)

    print(f"Wrote {result.rows} rows to {result.csv_path}")
    print(f"  carousel rows: {result.carousel_rows}")
    print(f"  static rows:   {result.static_rows}")

    if args.push:
        rel = batch_dir.relative_to(repo_root).as_posix()
        git("add", rel, cwd=repo_root)
        # Allow no-op commits to succeed silently
        rv = subprocess.run(
            ["git", "-c", "user.email=saurabh.thapa@qubit.capital",
             "-c", "user.name=Saurabh Thapa",
             "commit", "-m", f"Build batch {batch_dir.name}"],
            cwd=repo_root,
        )
        if rv.returncode != 0:
            print("Nothing new to commit (media may already be pushed).")
        git("push", cwd=repo_root)
        print("Pushed to GitHub.")


if __name__ == "__main__":
    main()
