import os
import shutil
from distutils import dir_util

from Mod_NeonOcean_S4_Debug import Mod, Paths
from Mod_NeonOcean_S4_Debug.Tools import IO, Merging

def Merge () -> bool:
	IO.ClearDirectory(Paths.BuildPath)

	_MergeLoose()
	_MergeMisc()
	_MergeInformation()
	_MergePython()
	_MergePackage()

	#_BuildManifest()

	return True

def _MergeInformation () -> None:
	if os.path.exists(Paths.InformationBuildPath):
		dir_util.copy_tree(Paths.InformationBuildPath, Paths.BuildPath)

def _MergeLoose () -> None:
	if os.path.exists(Paths.LoosePath):
		dir_util.copy_tree(Paths.LoosePath, Paths.BuildPath)

def _MergeMisc () -> None:
	if os.path.exists(Paths.MiscPath):
		dir_util.copy_tree(Paths.MiscPath, Paths.BuildPath)

def _MergePython () -> None:
	if os.path.exists(Mod.GetCurrentMod().PythonBuildArchiveFilePath):
		shutil.copy(Mod.GetCurrentMod().PythonBuildArchiveFilePath, Mod.GetCurrentMod().PythonMergeRoot)

def _MergePackage () -> None:
	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if os.path.exists(package.BuildFilePath):
			shutil.copy(package.BuildFilePath, package.MergeRoot)

def _BuildManifest () -> None:
	Merging.BuildManifest(os.path.join(Mod.GetCurrentMod().Namespace, Mod.GetCurrentMod().Namespace + "-Uninstall-Files.txt"), Paths.BuildPath)
