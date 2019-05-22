import os
import typing
from json import decoder, encoder

from Mod_NeonOcean_Debug import Mod
from Mod_NeonOcean_Debug.Tools import Package

def BuildPackageChanges () -> bool:
	if not Package.CanBuildPackage():
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		baseFileExists = os.path.exists(package.SourceBaseFilePath)  # type: bool
		loosePathExists = os.path.exists(package.SourceLoosePath)  # type: bool

		packageManifest = None  # type: typing.Dict[str, typing.Union[float, typing.Dict[str, float]]]

		if not os.path.exists(package.BuildFilePath):
			_BuildPackageEverythingInternal(package)
			return True

		if os.path.exists(package.BuildManifestFilePath):
			with open(package.BuildManifestFilePath) as packageManifestFile:
				packageManifest = decoder.JSONDecoder().decode(packageManifestFile.read())

		if packageManifest is not None and not isinstance(packageManifest, dict):
			packageManifest = None

		if packageManifest is not None and (not "Loose" in packageManifest or not "Base" in packageManifest):
			packageManifest = None

		if packageManifest is None:
			_BuildPackageEverythingInternal(package)
			return True
		else:
			filesChanged = False  # type: str

			if baseFileExists:
				baseCurrentChangeTime = os.path.getmtime(package.SourceBaseFilePath)  # type: float

				if packageManifest["Base"] != os.path.getmtime(package.SourceBaseFilePath):
					packageManifest["Base"] = baseCurrentChangeTime
					filesChanged = True

			if loosePathExists:
				for entryFileName, entryChangeTime in packageManifest["Loose"].items():  # type: str, float
					entryFilePath = os.path.join(package.SourceLoosePath, entryFileName)  # type: str

					if not os.path.exists(entryFilePath):
						filesChanged = True
						continue

					entryCurrentChangeTime = os.path.getmtime(entryFilePath)  # type: float

					if entryCurrentChangeTime != entryChangeTime:
						packageManifest["Loose"][entryFileName] = entryCurrentChangeTime
						filesChanged = True

				for sourceFileName in os.listdir(package.SourceLoosePath):
					sourceFilePath = os.path.join(package.SourceLoosePath, sourceFileName)  # type: str

					if os.path.isfile(sourceFilePath):
						sourceFileDuplicate = False  # type: bool

						for entryFileName in packageManifest["Loose"].keys():  # type: str
							if entryFileName.lower() == sourceFileName.lower():
								sourceFileDuplicate = True
								break

						if not sourceFileDuplicate:
							packageManifest["Loose"][sourceFileName] = os.path.getmtime(sourceFilePath)
							filesChanged = True

			if filesChanged:
				addingFiles = list()  # type: typing.List[str]

				if loosePathExists:
					for sourceFileName in os.listdir(package.SourceLoosePath):
						addingFiles.append(os.path.join(package.SourceLoosePath, sourceFileName))

				if baseFileExists:
					Package.BuildPackage(package.BuildFilePath,
										 baseFilePath = package.SourceBaseFilePath,
										 addingFilePaths = addingFiles)
				else:
					Package.BuildPackage(package.BuildFilePath,
										 addingFilePaths = addingFiles)

				with open(package.BuildManifestFilePath, "w+") as packageManifestFile:
					packageManifestFile.write(encoder.JSONEncoder(indent = "\t").encode(packageManifest))

	return True

def BuildPackageEverything () -> bool:
	if not Package.CanBuildPackage():
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		_BuildPackageEverythingInternal(package)

	return True

def _BuildPackageEverythingInternal (package: Mod.Package) -> None:
	baseFileExists = os.path.exists(package.SourceBaseFilePath)  # type: bool
	loosePathExists = os.path.exists(package.SourceLoosePath)  # type: bool

	addingFilePaths = list()  # type: typing.List[str]

	if loosePathExists:
		for sourceFileName in os.listdir(package.SourceLoosePath):
			sourceFilePath = os.path.join(package.SourceLoosePath, sourceFileName)

			if os.path.isfile(sourceFilePath):
				addingFilePaths.append(sourceFilePath)

	if baseFileExists:
		Package.BuildPackage(package.BuildFilePath,
							 baseFilePath = package.SourceBaseFilePath,
							 addingFilePaths = addingFilePaths)
	else:
		Package.BuildPackage(package.BuildFilePath,
							 addingFilePaths = addingFilePaths)

	packageManifest = dict()  # type: typing.Dict[str, typing.Union[float, typing.Dict[str, float]]]

	packageManifest["Base"] = os.path.getmtime(package.SourceBaseFilePath)
	packageManifest["Loose"] = dict()

	for sourceFilePath in addingFilePaths:
		packageManifest["Loose"][os.path.split(sourceFilePath)[1]] = os.path.getmtime(sourceFilePath)

	with open(package.BuildManifestFilePath, "w+") as packageManifestFile:
		packageManifestFile.write(encoder.JSONEncoder(indent = "\t").encode(packageManifest))
