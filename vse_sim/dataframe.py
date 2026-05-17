"""Pandas-first helpers for VSE simulation results."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DEFAULT_GROUP_BY = ("method", "chooser")


def _group_columns(group_by) -> list[str]:
    return [group_by] if isinstance(group_by, str) else list(group_by)


def _unique_columns(*groups) -> tuple[str, ...]:
    columns = []
    for group in groups:
        for column in _group_columns(group):
            if column not in columns:
                columns.append(column)
    return tuple(columns)


def rows_to_dataframe(
    rows: Iterable[dict] | pd.DataFrame | "VseResults", copy=True
) -> pd.DataFrame:
    """Convert simulation rows, a DataFrame, or ``VseResults`` to a DataFrame."""
    if isinstance(rows, VseResults):
        return rows.to_dataframe(copy=copy)
    if isinstance(rows, pd.DataFrame):
        return rows.copy() if copy else rows
    return pd.DataFrame(rows)


def summarize_vse(
    rows: Iterable[dict] | pd.DataFrame | "VseResults",
    group_by=DEFAULT_GROUP_BY,
    sort_by="mean_vse",
    ascending=False,
) -> pd.DataFrame:
    """Summarize VSE scores by method, chooser, or another grouping."""
    return VseResults(rows_to_dataframe(rows, copy=False)).summarize(
        group_by=group_by,
        sort_by=sort_by,
        ascending=ascending,
    )


def read_results_csv(path) -> "VseResults":
    """Load a VSE result CSV written by ``CsvBatch.saveFile``."""
    return VseResults.from_csv(path)


@dataclass(frozen=True)
class VseResults:
    """Pandas-backed simulation result set.

    ``frame`` is the canonical tabular representation. Convenience methods
    return DataFrames or matplotlib axes so notebook workflows can keep chaining.
    """

    frame: pd.DataFrame

    @classmethod
    def from_rows(cls, rows: Iterable[dict] | pd.DataFrame | "VseResults") -> "VseResults":
        return cls(rows_to_dataframe(rows))

    @classmethod
    def from_csv(cls, path) -> "VseResults":
        return cls(pd.read_csv(Path(path), comment="#"))

    @classmethod
    def concat(
        cls, results: Iterable["VseResults" | pd.DataFrame | Iterable[dict]]
    ) -> "VseResults":
        frames = [rows_to_dataframe(result) for result in results]
        return cls(pd.concat(frames, ignore_index=True))

    def __len__(self) -> int:
        return len(self.frame)

    def to_dataframe(self, copy=True) -> pd.DataFrame:
        return self.frame.copy() if copy else self.frame

    def to_csv(self, path, index=False, **kwargs):
        """Write the result DataFrame to CSV and return the path."""
        self.frame.to_csv(path, index=index, **kwargs)
        return path

    def summarize(
        self,
        group_by=DEFAULT_GROUP_BY,
        sort_by="mean_vse",
        ascending=False,
    ) -> pd.DataFrame:
        """Return aggregate VSE metrics grouped by one or more columns."""
        group_columns = _group_columns(group_by)
        summary = (
            self.frame.groupby(group_columns, as_index=False)
            .agg(
                rows=("vse", "size"),
                elections=("eid", "nunique"),
                mean_vse=("vse", "mean"),
                median_vse=("vse", "median"),
                min_vse=("vse", "min"),
                max_vse=("vse", "max"),
                std_vse=("vse", "std"),
            )
            .fillna({"std_vse": 0})
        )
        return summary.sort_values(
            [sort_by, *group_columns],
            ascending=[ascending, *[True] * len(group_columns)],
        ).reset_index(drop=True)

    def leaderboard(self, n=10, group_by="method", by="mean_vse") -> pd.DataFrame:
        """Return the top groups by a summary metric."""
        return self.summarize(group_by=group_by, sort_by=by).head(n)

    def pivot(
        self,
        index="method",
        columns="chooser",
        values="mean_vse",
        group_by=None,
    ) -> pd.DataFrame:
        """Return a comparison matrix from summarized result data."""
        index_columns = _group_columns(index)
        column_columns = _group_columns(columns)
        if group_by is None:
            group_by = _unique_columns(index, columns)
        summary = self.summarize(group_by=group_by).copy()
        pivot_columns = []
        for column in column_columns:
            if column in index_columns:
                column_alias = f"__vse_sim_pivot_{column}"
                summary[column_alias] = summary[column]
                pivot_columns.append(column_alias)
            else:
                pivot_columns.append(column)
        pivoted = summary.pivot(
            index=index,
            columns=pivot_columns[0] if isinstance(columns, str) else pivot_columns,
            values=values,
        )
        pivoted.columns = pivoted.columns.set_names(column_columns)
        return pivoted

    def report(self, group_by=DEFAULT_GROUP_BY) -> dict[str, pd.DataFrame]:
        """Build common report tables from a result set."""
        tables = {
            "results": self.to_dataframe(),
            "summary": self.summarize(group_by=group_by),
            "method_summary": self.summarize(group_by="method"),
        }
        if "chooser" in self.frame:
            tables["chooser_summary"] = self.summarize(group_by="chooser")
            tables["method_by_chooser"] = self.pivot()
        return tables

    def plot_vse(
        self,
        group_by="method",
        value="mean_vse",
        kind="bar",
        ax=None,
        title=None,
        **kwargs,
    ):
        """Plot summarized VSE scores and return the matplotlib axes."""
        summary = self.summarize(group_by=group_by)
        group_columns = _group_columns(group_by)
        labels = summary[group_columns].astype(str).agg(" | ".join, axis=1)
        plot_frame = summary.assign(label=labels).set_index("label")
        axes = plot_frame[value].plot(kind=kind, ax=ax, **kwargs)
        axes.set_xlabel("VSE" if kind == "barh" else "")
        axes.set_ylabel("" if kind == "barh" else "VSE")
        axes.set_title(title or f"{value} by {' / '.join(group_columns)}")
        return axes


__all__ = [
    "DEFAULT_GROUP_BY",
    "VseResults",
    "read_results_csv",
    "rows_to_dataframe",
    "summarize_vse",
]
