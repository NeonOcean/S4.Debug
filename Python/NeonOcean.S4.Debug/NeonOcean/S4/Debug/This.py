from __future__ import annotations

from NeonOcean.S4.Main import Mods

try:
	Mod = Mods.GetMod("NeonOcean.S4.Debug")  # type: Mods.Mod
except Exception as e:
	raise Exception("Cannot find self in mod list.") from e
