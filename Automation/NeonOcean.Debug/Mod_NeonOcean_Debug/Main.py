import os
import subprocess
import sys
import time
import typing
from distutils import dir_util

from Mod_NeonOcean_Debug import Mod, Paths
from Mod_NeonOcean_Debug.Building import Merging, Package, Python, STBL
from Mod_NeonOcean_Debug.Publishing import Distribution
from Mod_NeonOcean_Debug.Tools import Exceptions

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

	try:
		Merging.Merge()
	except Exception as e:
		print("Failed to merge mod components.\n" + \
			  "Mod: '" + Mod.GetCurrentMod().Namespace + "' \n" + \
			  Exceptions.FormatException(e), file = sys.stderr)

	return UpdateGameFiles()

def UpdateGameFiles () -> bool:
	"""
	Send currently built mod files to the Sims 4 mod folder.
	:return:
	"""

	try:
		if os.path.exists(Mod.GetCurrentMod().UninstallPath):
			uninstallExitCode = subprocess.call([Mod.GetCurrentMod().UninstallPath, "-s", "-p"])  # type: int

			if uninstallExitCode != 0:
				print("Failed to uninstall previous version.", file = sys.stderr)
				return False

			time.sleep(0.25)
			os.remove(Mod.GetCurrentMod().UninstallPath)
			time.sleep(0.25)

		dir_util.copy_tree(Paths.BuildPath, Paths.S4ModsPath)
	except Exception as e:
		print("Failed to send mod to the Sims 4 mod folder.\n" + \
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
	"Quick": [
		Python.BuildPython
	],

	"Normal": [
		Python.BuildPython,
		STBL.BuildSTBLChanges,
		Package.BuildPackageChanges
	],

	"Rebuild": [
		Python.BuildPython,
		STBL.BuildSTBLEverything,
		Package.BuildPackageEverything
	]

}  # type: typing.Dict[str, typing.List[typing.Callable]]

_publishingPhases = [
	Distribution.BuildDistribution
]

_modBuildDefaultMode = "Normal"  # type: str
