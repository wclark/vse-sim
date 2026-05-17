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
python -m pip install "vse-sim==0.1.1"
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
%pip install "vse-sim==0.1.1"
```

Restart the kernel after installing or upgrading if the notebook already
imported an older copy.

## Basic Notebook Example

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

results.frame.head()
```

Summarize and plot results directly:

```python
summary = results.summarize(group_by="method")
axes = results.plot_vse(group_by="method", kind="barh")
```

Write the result DataFrame in the notebook working directory:

```python
results.to_csv("notebook-results.csv")
```

For a full notebook cookbook with copy-paste examples covering voter models,
methods, strategy choosers, media helpers, CSV output, DataFrames, and
compatibility checks, see [Jupyter notebook examples](./JUPYTER_EXAMPLES.md).

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
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@v0.1.1"
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
