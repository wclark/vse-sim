import os

import pandas as pd

from vse_sim import (
    CsvBatch,
    RandomModel,
    Score,
    VseResults,
    baseRuns,
    read_results_csv,
    rows_to_dataframe,
    run_simulation,
    summarize_vse,
)

os.environ.setdefault("MPLBACKEND", "Agg")


def test_csv_batch_dataframe_helpers():
    batch = CsvBatch(RandomModel(), [[Score(), baseRuns]], 5, 4, 2, seed="dataframe-test")

    frame = batch.to_dataframe()
    summary = batch.summarize()
    method_summary = batch.summarize(group_by="method")
    ascending_summary = batch.summarize(group_by="method", ascending=True)
    report = batch.report()
    axes = batch.plot_vse(group_by="method")
    horizontal_axes = batch.plot_vse(group_by="method", kind="barh")

    assert list(frame.columns[:3]) == ["eid", "emodel", "ncand"]
    assert batch.dataframe.equals(frame)
    assert batch.to_dataframe(copy=False).equals(frame)
    assert isinstance(batch.results, VseResults)
    assert len(frame) == len(batch.rows)
    assert {"method", "chooser", "mean_vse", "median_vse"} <= set(summary.columns)
    assert method_summary["rows"].sum() == len(batch.rows)
    assert ascending_summary["rows"].sum() == len(batch.rows)
    assert set(report) == {
        "results",
        "summary",
        "method_summary",
        "chooser_summary",
        "method_by_chooser",
    }
    assert axes.get_title() == "mean_vse by method"
    assert horizontal_axes.get_xlabel() == "VSE"


def test_dataframe_module_helpers_accept_rows_and_frames():
    rows = [
        {"eid": "one", "method": "Score", "chooser": "hon", "vse": 1.0},
        {"eid": "two", "method": "Score", "chooser": "hon", "vse": 0.5},
        {"eid": "three", "method": "Mav", "chooser": "hon", "vse": 0.25},
    ]

    frame = rows_to_dataframe(rows)
    same_frame = rows_to_dataframe(frame, copy=False)
    result = VseResults.from_rows(frame)
    summary_from_rows = summarize_vse(rows, group_by="method")
    summary_from_frame = summarize_vse(frame, group_by=("method", "chooser"))
    summary_from_results = summarize_vse(result, group_by="method")

    assert frame["vse"].tolist() == [1.0, 0.5, 0.25]
    assert same_frame is frame
    assert len(result) == 3
    assert result.to_dataframe(copy=False) is result.frame
    assert summary_from_rows["method"].tolist() == ["Score", "Mav"]
    assert summary_from_rows["mean_vse"].round(2).tolist() == [0.75, 0.25]
    assert summary_from_frame["rows"].tolist() == [2, 1]
    assert summary_from_results.equals(summary_from_rows)


def test_vse_results_reports_csv_and_run_helper(tmp_path):
    first = CsvBatch(RandomModel(), [[Score(), baseRuns]], 5, 4, 1, seed="first")
    second = CsvBatch(RandomModel(), [[Score(), baseRuns]], 5, 4, 1, seed="second")

    combined = VseResults.concat([first.results, second.to_dataframe()])
    pivot = combined.pivot(index="method", columns="chooser")
    explicit_pivot = combined.pivot(
        index="method",
        columns="chooser",
        group_by=("method", "chooser"),
    )
    repeated_column_pivot = combined.pivot(index="method", columns="method")
    leaderboard = combined.leaderboard(n=1)
    method_only_report = VseResults.from_rows(
        [{"eid": "one", "method": "Score", "vse": 1.0}]
    ).report(group_by="method")

    assert len(combined) == len(first.rows) + len(second.rows)
    assert "honBallot" in pivot.columns
    assert explicit_pivot.equals(pivot)
    assert "Score0to10" in repeated_column_pivot.columns
    assert len(leaderboard) == 1
    assert set(method_only_report) == {"results", "summary", "method_summary"}

    saved_path = first.saveFile(str(tmp_path / "results"))
    loaded = read_results_csv(saved_path)
    plain_path = combined.to_csv(tmp_path / "plain-results.csv")
    plain_loaded = VseResults.from_csv(plain_path)

    assert loaded.frame["method"].tolist() == first.to_dataframe()["method"].tolist()
    assert len(plain_loaded) == len(combined)

    simulated = run_simulation(
        RandomModel(),
        [[Score(), baseRuns]],
        nvot=5,
        ncand=4,
        niter=1,
        seed="run-helper",
    )

    assert isinstance(simulated, VseResults)
    assert isinstance(simulated.frame, pd.DataFrame)
