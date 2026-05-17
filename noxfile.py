from __future__ import annotations

import shutil
from pathlib import Path

import nox

nox.options.sessions = ["lint", "tests-3.10", "build", "audit"]

PYTHON_VERSIONS = ["3.10", "3.12"]


def clean_build_artifacts() -> None:
    for path in (Path("build"), Path("dist"), Path("vse_sim.egg-info")):
        if path.exists():
            shutil.rmtree(path)


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    session.install("-e", ".[test]")
    session.run(
        "python",
        "-m",
        "pytest",
        "--doctest-modules",
        "--cov=.",
        "--cov-fail-under=100",
        "--cov-report=term-missing:skip-covered",
        "--cov-report=xml:coverage.xml",
        "--cov-report=html:htmlcov",
        "--junitxml=pytest-results.xml",
    )


@nox.session(python="3.10")
def lint(session: nox.Session) -> None:
    session.install("-e", ".[lint]")
    session.run("python", "-m", "ruff", "format", "--check", ".")
    session.run("python", "-m", "ruff", "check", ".")
    session.run("validate-pyproject", "pyproject.toml")


@nox.session(python="3.10")
def build(session: nox.Session) -> None:
    session.install("-e", ".[publish,build-check]")
    clean_build_artifacts()
    session.run("python", "-m", "build")
    artifacts = [str(path) for path in sorted(Path("dist").iterdir())]
    wheels = [path for path in artifacts if path.endswith(".whl")]
    session.run("python", "-m", "twine", "check", *artifacts)
    session.run("check-wheel-contents", *wheels)


@nox.session(python="3.10")
def audit(session: nox.Session) -> None:
    session.install("-e", ".[audit]")
    session.run(
        "python",
        "-m",
        "pip_audit",
        "--skip-editable",
        "--progress-spinner",
        "off",
        ".",
    )
