"""Legacy compatibility wrapper for :mod:`vse_sim.debug_dump`."""

from vse_sim import debug_dump as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})
__all__ = _impl.__all__
