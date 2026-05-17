# Jupyter Notebook Examples

This page is a notebook-oriented cookbook for `vse-sim`. The examples are
written as small cells you can copy into Jupyter. They intentionally use tiny
simulations so they run quickly while exercising the same user-facing surface
area you are likely to use in real analysis:

- installing the package in a notebook kernel
- importing the modern package namespace
- generating electorates with each voter model
- running individual voting methods
- running full VSE batches
- using strategy choosers and media models
- saving CSV output
- checking legacy import compatibility

For real studies, increase `nvot`, `ncand`, and `niter` once the notebook shape
looks right.

## Install In The Active Kernel

Use `%pip` inside notebooks so the package installs into the same Python
environment as the active kernel.

```python
%pip install vse-sim
```

Pin a release for a reproducible notebook:

```python
%pip install "vse-sim==0.1.0"
```

Restart the kernel after installing or upgrading if you already imported
`vse_sim` in the notebook.

## Imports And Debug Output

The package distribution is named `vse-sim`, but Python imports use
`vse_sim`. The original top-level modules remain available for older scripts.

```python
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
import random

from debugDump import setDebug
import vse_sim as vse
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
    skewedMediaFor,
    topNMediaFor,
    truth,
)

setDebug(False)

assert hasattr(vse, "__version__")
vse.__version__
```

## Voters And Electorates

A `Voter` is a tuple of utilities, one utility per candidate. An `Electorate`
is a list-like collection of voters with aggregate social utilities.

```python
voter = Voter([3, 1, 2])
another_voter = Voter([1, 3, 2])
hybrid_voter = voter.hybridWith(another_voter, 1)

assert tuple(voter) == (3, 1, 2)
assert [round(value, 5) for value in hybrid_voter] == [2.82843, 2.82843, 2.82843]

electorate = Electorate(
    [
        Voter([3, 1, 2]),
        Voter([1, 3, 2]),
        Voter([2, 1, 3]),
    ]
)

assert electorate.socUtils == [2.0, 5 / 3, 7 / 3]
electorate.socUtils
```

You can also generate random voters directly. Set `random.seed(...)` before
cells when you want repeatable notebook examples.

```python
random.seed(10)

sample_voter = Voter.rand(4)
mutated_voter = sample_voter.mutantChild(0.2)

assert len(sample_voter) == 4
assert len(mutated_voter) == 4
```

## Voter Models

The voter models are callable electorate factories. This cell touches every
exported model while keeping the generated electorates small.

```python
models = [
    ("random", RandomModel(), 4, 3),
    ("reverse", ReverseModel(), 4, 3),  # nvot must be even.
    ("quality", QModel(), 4, 3),
    ("polya", PolyaModel(), 5, 3),
    ("deterministic", DeterministicModel(3), 4, 3),
    ("dimensional", DimModel(ndims=2), 4, 3),
    ("hierarchical", KSModel(dccut=0.2, wccut=0.2), 4, 3),
]

random.seed(7)
model_summary = []

for label, model, nvot, ncand in models:
    electorate = model(nvot, ncand)
    model_summary.append(
        {
            "label": label,
            "model": str(model),
            "voters": len(electorate),
            "candidates": len(electorate[0]),
            "social_utilities": [round(value, 3) for value in electorate.socUtils],
        }
    )

assert {row["label"] for row in model_summary} == {label for label, *_ in models}
model_summary
```

`CsvBatch` computes VSE as `(winner utility - random utility) / (best utility -
random utility)`. Perfectly symmetric toy electorates, such as a bare
`ReverseModel`, can make the denominator zero. Generate and inspect those
electorates directly, or use a less symmetric model such as `QModel` or
`PolyaModel` for VSE batches.

## Quick VSE Batch

`CsvBatch` is the main simulation harness. It repeatedly generates electorates,
runs the requested voting methods, and stores row dictionaries that can be
written as CSV.

```python
quick_batch = CsvBatch(
    PolyaModel(),
    [[Score(), baseRuns], [Mav(), medianRuns]],
    nvot=5,
    ncand=4,
    niter=3,
    seed="notebook-quickstart",
)

assert len(quick_batch.rows) == 60
quick_batch.rows[0]
```

Rows include the election id, model, method, chooser, realized utility, and VSE
score.

```python
row_keys = sorted(quick_batch.rows[0])
methods_seen = sorted({row["method"] for row in quick_batch.rows})
choosers_seen = sorted({row["chooser"] for row in quick_batch.rows})

assert "vse" in row_keys
assert methods_seen == ["Mav", "Score0to10"]

row_keys, choosers_seen
```

## Reproducible Batches

