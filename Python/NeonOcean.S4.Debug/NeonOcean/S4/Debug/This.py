from __future__ import annotations

from NeonOcean.S4.Main import Mods
from NeonOcean.S4.Debug import ThisNamespace

try:
	Mod = Mods.GetMod(ThisNamespace.Namespace)  # type: Mods.Mod
except Exception as e:
	raise Exception("Cannot find self in mod list.") from e
