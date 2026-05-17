import importlib

import methods
import voterModels
import vse


def test_modern_package_exports_match_legacy_modules():
    import vse_sim

    assert vse_sim.__version__ == "0.1.0"
    assert vse_sim.CsvBatch is vse.CsvBatch
    assert vse_sim.Score is methods.Score
    assert vse_sim.Mav is methods.Mav
    assert vse_sim.PolyaModel is voterModels.PolyaModel
    assert vse_sim.baseRuns is vse.baseRuns
    assert vse_sim.rows_to_dataframe.__module__ == "vse_sim.dataframe"
    assert vse_sim.CsvBatch.__module__ == "vse_sim.simulation"
    assert vse_sim.Score().__class__.__module__ == "vse_sim.methods"
    assert vse_sim.PolyaModel.__module__ == "vse_sim.voter_models"
    assert "CsvBatch" in vse_sim.__all__


def test_modern_submodule_imports_match_legacy_modules():
    from compat import mean as legacy_mean
    from dataClasses import Method as LegacyMethod
    from stratFunctions import truth as legacy_truth
    from vse_sim.compat import mean
    from vse_sim.data_classes import Method
    from vse_sim.dataframe import rows_to_dataframe
    from vse_sim.methods import Score
    from vse_sim.simulation import CsvBatch
    from vse_sim.strategies import truth
    from vse_sim.voter_models import PolyaModel

    assert CsvBatch is vse.CsvBatch
    assert Method is LegacyMethod
    assert mean is legacy_mean
    assert rows_to_dataframe is importlib.import_module("vse_sim").rows_to_dataframe
    assert PolyaModel is voterModels.PolyaModel
    assert Score is methods.Score
    assert truth is legacy_truth


def test_legacy_module_imports_stay_available():
    legacy_names = [
        "compat",
        "dataClasses",
        "debugDump",
        "methods",
        "mydecorators",
        "sodaTest",
        "stratFunctions",
        "voterModels",
        "vse",
    ]

    for module_name in legacy_names:
        assert importlib.import_module(module_name).__name__ == module_name