Pass `seed=...` to make the simulated electorates repeatable. Each row also has
a fresh UUID election id, so compare rows after dropping `eid` when checking
repeatability.

```python
def comparable_rows(rows):
    return [{key: value for key, value in row.items() if key != "eid"} for row in rows]


batch_a = CsvBatch(PolyaModel(), [[Score(), baseRuns]], 5, 4, 2, seed="same-seed")
batch_b = CsvBatch(PolyaModel(), [[Score(), baseRuns]], 5, 4, 2, seed="same-seed")

assert batch_a.rows != batch_b.rows
assert comparable_rows(batch_a.rows) == comparable_rows(batch_b.rows)
```

## Save CSV Output

`saveFile` appends a number to the base name, writes a metadata comment, and
then writes the row dictionaries as CSV.

```python
with TemporaryDirectory() as tmpdir:
    output_base = Path(tmpdir) / "notebook-results"
    quick_batch.saveFile(str(output_base))

    saved_files = sorted(Path(tmpdir).glob("notebook-results*.csv"))
    assert len(saved_files) == 1

    first_lines = saved_files[0].read_text().splitlines()[:3]

first_lines
```

If you use pandas in your notebooks, convert rows directly:

```python
# Optional: install pandas separately if your notebook environment does not
# already provide it.
# %pip install pandas

# import pandas as pd
# frame = pd.DataFrame(quick_batch.rows)
# frame.groupby("method")["vse"].mean().sort_values(ascending=False)
```

Without pandas, the standard library is enough for quick checks:

```python
method_counts = Counter(row["method"] for row in quick_batch.rows)
average_vse = {
    method: sum(row["vse"] for row in quick_batch.rows if row["method"] == method)
    / method_counts[method]
    for method in method_counts
}

method_counts, average_vse
```

## Run Every Bundled Voting Method

`allSystems` is the broad built-in method suite. This cell runs every bundled
method once with a tiny electorate.

```python
method_names = sorted(str(method) for method, _choosers in allSystems)

all_method_batch = CsvBatch(
    RandomModel(),
    allSystems,
    nvot=6,
    ncand=4,
    niter=1,
    seed="all-methods",
)

methods_in_rows = sorted({row["method"] for row in all_method_batch.rows})

assert methods_in_rows == method_names
assert len(all_method_batch.rows) == 144

methods_in_rows
```

Other built-in suites are available when you want the historical baseline
chooser sets or the Mark-requested method set.

```python
suite_sizes = {
    "baseRuns": len(baseRuns),
    "medianRuns": len(medianRuns),
    "allSystems": len(allSystems),
    "markMethods": len(markMethods),
}

assert suite_sizes == {
    "baseRuns": 4,
    "medianRuns": 8,
    "allSystems": 17,
    "markMethods": 13,
}

suite_sizes
```

## Direct Method Experiments

For most work, prefer `CsvBatch`. When you want to inspect ballots and raw
method results, call a method's ballot factory directly.

```python
def honest_ballots(method, voters):
    ballot_factory = method.honBallotFor(voters)
    return [ballot_factory(method.__class__, voter) for voter in voters]


toy_voters = [
    Voter([3, 1, 2]),
    Voter([1, 3, 2]),
    Voter([2, 1, 3]),
]

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
direct_results = []

for method in direct_methods:
    if isinstance(method, V321):
        V321.extraEvents = {}

    ballots = honest_ballots(method, toy_voters)
    results = method.results(ballots, isHonest=True)

    direct_results.append(
        {
            "method": str(method),
            "ballots": ballots,
            "results": [
                round(value, 3) if isinstance(value, (int, float)) else value
                for value in results
            ],
            "winner": method.winner(results),
        }
    )

assert len(direct_results) == len(direct_methods)
direct_results
```

## Strategy Choosers

Choosers select whether each voter casts an honest, strategic, or extra
strategic ballot after the method has prepared those options.

```python
chooser_examples = [
    beHon,
    beStrat,
    beX,
    ProbChooser([(0.5, beHon), (0.5, beStrat)]),
    OssChooser(),
    LazyChooser(),
]

chooser_names = [chooser.getName() for chooser in chooser_examples]

assert chooser_names == [
    "hon",
    "strat",
    "extraStrat",
    "Prob.hon50_strat50.",
    "Oss.hon_strat.",
    "Lazy",
]

chooser_names
```

Use custom chooser lists in the second element of each `[method, choosers]`
entry. Some methods support extra-strategic ballots and some do not, so the
example uses `beX` only with `Mav`.

