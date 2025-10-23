from __future__ import annotations
import contextlib
import glob
import os
import tempfile
import random
from typing import Iterable, Tuple, Any, Optional

import numpy as np
import pandas as pd

from vse import CsvBatch

@contextlib.contextmanager
def _temp_cwd():
    """Run code in a temporary working directory and restore the CWD afterwards."""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            yield d
        finally:
            os.chdir(cwd)

def _seed_all(seed: Optional[int]):
    """Seed Python and NumPy random number generators for reproducibility."""
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)

def run_batch_to_df(
    voter_model: Any,
    method_runs: Iterable[Tuple[Any, Any]],
    *,
    nvot: int,
    ncand: int,
    niter: int,
    seed: Optional[int] = None,
    csv_glob: str = "*.csv",
) -> pd.DataFrame:
    """
    Execute a batch of simulations and return the results as a pandas DataFrame.

    The upstream CsvBatch API writes out results to a CSV on disk via ``saveFile()``.
    This wrapper contains that side-effect in a temporary directory and reads the
    generated CSV into a DataFrame.
    """
    _seed_all(seed)
    csvs = CsvBatch(voter_model, list(method_runs), nvot=nvot, ncand=ncand, niter=niter)
    with _temp_cwd() as tmp:
        csvs.saveFile()
        files = glob.glob(os.path.join(tmp, csv_glob))
        if not files:
            raise RuntimeError(
                "No CSV produced by CsvBatch.saveFile(). If upstream naming changes, adjust ``csv_glob``."
            )
        if len(files) > 1:
            files.sort(key=os.path.getmtime, reverse=True)
        df = pd.read_csv(files[0])
    return df

def sweep(
    voter_models: Iterable[Any],
    method_runs: Iterable[Tuple[Any, Any]],
    *,
    nvot_list: Iterable[int],
    ncand_list: Iterable[int],
    niter: int,
    seed: Optional[int] = None,
) -> pd.DataFrame:
    """
    Run a grid of simulations over lists of voter and candidate counts and
    combine the results into a single DataFrame.

    Each combination of voter model, number of voters and number of candidates
    yields one batch of simulations via ``run_batch_to_df()``. The results are
    annotated with ``nvot``, ``ncand`` and ``voter_model`` columns for ease of grouping and plotting.
    """
    frames = []
    for vm in voter_models:
        for nv in nvot_list:
            for nc in ncand_list:
                df = run_batch_to_df(
                    vm, method_runs, nvot=nv, ncand=nc, niter=niter, seed=seed
                )
                df["nvot"] = nv
                df["ncand"] = nc
                df["voter_model"] = getattr(vm, "__class__", type(vm)).__name__
                frames.append(df)
    return pd.concat(frames, ignore_index=True)

def summarize_vse(
    df: pd.DataFrame,
    method_col: str = "Method",
    vse_col: str = "VSE",
) -> pd.DataFrame:
    """
    Summarize VSE results by computing mean and standard error for each method.
    """
    if method_col not in df.columns or vse_col not in df.columns:
        raise ValueError(
            f"Expected columns `{method_col}` and `{vse_col}` not found. "
            f"Available columns: {list(df.columns)}"
        )
    out = (
        df.groupby(method_col, as_index=False)[vse_col]
        .agg(mean="mean", std="std", n="count")
    )
    out["se"] = out["std"] / np.sqrt(out["n"].clip(lower=1))
    return out.sort_values("mean", ascending=False)
