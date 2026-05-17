# Release Process

`vse-sim` is published on PyPI and uses GitHub Actions Trusted Publishing. No
PyPI API token is stored in the repository.

## Current Package

- Distribution name: `vse-sim`
- Import namespace: `vse_sim`
- Current public version: `0.1.0`
- PyPI: <https://pypi.org/project/vse-sim/>
- GitHub releases: <https://github.com/wclark/vse-sim/releases>
- Publish workflow: `.github/workflows/python-publish.yml`
- GitHub Actions environment: `pypi`

## Before A Release

1. Choose the next version number.
2. Update both version locations:
   - `pyproject.toml`
   - `vse_sim/__init__.py`
3. Update release notes or documentation that mention the current version.
4. Run the full local validation gate:

   ```shell
   python -m pip install -e ".[dev,publish]"
   nox
   ```

5. Run additional interpreter coverage when available:

   ```shell
   nox -s tests-3.12
   ```

6. Confirm the package builds and installs cleanly from the generated wheel if
   the release changes packaging behavior.

## Publishing

Publish by creating a GitHub release whose tag matches the package version with
a leading `v`, for example `v0.1.0`.

The release workflow runs when a GitHub release is published. It:

1. Builds the source distribution and wheel.
2. Runs `twine check dist/*`.
3. Runs `check-wheel-contents dist/*.whl`.
4. Publishes to PyPI through Trusted Publishing.
5. Uploads PyPI attestations through the PyPA publish action.

## After Publishing

Verify the new release:

```shell
python -m pip index versions vse-sim
```

Run a clean install smoke test:

```shell
python -m venv .package-smoke
.package-smoke/Scripts/python -m pip install --upgrade pip
.package-smoke/Scripts/python -m pip install "vse-sim==0.1.0"
.package-smoke/Scripts/python -m pip check
```

Then verify imports:

```shell
.package-smoke/Scripts/python -c "from vse_sim import CsvBatch, PolyaModel; from vse import CsvBatch as LegacyCsvBatch; assert CsvBatch is LegacyCsvBatch; print('ok')"
```

On macOS or Linux, use `.package-smoke/bin/python` instead of
`.package-smoke/Scripts/python`.

## Trusted Publishing Configuration

The PyPI trusted publisher should match these values:

- Project name: `vse-sim`
- Owner: `wclark`
- Repository: `vse-sim`
- Workflow filename: `python-publish.yml`
- Environment: `pypi`

If publishing fails with a Trusted Publishing error, check those values first,
then confirm the workflow job still has `id-token: write` and `environment:
pypi`.
