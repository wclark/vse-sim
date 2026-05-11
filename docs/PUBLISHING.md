# Publishing Checklist

The package metadata is present in `pyproject.toml`, and CI builds both wheel
and source distribution artifacts. This checklist captures the remaining steps
before publishing `vse-sim` to a public Python package index.

## Current Preparation

- Distribution name: `vse-sim`.
- Import namespace: `vse_sim`.
- Runtime dependencies: `numpy`, `scipy`.
- Build backend: `setuptools`.
- Build artifacts checked in CI: wheel and source distribution.
- Distribution metadata check in CI: `twine check dist/*`.

## Pre-Release Checklist

1. Confirm that the `vse-sim` project name is available or controlled on PyPI.
2. Decide the first public version number.
3. Update both version locations:
   - `pyproject.toml`
   - `vse_sim/__init__.py`
4. Confirm the README renders cleanly as the package long description.
5. Run the full validation set:

   ```shell
   python -m pip install ".[dev,publish]"
   python -m pytest --doctest-modules --cov=. --cov-fail-under=100
   python -m build
   python -m twine check dist/*
   ```

6. Install the built wheel in a clean environment and run an import smoke test.
7. Create and push a signed or otherwise trusted release tag.

## TestPyPI Dry Run

Use TestPyPI before the first real release:

```shell
python -m pip install ".[publish]"
python -m build
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*
```

Then install from TestPyPI, using PyPI as an extra index for dependencies:

```shell
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  vse-sim
```

## PyPI Trusted Publishing

Prefer PyPI Trusted Publishing over long-lived API tokens for GitHub Actions
releases. Trusted Publishing uses GitHub Actions OIDC and a short-lived token
minted by PyPI for the configured project.

When ready, configure a trusted publisher on PyPI with:

- Owner: `wclark`
- Repository: `vse-sim`
- Workflow filename: the future publish workflow, for example
  `python-publish.yml`
- Environment: `pypi`

After that PyPI-side setup exists, add a GitHub Actions publish workflow that:

1. Runs on published GitHub releases.
2. Builds `dist/*`.
3. Runs `twine check dist/*`.
4. Publishes with `pypa/gh-action-pypi-publish` and `id-token: write`.

Useful references:

- [Python Packaging User Guide: installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
- [Python Packaging User Guide: building and publishing](https://packaging.python.org/guides/section-build-and-publish/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