```python
custom_runs = [
    [Score(), [ProbChooser([(0.5, beHon), (0.5, beStrat)]), OssChooser()]],
    [Mav(), [LazyChooser(), ProbChooser([(0.5, beX), (0.5, beHon)])]],
]

strategy_batch = CsvBatch(
    RandomModel(),
    custom_runs,
    nvot=6,
    ncand=4,
    niter=2,
    media=topNMediaFor(2),
    seed="strategy-media",
)

strategy_choosers = sorted({row["chooser"] for row in strategy_batch.rows})

assert "Prob.hon50_strat50." in strategy_choosers
assert "Prob.extraStrat50_hon50." in strategy_choosers
assert "Lazy" in strategy_choosers

strategy_choosers
```

## Media Helpers

Media functions transform honest polling results before strategic ballots are
calculated.

```python
standings = [10, 8, 6, 2]
tally = defaultdict(int)
random.seed(9)

media_examples = {
    "truth": truth(standings),
    "top_two": topNMediaFor(2)(standings),
    "order": orderOf(standings),
    "bias_scale": round(biaserAround(1)(standings), 3),
    "fuzzy": [round(value, 3) for value in fuzzyMediaFor(0.25)(standings, tally)],
    "biased": [
        round(value, 3)
        for value in biasedMediaFor(1, numerator=1)(standings, defaultdict(int))
    ],
    "skewed": [
        round(value, 3) for value in skewedMediaFor(1)(standings, defaultdict(int))
    ],
    "changed_tally": dict(tally),
}

assert media_examples["truth"] == standings
assert media_examples["top_two"] == [10, 8, 2, 2]
assert media_examples["order"] == [0, 1, 2, 3]

media_examples
```

## Modern And Legacy Imports

New notebooks should use `vse_sim`, but legacy imports are intentionally still
available.

```python
from methods import Score as LegacyScore
from voterModels import PolyaModel as LegacyPolyaModel
from vse import CsvBatch as LegacyCsvBatch
from vse_sim.methods import Score as PackageScore
from vse_sim.simulation import CsvBatch as PackageCsvBatch
from vse_sim.voter_models import PolyaModel as PackagePolyaModel

assert PackageCsvBatch is LegacyCsvBatch
assert PackageScore is LegacyScore
assert PackagePolyaModel is LegacyPolyaModel
```

## One-Cell Notebook Smoke Suite

This final cell is a compact user-facing regression check. Run it after
changing notebook setup code, upgrading `vse-sim`, or trying a GitHub install.

```python
def run_vse_sim_notebook_smoke_suite():
    setDebug(False)

    voters = Electorate(
        [
            Voter([3, 1, 2]),
            Voter([1, 3, 2]),
            Voter([2, 1, 3]),
        ]
    )
    assert voters.socUtils == [2.0, 5 / 3, 7 / 3]

    for _label, model, nvot, ncand in models:
        electorate = model(nvot, ncand)
        assert len(electorate) == nvot
        assert len(electorate[0]) == ncand

    quick = CsvBatch(
        PolyaModel(),
        [[Score(), baseRuns], [Mav(), medianRuns]],
        nvot=5,
        ncand=4,
        niter=3,
        seed="notebook-smoke",
    )
    assert len(quick.rows) == 60
    assert {"Score0to10", "Mav"} == {row["method"] for row in quick.rows}

    all_methods_once = CsvBatch(
        RandomModel(),
        allSystems,
        nvot=6,
        ncand=4,
        niter=1,
        seed="notebook-smoke-all-methods",
    )
    assert sorted({row["method"] for row in all_methods_once.rows}) == sorted(
        str(method) for method, _choosers in allSystems
    )

    custom = CsvBatch(
        RandomModel(),
        [
            [Score(), [ProbChooser([(0.5, beHon), (0.5, beStrat)])]],
            [Mav(), [LazyChooser(), ProbChooser([(0.5, beX), (0.5, beHon)])]],
        ],
        nvot=6,
        ncand=4,
        niter=1,
        media=topNMediaFor(2),
        seed="notebook-smoke-strategy",
    )
    assert any(row["chooser"] == "Lazy" for row in custom.rows)
    assert any(row["chooser"] == "Prob.hon50_strat50." for row in custom.rows)

    V321.extraEvents = {}
    ballots = honest_ballots(V321(), list(voters))
    assert len(V321().results(ballots, isHonest=True)) == 3

    assert PackageCsvBatch is LegacyCsvBatch
    return {
        "version": vse.__version__,
        "quick_rows": len(quick.rows),
        "all_method_rows": len(all_methods_once.rows),
        "custom_rows": len(custom.rows),
    }


run_vse_sim_notebook_smoke_suite()
```
