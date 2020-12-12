import os
import typing
from NeonOcean.S4.Main import Reporting, LoadingShared
from NeonOcean.S4.Debug import This

# noinspection PyUnusedLocal
def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	Reporting.RegisterReportFileCollector(_PersistentCollector)

# noinspection PyUnusedLocal
def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	Reporting.UnregisterReportFileCollector(_PersistentCollector)

def _GetIgnoringPersistentDirectories () -> typing.List[str]:
	"""
	Each of these paths should be normalized before they are returned.
	"""

	ignoringDirectories = [

	]  # type: typing.List[str]

	return ignoringDirectories

def _PersistentCollector () -> typing.List[str]:
	persistentFilePaths = list()  # type: typing.List[str]

	ignoringDirectories = _GetIgnoringPersistentDirectories()  # type: typing.List[str]

	for directoryRoot, directoryNames, fileNames in os.walk(This.Mod.PersistentPath):  # type: str, list, list
		normalizedDirectoryRoot = os.path.normpath(directoryRoot)  # type: str

		ignoreDirectory = False  # type: bool

		for ignoringDirectory in ignoringDirectories:
			if normalizedDirectoryRoot.startswith(ignoringDirectory):
				ignoreDirectory = True

		if ignoreDirectory:
			continue

		for fileName in fileNames:
			filePath = os.path.join(directoryRoot, fileName)  # type: str

			persistentFilePaths.append(filePath)

	return persistentFilePaths