from Mod_NeonOcean_S4_Debug import Mod
from Mod_NeonOcean_S4_Debug.Tools import Information

def BuildInformation () -> bool:
	if not Information.CanBuildInformation():
		return True

	Information.BuildInformation(Mod.GetCurrentMod().InformationSourceFilePath, Mod.GetCurrentMod().InformationBuildFilePath)

	return True
