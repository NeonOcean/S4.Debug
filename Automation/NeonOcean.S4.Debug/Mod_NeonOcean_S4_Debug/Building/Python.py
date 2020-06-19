import os
import shutil

from Mod_NeonOcean_S4_Debug import Mod, Paths
from Mod_NeonOcean_S4_Debug.Tools import IO, Python

def BuildPython () -> bool:
	if not Python.CanBuildPython():
		return False

	IO.ClearDirectory(Paths.PythonBuildArchivePath)
	IO.ClearDirectory(Paths.PythonBuildLoosePath)

	Python.BuildPython(Paths.PythonBuildLoosePath,
					   Mod.GetCurrentMod().PythonBuildArchiveFilePath,
					   Mod.GetCurrentMod().PythonSourceRootPath,
					   Mod.GetCurrentMod().PythonSourceTargetPath,
					   Mod.GetCurrentMod().PythonSourceExcludedFiles)

	if not os.path.exists(Mod.GetCurrentMod().PythonMergeRoot):
		os.makedirs(Mod.GetCurrentMod().PythonMergeRoot)

	shutil.copy(Mod.GetCurrentMod().PythonBuildArchiveFilePath, Mod.GetCurrentMod().PythonMergeRoot)

	return True
