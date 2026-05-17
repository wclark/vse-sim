# Jupyter Notebook Examples

This page is a copy-paste cookbook for using `vse-sim` in a modern notebook.
The examples use the package namespace, `vse_sim`, and work with pandas
DataFrames throughout.

The original legacy imports, such as `from vse import CsvBatch`, are still
available for older scripts. New notebooks should use `vse_sim`.

## Install In The Active Kernel

Use `%pip` in notebooks so the package installs into the same Python
environment as the active kernel.

```python
%pip install vse-sim
```

Pin a release when you need reproducible notebooks:

```python
%pip install "vse-sim==0.1.1"
```

Restart the kernel after installing or upgrading if you already imported
`vse_sim`.

## Imports

```python
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
import random

import vse_sim as vse
import pandas as pd
from vse_sim.debug_dump import setDebug
from vse_sim import (
    IRNR,
    Borda,
    BulletyApprovalWith,
    CsvBatch,
    DeterministicModel,
    DimModel,
    Electorate,
    Irv,
    IrvPrime,
    KSModel,
    LazyChooser,
    Mav,
    Mj,
    OssChooser,
    Plurality,
    PolyaModel,
    ProbChooser,
    QModel,
    RandomModel,
    ReverseModel,
    Rp,
    Schulze,
    Score,
    Srv,
    V321,
    Voter,
    VseResults,
    allSystems,
    baseRuns,
    beHon,
    beStrat,
    beX,
    biasedMediaFor,
    biaserAround,
    fuzzyMediaFor,
    markMethods,
    medianRuns,
    orderOf,
    read_results_csv,
    rows_to_dataframe,
    skewedMediaFor,
    summarize_vse,
    topNMediaFor,
    truth,
)

setDebug(False)
vse.__version__
```

## Voters And Electorates

A `Voter` is a tuple of utilities, one utility per candidate. An `Electorate`
is a list-like collection of voters with aggregate social utilities.

```python
toy_voters = Electorate(
    [
        Voter([3, 1, 2]),
        Voter([1, 3, 2]),
        Voter([2, 1, 3]),
    ]
)

pd.DataFrame(
    toy_voters,
    columns=["candidate_0", "candidate_1", "candidate_2"],
).assign(voter=range(len(toy_voters))).set_index("voter")
```

```python
pd.DataFrame(
    {
        "candidate": range(len(toy_voters.socUtils)),
        "social_utility": toy_voters.socUtils,
    }
).sort_values("social_utility", ascending=False)
```

Random voters are useful for quick exploratory cells.

```python
random.seed(10)

sample_voter = Voter.rand(4)
mutated_voter = sample_voter.mutantChild(0.2)

pd.DataFrame(
    {
        "candidate": range(4),
        "sample_voter": sample_voter,
        "mutated_voter": mutated_voter,
    }
)
```

## Voter Models

The voter models are callable electorate factories. This example inspects every
exported voter model directly.

```python
model_specs = [
    ("random", RandomModel(), 4, 3),
    ("reverse", ReverseModel(), 4, 3),
    ("quality", QModel(), 4, 3),
    ("polya", PolyaModel(), 5, 3),
    ("deterministic", DeterministicModel(3), 4, 3),
    ("dimensional", DimModel(ndims=2), 4, 3),
    ("hierarchical", KSModel(dccut=0.2, wccut=0.2), 4, 3),
]

random.seed(7)
model_rows = []

for label, model, nvot, ncand in model_specs:
    electorate = model(nvot, ncand)
    for candidate, utility in enumerate(electorate.socUtils):
        model_rows.append(
            {
                "label": label,
                "model": str(model),
                "voters": len(electorate),
                "candidates": ncand,
                "candidate": candidate,
                "social_utility": utility,
            }
        )

model_frame = pd.DataFrame(model_rows)
model_frame.pivot_table(
    index=["label", "model"],
    columns="candidate",
    values="social_utility",
)
```

VSE uses the spread between the best candidate and a random winner baseline.
Perfectly symmetric tiny electorates can make that denominator zero, so use
`ReverseModel` and small deterministic electorates for direct model inspection,
or add quality/noise before running VSE batches.

## Quick VSE Batch

`vse.run_simulation(...)` is the DataFrame-first entry point. It repeatedly
generates electorates, runs the requested voting methods, and returns a
`VseResults` object.

```python
quick_results = vse.run_simulation(
    PolyaModel(),
    [[Score(), baseRuns], [Mav(), medianRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="notebook-quickstart",
)

quick_results.frame.head()
```

`VseResults.summarize()` returns a DataFrame grouped by method and chooser.

