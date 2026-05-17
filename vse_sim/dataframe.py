"""Pandas helpers for notebook-friendly VSE simulation results."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


def rows_to_dataframe(rows: Iterable[dict]) -> pd.DataFrame:
    """Convert ``CsvBatch.rows`` or another row iterable to a DataFrame."""
    return pd.DataFrame(rows)


def summarize_vse(
    rows: Iterable[dict] | pd.DataFrame, group_by=("method", "chooser")
) -> pd.DataFrame:
    """Summarize VSE scores by method, chooser, or another grouping."""
    group_columns = [group_by] if isinstance(group_by, str) else list(group_by)
    frame = rows_to_dataframe(rows)
    return (
        frame.groupby(group_columns, as_index=False)
        .agg(
            rows=("vse", "size"),
            elections=("eid", "nunique"),
            mean_vse=("vse", "mean"),
            median_vse=("vse", "median"),
            min_vse=("vse", "min"),
            max_vse=("vse", "max"),
        )
        .sort_values(["mean_vse", *group_columns], ascending=[False, *[True] * len(group_columns)])
        .reset_index(drop=True)
    )


__all__ = ["rows_to_dataframe", "summarize_vse"]
