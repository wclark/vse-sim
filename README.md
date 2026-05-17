# VSE Sim

VSE Sim provides Python tools for running Voter Satisfaction Efficiency (VSE)
simulations for voting methods.

The package is published as `vse-sim` and imports as `vse_sim`. The original
top-level modules, such as `vse` and `voterModels`, are still installed for
older scripts and examples.

For background on the metric and published simulation results, see the
[Voter Satisfaction Efficiency FAQ](http://electionscience.github.io/vse-sim/).

## Install

Install the released package from PyPI:

```shell
python -m pip install vse-sim
```

In a notebook, use `%pip` so the package is installed into the active kernel:

```python
%pip install vse-sim
```

For reproducible notebooks or environments, pin a released version:

```shell
python -m pip install "vse-sim==0.1.2"
```

To install the latest code from GitHub instead of PyPI:

```shell
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@main"
```

## Basic Usage

Prefer the modern `vse_sim` namespace for new code:

```python
import vse_sim as vse
from vse_sim import Mav, PolyaModel, Score, baseRuns, medianRuns
from vse_sim.debug_dump import setDebug

setDebug(False)

results = vse.run_simulation(
    PolyaModel(),
    [[Score(), baseRuns], [Mav(), medianRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="quickstart",
)

results.df.head()
```

Work with results using pandas-native helpers and DataFrame aliases:

```python
frame = results.dataframe
summary = results.summarize(group_by="method")
leaderboard = results.leaderboard()
report_tables = results.report()
axes = results.plot_vse(group_by="method", kind="barh")
```

Use the convenience helpers when you want DataFrames directly:

```python
frame = vse.run_simulation_dataframe(
    PolyaModel(),
    [[Score(), baseRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="quickstart-frame",
)

voters = PolyaModel()(5, 4)
voter_utilities = voters.to_dataframe(wide=True)
ballots = Score().ballots_dataframe(voters)
scores = Score().results_dataframe(ballots)
```

For notebook work, the recommended starting point is the copy-paste template in
[Jupyter notebook template](docs/JUPYTER_EXAMPLES.md). It has one setup cell
with imports, reusable report helpers, and plotting functions, followed by a
larger simulation/reporting cell that produces summary tables, a heatmap,
distribution plots, and method-level scoring tables.

`CsvBatch` remains available when you want the legacy batch object or metadata
CSV writer:

```python
from vse_sim import CsvBatch

csvs = CsvBatch(
    PolyaModel(),
    [[Score(), baseRuns], [Mav(), medianRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="quickstart",
)
csvs.saveFile("quickstart-results")
```

Legacy imports remain supported:

```python
from vse import CsvBatch
from voterModels import PolyaModel
```

See [Installation and notebook usage](docs/INSTALL.md) for environment setup,
including GitHub installs and notebook workflow notes.

## Development

Create or activate a Python 3.10+ environment, then install the project in
editable mode with development tools:

```shell
python -m pip install -e ".[dev,publish]"
```

Install local Git hooks if you want pre-commit checks:

```shell
pre-commit install
```

Run the default local quality gate:

```shell
nox
```

The default Nox gate validates metadata, runs Ruff format/lint checks, runs the
Python 3.10 test and coverage suite, builds the package, validates distribution
metadata and wheel contents, and audits dependencies.

Run Python 3.12 tests explicitly when that interpreter is available:

```shell
nox -s tests-3.12
```

Useful direct commands:

```shell
python -m pytest --doctest-modules --cov=. --cov-fail-under=100
python -m ruff format --check .
python -m ruff check .
python -m build
python -m twine check dist/*
check-wheel-contents dist/*.whl
python -m pip_audit --skip-editable --progress-spinner off .
```

Coverage reports are written to `htmlcov/`, `coverage.xml`, and
`pytest-results.xml` when the full coverage command is run.

## Repository Layout

- `vse_sim/`: modern package facade for new imports.
- Root Python modules: legacy-compatible modules that remain importable.
- `test/`: coverage and compatibility tests.
- `data/`: retained legacy/reference data artifacts.
- `docs/`: GitHub Pages content plus install and release notes.

See [Release process](docs/PUBLISHING.md) for the PyPI publishing workflow.