```python
quick_summary = quick_results.summarize()
quick_summary.sort_values("mean_vse", ascending=False).head(10)
```

You can group at a different level when you want a compact comparison.

```python
quick_results.summarize(group_by="method")
```

Use `leaderboard`, `pivot`, and `report` for common notebook report tables.

```python
quick_results.leaderboard(n=5, group_by="method")
```

```python
quick_results.pivot(index="method", columns="chooser")
```

```python
quick_report = quick_results.report()
quick_report.keys()
```

The same summary helper also works with plain row dictionaries or existing
DataFrames.

```python
summarize_vse(quick_results.frame, group_by="method")
```

```python
rows_to_dataframe(quick_results).head()
```

Plots are built from the same summary tables and return matplotlib axes.

```python
quick_results.plot_vse(group_by="method", kind="barh", title="Quick VSE comparison")
```

## Save And Reopen CSV Output

`VseResults.to_csv(...)` writes the result DataFrame, and
`read_results_csv(...)` loads it back into a `VseResults` object.

```python
with TemporaryDirectory() as tmpdir:
    saved_path = Path(tmpdir) / "notebook-results.csv"
    quick_results.to_csv(saved_path)

    saved_results = read_results_csv(saved_path)

saved_results.frame.head()
```

`CsvBatch` is still available when you want the legacy object or its metadata
CSV writer.

```python
quick_batch = CsvBatch(
    PolyaModel(),
    [[Score(), baseRuns], [Mav(), medianRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="notebook-quickstart",
)

with TemporaryDirectory() as tmpdir:
    legacy_metadata_csv = quick_batch.saveFile(str(Path(tmpdir) / "notebook-results"))
```

## Run Every Bundled Voting Method

`allSystems` is the broad built-in method suite. This cell runs every bundled
method once with a tiny electorate.

```python
all_method_results = vse.run_simulation(
    RandomModel(),
    allSystems,
    nvot=6,
    ncand=4,
    niter=1,
    seed="all-methods",
)

all_method_summary = all_method_results.summarize(group_by="method")

all_method_summary.sort_values("mean_vse", ascending=False)
```

The built-in suites are ordinary lists, so you can inspect and reuse them.

```python
pd.DataFrame(
    {
        "suite": ["baseRuns", "medianRuns", "allSystems", "markMethods"],
        "entries": [len(baseRuns), len(medianRuns), len(allSystems), len(markMethods)],
    }
)
```

```python
pd.DataFrame(
    {
        "method": [str(method) for method, _choosers in markMethods],
        "chooser_count": [len(choosers) for _method, choosers in markMethods],
    }
)
```

## Direct Method Experiments

For most notebook work, use `vse.run_simulation(...)`. When you want to inspect
ballots and raw method scores, call a method's honest ballot factory directly.

```python
def honest_ballots(method, voters):
    ballot_factory = method.honBallotFor(voters)
    return [ballot_factory(method.__class__, voter) for voter in voters]


direct_methods = [
    Score(),
    Score(1),
    BulletyApprovalWith(0.6),
    Srv(2),
    Plurality(),
    Borda(),
    Irv(),
    IrvPrime(),
    Schulze(),
    Rp(),
    V321(),
    Mav(),
    Mj(),
    IRNR(),
]

random.seed(2)
direct_rows = []

for method in direct_methods:
    if isinstance(method, V321):
        V321.extraEvents = {}

    ballots = honest_ballots(method, toy_voters)
    results = method.results(ballots, isHonest=True)

    direct_rows.append(
        {
            "method": str(method),
            "winner": method.winner(results),
            "ballots": ballots,
            "results": results,
        }
    )

direct_frame = pd.DataFrame(direct_rows)
direct_frame[["method", "winner", "results"]]
```

Explode list-valued results into a candidate-by-method table.

```python
direct_scores = (
    direct_frame[["method", "results"]]
    .explode("results")
    .assign(candidate=lambda frame: frame.groupby("method").cumcount())
    .rename(columns={"results": "score"})
)

direct_scores.pivot(index="method", columns="candidate", values="score")
```

## Strategy Choosers

Choosers select whether each voter casts an honest, strategic, or
extra-strategic ballot after the method has prepared those options.

```python
chooser_examples = [
    beHon,
    beStrat,
    beX,
    ProbChooser([(0.5, beHon), (0.5, beStrat)]),
    OssChooser(),
    LazyChooser(),
]

pd.DataFrame(
    {
        "chooser": [chooser.getName() for chooser in chooser_examples],
        "class": [chooser.__class__.__name__ for chooser in chooser_examples],
    }
)
```

Use custom chooser lists in the second element of each `[method, choosers]`
entry. Some methods support extra-strategic ballots and some do not; this
example uses `beX` with `Mav`, where it is supported.

