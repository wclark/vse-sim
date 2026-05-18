"""Build or check the generated pdoc API reference."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DOCS = ROOT / "docs" / "api"
MODULES = [
    "vse_sim",
    "vse_sim.compat",
    "vse_sim.data_classes",
    "vse_sim.dataframe",
    "vse_sim.debug_dump",
    "vse_sim.decorators",
    "vse_sim.methods",
    "vse_sim.simulation",
    "vse_sim.strategies",
    "vse_sim.voter_models",
]
PDOC_COMMAND = [
    sys.executable,
    "-m",
    "pdoc",
    "--output-directory",
    "{output}",
    "--docformat",
    "restructuredtext",
    "--footer-text",
    "vse-sim API reference",
    "--edit-url",
    "vse_sim=https://github.com/wclark/vse-sim/blob/main/vse_sim/",
    "--no-search",
    *MODULES,
]


def build_docs(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    command = [argument.format(output=str(output)) for argument in PDOC_COMMAND]
    subprocess.run(command, cwd=ROOT, check=True)


def relative_files(directory: Path) -> set[Path]:
    if not directory.exists():
        return set()
    return {path.relative_to(directory) for path in directory.rglob("*") if path.is_file()}


def changed_files(expected: Path, actual: Path) -> list[str]:
    expected_files = relative_files(expected)
    actual_files = relative_files(actual)
    changes = []

    for path in sorted(expected_files - actual_files):
        changes.append(f"missing from generated docs: {path.as_posix()}")
    for path in sorted(actual_files - expected_files):
        changes.append(f"missing from committed docs: {path.as_posix()}")
    for path in sorted(expected_files & actual_files):
        if not filecmp.cmp(expected / path, actual / path, shallow=False):
            changes.append(f"changed: {path.as_posix()}")

    return changes


def check_docs() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        generated = Path(tmpdir) / "api"
        build_docs(generated)
        changes = changed_files(API_DOCS, generated)

    if changes:
        print("Generated API docs are not current. Run:")
        print("  python tools/build_api_docs.py")
        print()
        print("Differences:")
        for change in changes:
            print(f"  - {change}")
        return 1

    print("Generated API docs are current.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="build docs in a temporary directory and compare them with docs/api",
    )
    args = parser.parse_args()

    if args.check:
        return check_docs()

    build_docs(API_DOCS)
    print(f"Generated API docs in {API_DOCS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
