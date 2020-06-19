import os
import shutil
import sys
import typing
from distutils import dir_util

from Mod_NeonOcean_S4_Debug import Mod, Paths
from Mod_NeonOcean_S4_Debug.Building import Information, Merging, Misc, Package, Python, STBL
from Mod_NeonOcean_S4_Debug.Publishing import Distribution
from Mod_NeonOcean_S4_Debug.Tools import Exceptions

def BuildMod (modeName: str) -> bool:
	if not modeName in _modBuildModes:
		modeName = _modBuildDefaultMode

	modePhases = _modBuildModes.get(modeName)  # type: typing.List[typing.Callable]

	print("Building mod '" + Mod.GetCurrentMod().Namespace + "' in mode '" + modeName + "'.")

	for phase in modePhases:  # type: typing.Callable
		try:
			if not phase():
				print("Forced to skip all or part of phase '" + phase.__name__ + "'.\n" + \
					  "Phase: '" + phase.__name__ + "' Mod: '" + Mod.GetCurrentMod().Namespace + "' Build mode: '" + modeName + "'", file = sys.stderr)
		except Exception as e:
			print("Failed to complete mod build phase.\n" + \
				  "Phase: '" + phase.__name__ + "' Mod: '" + Mod.GetCurrentMod().Namespace + "' Build mode: '" + modeName + "' \n" + \
				  Exceptions.FormatException(e), file = sys.stderr)

			return False

	return True

def UpdateGameFiles () -> bool:
	"""
	Send currently built mod files to the Sims 4 mod folder.
	:return:
	"""

	try:
		if os.path.exists(Mod.GetCurrentMod().UninstallFilesFilePath):
			with open(Mod.GetCurrentMod().UninstallFilesFilePath) as uninstallFilesFile:
				uninstallFiles = uninstallFilesFile.read().splitlines()  # type: typing.List[str]

			for uninstallFile in uninstallFiles:  # type: str
				uninstallFilePath = os.path.join(Paths.S4ModsPath, uninstallFile)  # type: str

				if os.path.exists(uninstallFilePath):
					os.remove(uninstallFilePath)
	except Exception as e:
		print("Failed to uninstall the previous mod version.\n" + \
			  "Mod: '" + Mod.GetCurrentMod().Namespace + "'\n" + \
			  Exceptions.FormatException(e), file = sys.stderr)

	try:
		dir_util.copy_tree(Paths.BuildPath, Paths.S4ModsPath)
	except Exception as e:
		print("Failed to send mod to the Sims 4 mod folder.\n" + \
			  "Mod: '" + Mod.GetCurrentMod().Namespace + "'\n" + \
			  Exceptions.FormatException(e), file = sys.stderr)

		return False

	return True

def UpdateGamePython () -> bool:
	"""
	Send currently built python files to the Sims 4 mod folder.
	:return:
	"""

	try:
		currentPythonFilePath = os.path.join(Paths.S4ModsPath, Mod.GetCurrentMod().PythonMergeRelativeRoot, Mod.GetCurrentMod().PythonBuildArchiveFileName)  # type: str

		if os.path.exists(currentPythonFilePath):
			os.remove(currentPythonFilePath)

		shutil.copy(Mod.GetCurrentMod().PythonBuildArchiveFilePath, os.path.join(Paths.S4ModsPath, Mod.GetCurrentMod().PythonMergeRelativeRoot))
	except Exception as e:
		print("Failed to send python to the Sims 4 mod folder.\n" + \
			  "Mod: '" + Mod.GetCurrentMod().Namespace + "'\n" + \
			  Exceptions.FormatException(e), file = sys.stderr)

		return False

	return True

def BuildPublishing () -> bool:
	print("Building mod publishing '" + Mod.GetCurrentMod().Namespace + "'.")

	for phase in _publishingPhases:  # type: typing.Callable
		try:
			if not phase():
				print("Forced to skip all or part of phase 'Publishing'.\n" + \
					  "Phase: 'Publishing' Mod: '" + Mod.GetCurrentMod().Namespace + "'", file = sys.stderr)
		except Exception as e:
			print("Failed to complete mod build phase.\n" + \
				  "Phase: 'Publishing' Mod: '" + Mod.GetCurrentMod().Namespace + "'" + \
				  Exceptions.FormatException(e), file = sys.stderr)

			return False

	return True

_modBuildModes = {
	"Python": [
		Python.BuildPython,
		Merging.Merge,
		UpdateGamePython
	],

	"Normal": [
		Misc.BuildMisc,
		Python.BuildPython,
		STBL.BuildSTBLChanges,
		Package.BuildPackageChanges,
		Information.BuildInformation,
		Merging.Merge,
		UpdateGameFiles
	],

	"Rebuild": [
		Misc.BuildMisc,
		Python.BuildPython,
		STBL.BuildSTBLEverything,
		Package.BuildPackageEverything,
		Information.BuildInformation,
		Merging.Merge,
		UpdateGameFiles
	]

}  # type: typing.Dict[str, typing.List[typing.Callable]]

_publishingPhases = [
	Distribution.BuildDistribution
]

_modBuildDefaultMode = "Normal"  # type: str