```python
custom_runs = [
    [Score(), [ProbChooser([(0.5, beHon), (0.5, beStrat)]), OssChooser()]],
    [Mav(), [LazyChooser(), ProbChooser([(0.5, beX), (0.5, beHon)])]],
]

strategy_results = vse.run_simulation(
    RandomModel(),
    custom_runs,
    nvot=6,
    ncand=4,
    niter=2,
    media=topNMediaFor(2),
    seed="strategy-media",
)

strategy_results.frame[["method", "chooser", "vse"]].head(12)
```

```python
strategy_results.summarize().sort_values(["method", "mean_vse"], ascending=[True, False])
```

Tally columns are present only when a chooser records tally information, so
reshape them after filtering for rows that have a tally.

```python
tally_columns = [column for column in strategy_results.frame.columns if column.startswith("tally")]

strategy_results.frame.dropna(subset=["tallyName0"])[
    ["method", "chooser", *tally_columns]
].head()
```

## Media Helpers

Media functions transform honest polling results before strategic ballots are
calculated.

```python
standings = [10, 8, 6, 2]
tally = defaultdict(int)
random.seed(9)

media_frame = pd.DataFrame(
    {
        "candidate": range(len(standings)),
        "truth": truth(standings),
        "top_two": topNMediaFor(2)(standings),
        "fuzzy": fuzzyMediaFor(0.25)(standings, tally),
        "biased": biasedMediaFor(1, numerator=1)(standings, defaultdict(int)),
        "skewed": skewedMediaFor(1)(standings, defaultdict(int)),
    }
)

media_frame
```

```python
pd.DataFrame(
    {
        "candidate_order": [orderOf(standings)],
        "bias_scale": [biaserAround(1)(standings)],
        "fuzzy_changed_tally": [dict(tally)],
    }
)
```

Media helpers can be passed directly to `vse.run_simulation(...)`.

```python
media_batches = []

for label, media in [
    ("truth", truth),
    ("top_two", topNMediaFor(2)),
    ("fuzzy", fuzzyMediaFor(0.25)),
    ("biased", biasedMediaFor(1, numerator=1)),
    ("skewed", skewedMediaFor(1)),
]:
    results = vse.run_simulation(
        RandomModel(),
        [[Score(), baseRuns]],
        nvot=6,
        ncand=4,
        niter=2,
        media=media,
        seed=f"media-{label}",
    )
    media_batches.append(results.summarize(group_by="method").assign(media=label))

pd.concat(media_batches, ignore_index=True)[
    ["media", "method", "rows", "mean_vse", "min_vse", "max_vse"]
]
```

## Model And Method Batch Matrix

This pattern is useful when you want to exercise a range of working model and
method combinations without turning the notebook into a long-running study.

```python
batch_matrix = [
    ("random", RandomModel(), [[Score(), baseRuns], [Plurality(), baseRuns]]),
    ("quality", QModel(), [[Score(), baseRuns], [Borda(), baseRuns]]),
    ("polya", PolyaModel(), [[Score(), baseRuns], [Mav(), medianRuns]]),
    ("dimensional", DimModel(ndims=2), [[Score(), baseRuns], [Irv(), baseRuns]]),
    (
        "hierarchical",
        KSModel(dccut=0.2, wccut=0.2),
        [[Score(), baseRuns], [V321(), baseRuns]],
    ),
]

matrix_summaries = []

for label, model, methods in batch_matrix:
    results = vse.run_simulation(
        model,
        methods,
        nvot=6,
        ncand=4,
        niter=2,
        seed=f"matrix-{label}",
    )
    matrix_summaries.append(results.summarize(group_by="method").assign(model=label))

batch_matrix_summary = pd.concat(matrix_summaries, ignore_index=True)
batch_matrix_summary[["model", "method", "rows", "mean_vse"]].sort_values(
    ["model", "mean_vse"],
    ascending=[True, False],
)
```

## Legacy Compatibility Check

These imports remain supported for older scripts, but new notebook code should
prefer `vse_sim`.

```python
from methods import Score as LegacyScore
from voterModels import PolyaModel as LegacyPolyaModel
from vse import CsvBatch as LegacyCsvBatch

pd.DataFrame(
    {
        "object": ["CsvBatch", "Score", "PolyaModel"],
        "modern_module": [
            CsvBatch.__module__,
            Score().__class__.__module__,
            PolyaModel.__module__,
        ],
        "legacy_same_object": [
            LegacyCsvBatch is CsvBatch,
            LegacyScore is Score,
            LegacyPolyaModel is PolyaModel,
        ],
    }
)
```
