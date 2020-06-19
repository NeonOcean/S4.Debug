import os

from Mod_NeonOcean_S4_Debug import Mod, Paths
from Mod_NeonOcean_S4_Debug.Tools import IO, Misc

def BuildMisc () -> bool:
	if not Misc.CanBuildMarkdown():
		return False

	IO.ClearDirectory(Paths.MiscPath)

	changesFilePath = Mod.GetCurrentMod().ChangesFilePath  # type: str

	if os.path.exists(changesFilePath):
		changesBuildFileName = os.path.splitext(os.path.split(changesFilePath)[1])[0] + ".html"  # type: str
		changesBuildFilePath = os.path.join(Paths.MiscPath, Mod.GetCurrentMod().Namespace, changesBuildFileName)  # type: str

		Misc.BuildMarkdown(changesBuildFilePath, changesFilePath)

	plansFilePath = Mod.GetCurrentMod().PlansFilePath  # type: str

	if os.path.exists(plansFilePath):
		plansBuildFileName = os.path.splitext(os.path.split(plansFilePath)[1])[0] + ".html"  # type: str
		plansBuildFilePath = os.path.join(Paths.MiscPath, Mod.GetCurrentMod().Namespace, plansBuildFileName)  # type: str

		Misc.BuildMarkdown(plansBuildFilePath, plansFilePath)

	return True
