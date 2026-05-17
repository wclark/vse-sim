from vse_sim import CsvBatch, RandomModel, Score, baseRuns, rows_to_dataframe, summarize_vse


def test_csv_batch_dataframe_helpers():
    batch = CsvBatch(RandomModel(), [[Score(), baseRuns]], 5, 4, 2, seed="dataframe-test")

    frame = batch.to_dataframe()
    summary = batch.summarize()
    method_summary = batch.summarize(group_by="method")

    assert list(frame.columns[:3]) == ["eid", "emodel", "ncand"]
    assert len(frame) == len(batch.rows)
    assert {"method", "chooser", "mean_vse", "median_vse"} <= set(summary.columns)
    assert method_summary["rows"].sum() == len(batch.rows)


def test_dataframe_module_helpers_accept_rows_and_frames():
    rows = [
        {"eid": "one", "method": "Score", "chooser": "hon", "vse": 1.0},
        {"eid": "two", "method": "Score", "chooser": "hon", "vse": 0.5},
        {"eid": "three", "method": "Mav", "chooser": "hon", "vse": 0.25},
    ]

    frame = rows_to_dataframe(rows)
    summary_from_rows = summarize_vse(rows, group_by="method")
    summary_from_frame = summarize_vse(frame, group_by=("method", "chooser"))

    assert frame["vse"].tolist() == [1.0, 0.5, 0.25]
    assert summary_from_rows["method"].tolist() == ["Score", "Mav"]
    assert summary_from_rows["mean_vse"].round(2).tolist() == [0.75, 0.25]
    assert summary_from_frame["rows"].tolist() == [2, 1]
