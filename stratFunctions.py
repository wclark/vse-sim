"""Legacy compatibility wrapper for :mod:`vse_sim.strategies`."""

from vse_sim import strategies as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})
__all__ = _impl.__all__
