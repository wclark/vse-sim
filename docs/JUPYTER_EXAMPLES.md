# Jupyter Notebook Template

This page is a pasteable notebook template for using `vse-sim` in a
DataFrame-centric workflow. The goal is to make the library feel natural in a
modern analysis notebook: run simulations, keep results as DataFrames, build
summary tables, inspect ballots and candidate scores, and produce useful plots
without hand-building `pd.DataFrame(...)` objects.

The original legacy imports, such as `from vse import CsvBatch`, are still
available for older scripts. New notebooks should use `vse_sim`.

## Install In The Active Kernel

Use `%pip` in notebooks so the package installs into the active kernel.

```python
%pip install --upgrade vse-sim
```

For unreleased DataFrame helper APIs on `main`, install from GitHub until the
next PyPI release is cut:

```python
%pip install "vse-sim @ git+https://github.com/wclark/vse-sim.git@main"
```

Restart the kernel after installing or upgrading if the notebook already
imported `vse_sim`.

## Cell 1: Setup, Imports, And Helpers

Paste this cell once near the top of a notebook. It imports the library, defines
a larger default experiment, and creates reusable helpers for reporting,
plotting, and direct method-score inspection.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import random

import matplotlib.pyplot as plt
import pandas as pd
import vse_sim as vse
from vse_sim import (
    Borda,
    IRNR,
    Irv,
    Mav,
    Mj,
    Plurality,
    PolyaModel,
    ProbChooser,
    RandomModel,
    Schulze,
    Score,
    Srv,
    V321,
    baseRuns,
    beHon,
    beStrat,
    beX,
    medianRuns,
    read_results_csv,
    to_dataframe,
    topNMediaFor,
)
from vse_sim.debug_dump import setDebug

try:
    from IPython.display import display
except ImportError:

    def display(*_objects):
        return None


setDebug(False)
plt.style.use("seaborn-v0_8-whitegrid")
pd.set_option("display.max_columns", 80)
pd.set_option("display.width", 140)

DEFAULT_SEED = "vse-notebook-template"
DEFAULT_METHODS = [
    [Score(), baseRuns],
    [Score(1), baseRuns],
    [Srv(2), baseRuns],
    [Plurality(), baseRuns],
    [Borda(), baseRuns],
    [Irv(), baseRuns],
    [Schulze(), baseRuns],
    [V321(), baseRuns],
    [Mav(), medianRuns],
    [Mj(), medianRuns],
    [IRNR(), baseRuns],
]
DEFAULT_CONFIG = {
    "model": PolyaModel(seedVoters=4, alpha=2, mutantFactor=0.25),
    "methods": DEFAULT_METHODS,
    "nvot": 101,
    "ncand": 5,
    "niter": 24,
    "media": topNMediaFor(3),
    "seed": DEFAULT_SEED,
}


def run_experiment(**overrides):
    config = {**DEFAULT_CONFIG, **overrides}
    random.seed(config["seed"])
    return vse.run_simulation(**config)


def report_tables(results):
    frame = results.df
    method_summary = results.summarize(group_by="method")
    chooser_summary = results.summarize(group_by="chooser")
    method_chooser = results.summarize(group_by=("method", "chooser"))
    method_by_chooser = results.pivot(index="method", columns="chooser")
    return {
        "results": frame,
        "method_summary": method_summary,
        "chooser_summary": chooser_summary,
        "method_chooser": method_chooser,
        "method_by_chooser": method_by_chooser,
        "leaderboard": results.leaderboard(n=12, group_by="method"),
    }


def style_summary(frame, columns=("mean_vse", "median_vse", "min_vse", "max_vse")):
    visible_columns = [column for column in columns if column in frame.columns]
    try:
        return frame.style.format(precision=3).background_gradient(
            subset=visible_columns,
            cmap="viridis",
        )
    except AttributeError:
        return frame


def style_heatmap_table(frame):
    try:
        return frame.style.format(precision=3).background_gradient(cmap="viridis")
    except AttributeError:
        return frame


def plot_heatmap(table, ax=None, title="Mean VSE by method and chooser"):
    ax = ax or plt.gca()
    plot_data = table.fillna(0)
    image = ax.imshow(plot_data, aspect="auto", cmap="viridis")
    ax.set_title(title)
    ax.set_xlabel("Chooser")
    ax.set_ylabel("Method")
    ax.set_xticks(range(len(plot_data.columns)), labels=plot_data.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(plot_data.index)), labels=plot_data.index)

    for row_index, method in enumerate(plot_data.index):
        for column_index, chooser in enumerate(plot_data.columns):
            value = plot_data.loc[method, chooser]
            ax.text(column_index, row_index, f"{value:.2f}", ha="center", va="center", fontsize=7)

    plt.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    return ax


