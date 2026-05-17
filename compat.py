"""Legacy compatibility wrapper for :mod:`vse_sim.compat`."""

from vse_sim import compat as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})
__all__ = _impl.__all__
