from NeonOcean.Main import Mods

try:
	Mod = Mods.Debug  # type: Mods.Mod
except Exception as e:
	raise Exception("Cannot find self in mod list.") from e