def plot_dashboard(results, tables):
    frame = tables["results"]
    method_summary = tables["method_summary"].sort_values("mean_vse", ascending=True)
    chooser_summary = tables["chooser_summary"].sort_values("mean_vse", ascending=True)

    fig, axes = plt.subplots(2, 2, figsize=(18, 12), constrained_layout=True)

    method_summary.plot.barh(
        x="method",
        y="mean_vse",
        xerr="std_vse",
        legend=False,
        ax=axes[0, 0],
        color="#3f7f93",
    )
    axes[0, 0].set_title("Average VSE by method")
    axes[0, 0].set_xlabel("Mean VSE")
    axes[0, 0].set_ylabel("")

    plot_heatmap(tables["method_by_chooser"], ax=axes[0, 1])

    chooser_summary.plot.barh(
        x="chooser",
        y="mean_vse",
        legend=False,
        ax=axes[1, 0],
        color="#855c75",
    )
    axes[1, 0].set_title("Average VSE by strategy chooser")
    axes[1, 0].set_xlabel("Mean VSE")
    axes[1, 0].set_ylabel("")

    frame.boxplot(column="vse", by="method", ax=axes[1, 1], rot=45, grid=False)
    axes[1, 1].set_title("VSE distribution by method")
    axes[1, 1].set_xlabel("")
    axes[1, 1].set_ylabel("VSE")
    fig.suptitle("")
    return fig


def inspect_one_electorate(model=None, methods=None, nvot=21, ncand=5, seed=DEFAULT_SEED):
    random.seed(seed)
    model = model or DEFAULT_CONFIG["model"]
    methods = methods or DEFAULT_METHODS[:5]
    voters = model(nvot, ncand)

    ballot_frames = []
    score_frames = []
    for method, _choosers in methods:
        ballots = method.ballots_dataframe(voters)
        scores = method.results_dataframe(ballots, isHonest=True)
        winner = method.winner(scores["score"].tolist())
        ballot_frames.append(ballots.assign(method=str(method)))
        score_frames.append(scores.assign(winner=winner))

    return {
        "voters": voters,
        "voter_utilities": voters.to_dataframe(wide=True),
        "ballots": pd.concat(ballot_frames, ignore_index=True),
        "scores": pd.concat(score_frames, ignore_index=True),
    }


def save_and_reload(results, filename="vse-results.csv"):
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / filename
        results.to_csv(path)
        return read_results_csv(path)
```

## Cell 2: Run A Larger Simulation And Build A Report

Paste this cell after the setup cell. It runs a larger simulation than the tiny
smoke examples, displays DataFrame reports, creates a dashboard, and inspects
candidate-level scoring from one sampled electorate.

```python
results = run_experiment()
tables = report_tables(results)
detail = inspect_one_electorate()
reloaded_results = save_and_reload(results)

print(f"vse-sim version: {vse.__version__}")
print(f"simulation rows: {len(results):,}")
print(f"raw result shape: {results.df.shape}")
print(f"reloaded result shape: {reloaded_results.df.shape}")

display(results.df.head(12))
display(style_summary(tables["leaderboard"]))
display(style_summary(tables["method_chooser"].head(25)))
display(style_heatmap_table(tables["method_by_chooser"]))

dashboard = plot_dashboard(results, tables)
plt.show()

display(detail["voter_utilities"].head())
display(detail["ballots"].head(15))
display(detail["scores"].pivot(index="method", columns="candidate", values="score"))
```

## How To Experiment From Here

The setup cell is meant to be edited. Common changes:

- Increase `DEFAULT_CONFIG["niter"]` when you want smoother estimates.
- Increase `DEFAULT_CONFIG["nvot"]` for larger electorates.
- Swap `PolyaModel(...)` for `RandomModel()`, `QModel()`, `DimModel(...)`, or
  `KSModel(...)` when exploring different electorate assumptions.
- Add or remove entries in `DEFAULT_METHODS` to focus on a smaller method set.
- Change `media=topNMediaFor(3)` to `truth` or another media helper when
  testing strategic-information assumptions.
- Use `results.df` for row-level filtering and `results.summarize(...)` for
  grouped reports.
- Use `method.ballots_dataframe(voters)` and
  `method.results_dataframe(ballots)` when investigating a single electorate
  in detail.

For long-running studies, start by increasing `niter` gradually and saving
outputs with `results.to_csv(...)`. The result CSV can be reloaded later with
`read_results_csv(...)` and still supports the same `VseResults` summary,
pivot, report, and plotting helpers.
