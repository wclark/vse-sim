# Notebook and GitHub Installation

This project is packaged as the `vse-sim` distribution and exposes the modern
`vse_sim` import namespace. The legacy top-level modules are still installed so
older examples continue to work.

## Install From GitHub

Install the current `main` branch directly from GitHub:

```shell
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@main"
```

Install a specific branch, tag, or commit by replacing `main`:

```shell
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@<branch-name>"
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@<tag-name>"
python -m pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@<commit-sha>"
```

For local development from a checkout:

```shell
python -m pip install -e ".[dev]"
```

## Use In Jupyter

Inside a notebook, prefer `%pip` so the package is installed into the kernel's
active Python environment:

```python
%pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@main"
```

Then import from `vse_sim`:

```python
from debugDump import setDebug
from vse_sim import CsvBatch, Mav, PolyaModel, Score, baseRuns, medianRuns

setDebug(False)

csvs = CsvBatch(
    PolyaModel(),
    [[Score(), baseRuns], [Mav(), medianRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="notebook-demo",
)

len(csvs.rows)
```

Save CSV output when you want a file in the notebook working directory:

```python
csvs.saveFile("notebookResults")
```

Legacy imports are still supported:

```python
from vse import CsvBatch
from voterModels import PolyaModel
```

If a notebook already imported an older version, restart the kernel after
installing or upgrading before rerunning imports.

## Future PyPI Install

Once the project is published to PyPI, installation should become:

```shell
python -m pip install vse-sim
```

In notebooks:

```python
%pip install vse-sim
```

For reproducible notebooks, pin a version after public releases exist:

```python
%pip install "vse-sim==0.1.0"
```
