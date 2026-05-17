# Installation and Notebook Usage

`vse-sim` is the Python distribution name on PyPI. New code should import from
the `vse_sim` package namespace. Legacy top-level modules such as `vse`,
`methods`, and `voterModels` are still installed for compatibility.

## Install From PyPI

Install the latest released package:

```shell
python -m pip install vse-sim
```

Pin a known release when you need a reproducible environment:

```shell
python -m pip install "vse-sim==0.1.3"
```

Upgrade an existing environment:

```shell
python -m pip install --upgrade vse-sim
```

## Use In Jupyter

Inside notebooks, prefer `%pip` so the package installs into the active kernel:

```python
%pip install vse-sim
```

For reproducible notebooks:

```python
%pip install "vse-sim==0.1.3"
```

Restart the kernel after installing or upgrading if the notebook already
imported an older copy.

## Basic Notebook Example

For serious notebook work, start from the pasteable
[Jupyter notebook template](./JUPYTER_EXAMPLES.md). It has one setup cell with
imports, reusable helpers, reporting functions, and plotting functions, followed
by one larger experiment cell that runs a DataFrame-centric simulation and
builds tables and charts.

The minimal shape is:

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
    seed="notebook-demo",
)

results.df.head()
```

Summarize and plot results directly:

```python
frame = results.dataframe
summary = results.summarize(group_by="method")
axes = results.plot_vse(group_by="method", kind="barh")
```

Get DataFrames directly from common VSE objects:

```python
frame = vse.run_simulation_dataframe(
    PolyaModel(),
    [[Score(), baseRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="notebook-frame",
)

voters = PolyaModel()(5, 4)
voter_utilities = voters.to_dataframe(wide=True)
ballots = Score().ballots_dataframe(voters)
scores = Score().results_dataframe(ballots)
```

Write the result DataFrame in the notebook working directory:

```python
results.to_csv("notebook-results.csv")
```

The full template also shows summary styling, method-by-chooser heatmaps,
boxplots, raw result filtering, candidate score tables, and CSV round-tripping.

## Python Script Example

```python
import vse_sim as vse
from vse_sim import Mav, PolyaModel, Score, baseRuns, medianRuns
from vse_sim.debug_dump import setDebug


def main() -> None:
    setDebug(False)
    results = vse.run_simulation(
        PolyaModel(),
        [[Score(), baseRuns], [Mav(), medianRuns]],
        nvot=5,
        ncand=4,
        niter=3,
        seed="script-demo",
    )
    results.to_csv("script-results.csv")


if __name__ == "__main__":
    main()
```

## Legacy Imports

Older code can keep using the original module names:

```python
from vse import CsvBatch
from voterModels import PolyaModel
```

Prefer `vse_sim` for new notebooks and scripts so future package cleanup can be
introduced behind a stable import namespace.

## Install From GitHub

Use GitHub installs when you need unreleased changes:

```shell
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@main"
```

Install a specific branch, tag, or commit by replacing `main`:

```shell
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@v0.1.3"
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@<branch-name>"
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@<commit-sha>"
```

## Local Development Install

From a repository checkout:

```shell
python -m pip install -e ".[dev,publish]"
```

Run the local quality gate:

```shell
nox
```
