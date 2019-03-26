import shutil

from Mod_NeonOcean_Debug import Mod, Paths
from Mod_NeonOcean_Debug.Tools import IO, Python

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

	shutil.copy(Mod.GetCurrentMod().PythonBuildArchiveFilePath, Mod.GetCurrentMod().PythonMergeRoot)

	return True
