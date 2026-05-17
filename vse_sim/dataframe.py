"""Pandas-first helpers for VSE simulation results."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from inspect import signature
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


def _voter_metadata(voter) -> dict:
    metadata = {}
    for attribute in ("cluster", "personality"):
        if hasattr(voter, attribute):
            metadata[attribute] = getattr(voter, attribute)
    if hasattr(voter, "dims"):
        for dimension, value in enumerate(voter.dims):
            metadata[f"dimension_{dimension}"] = value
    return metadata


def _call_dataframe_method(method, copy=True, **kwargs) -> pd.DataFrame:
    if "copy" in signature(method).parameters:
        return method(copy=copy, **kwargs)
    frame = method(**kwargs)
    return frame.copy() if copy else frame


def to_dataframe(data, copy=True, **kwargs) -> pd.DataFrame:
    """Convert VSE objects, result rows, or records to a pandas DataFrame."""
    if isinstance(data, VseResults):
        return data.to_dataframe(copy=copy)
    if isinstance(data, pd.DataFrame):
        return data.copy() if copy else data
    dataframe_method = getattr(data, "to_dataframe", None)
    if callable(dataframe_method):
        return _call_dataframe_method(dataframe_method, copy=copy, **kwargs)
    return pd.DataFrame(data, **kwargs)


def rows_to_dataframe(
    rows: Iterable[dict] | pd.DataFrame | "VseResults", copy=True
) -> pd.DataFrame:
    """Convert simulation rows, a DataFrame, or ``VseResults`` to a DataFrame."""
    return to_dataframe(rows, copy=copy)


def voter_to_dataframe(
    voter,
    voter_id=None,
    voter_column="voter",
    candidate_column="candidate",
    value_column="utility",
) -> pd.DataFrame:
    """Return one voter's candidate utilities as a tidy DataFrame."""
    metadata = _voter_metadata(voter)
    rows = []
    for candidate, value in enumerate(voter):
        row = {candidate_column: candidate, value_column: value, **metadata}
        if voter_id is not None:
            row[voter_column] = voter_id
        rows.append(row)
    return pd.DataFrame(rows)


def voters_to_dataframe(
    voters,
    wide=False,
    voter_column="voter",
    candidate_column="candidate",
    value_column="utility",
    candidate_prefix="candidate_",
) -> pd.DataFrame:
    """Return voter utilities as a tidy or wide DataFrame."""
    if wide:
        rows = []
        for voter_id, voter in enumerate(voters):
            row = {
                voter_column: voter_id,
                **{
                    f"{candidate_prefix}{candidate}": value for candidate, value in enumerate(voter)
                },
                **_voter_metadata(voter),
            }
            rows.append(row)
        return pd.DataFrame(rows)

    rows = []
    for voter_id, voter in enumerate(voters):
        rows.extend(
            voter_to_dataframe(
                voter,
                voter_id=voter_id,
                voter_column=voter_column,
                candidate_column=candidate_column,
                value_column=value_column,
            ).to_dict("records")
        )
    return pd.DataFrame(rows)


def ballots_to_dataframe(
    ballots,
    wide=False,
    method=None,
    voter_column="voter",
    candidate_column="candidate",
    value_column="ballot",
    candidate_prefix="candidate_",
) -> pd.DataFrame:
    """Return ballots as a tidy or wide DataFrame."""
    if wide:
        rows = []
        for voter_id, ballot in enumerate(ballots):
            row = {
                voter_column: voter_id,
                **{
                    f"{candidate_prefix}{candidate}": value
                    for candidate, value in enumerate(ballot)
                },
            }
            if method is not None:
                row["method"] = str(method)
            rows.append(row)
        return pd.DataFrame(rows)

    rows = []
    for voter_id, ballot in enumerate(ballots):
        for candidate, value in enumerate(ballot):
            row = {
                voter_column: voter_id,
                candidate_column: candidate,
                value_column: value,
            }
            if method is not None:
                row["method"] = str(method)
            rows.append(row)
    return pd.DataFrame(rows)


def ballots_from_dataframe(
    ballots,
    voter_column="voter",
    candidate_column="candidate",
    value_column="ballot",
    candidate_prefix="candidate_",
):
    """Convert tidy or wide ballot DataFrames back to method-ready ballots."""
    if not isinstance(ballots, pd.DataFrame):
        return ballots if type(ballots) is list else list(ballots)

    if {voter_column, candidate_column, value_column} <= set(ballots.columns):
        return (
            ballots.pivot(index=voter_column, columns=candidate_column, values=value_column)
            .sort_index()
            .sort_index(axis=1)
            .to_numpy()
            .tolist()
        )

    candidate_columns = [
        column for column in ballots.columns if str(column).startswith(candidate_prefix)
    ]
    if candidate_columns:
        candidate_columns = sorted(
            candidate_columns, key=lambda column: int(str(column).split("_")[-1])
        )
        return ballots[candidate_columns].to_numpy().tolist()

    return ballots.to_numpy().tolist()


def scores_to_dataframe(
    scores,
    method=None,
    candidate_column="candidate",
    value_column="score",
) -> pd.DataFrame:
    """Return candidate-level method scores as a DataFrame."""
    rows = [
        {
            candidate_column: candidate,
            value_column: score,
        }
        for candidate, score in enumerate(scores)
    ]
    frame = pd.DataFrame(rows)
    if method is not None:
        frame.insert(0, "method", str(method))
    return frame


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
        return cls(to_dataframe(rows))

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

    @property
    def dataframe(self) -> pd.DataFrame:
        """Return the backing DataFrame for fluent notebook work."""
        return self.frame

    @property
    def df(self) -> pd.DataFrame:
        """Alias for ``dataframe``."""
        return self.frame

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
    "ballots_from_dataframe",
    "ballots_to_dataframe",
    "read_results_csv",
    "rows_to_dataframe",
    "scores_to_dataframe",
    "summarize_vse",
    "to_dataframe",
    "voter_to_dataframe",
    "voters_to_dataframe",
]
