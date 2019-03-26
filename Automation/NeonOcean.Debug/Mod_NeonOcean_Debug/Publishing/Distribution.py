import os

from Mod_NeonOcean_Debug import Mod, Paths
from Mod_NeonOcean_Debug.Tools import IO, Distribution

def BuildDistribution () -> bool:
	if not Distribution.CanSendToInstaller() or not Distribution.CanBuildInstaller():
		return False

	IO.ClearDirectory(os.path.dirname(Mod.GetCurrentMod().DistributionFilesFilePath))
	IO.ClearDirectory(os.path.dirname(Mod.GetCurrentMod().DistributionInstallerFilePath))

	IO.ZipDirectory(Paths.BuildPath, Mod.GetCurrentMod().DistributionFilesFilePath, compress = True)

	IO.ClearDirectory(os.path.dirname(Mod.GetCurrentMod().DistributionInstallerFilePath))

	Distribution.SendToNOModInstaller(Mod.GetCurrentMod().DistributionFilesFilePath, Paths.PublishingAdditionalInstallerPath)
	Distribution.BuildInstaller(os.path.dirname(Mod.GetCurrentMod().DistributionInstallerFilePath), os.path.splitext(os.path.split(Mod.GetCurrentMod().DistributionInstallerFilePath)[1])[0])

	return True