import json
import os
import shutil
import sys
import typing
from distutils import dir_util

from Mod_NeonOcean_Debug import Mod
from Mod_NeonOcean_Debug.Tools import Exceptions, STBL

ManifestBuiltModifiedTimeKey = "BuiltModifiedTime"  # type: str
ManifestBuiltFileNamesKey = "BuiltFileNames"  # type: str

def BuildSTBLChanges () -> bool:
	canBuildSTBL = STBL.CanBuildSTBL()  # type: bool

	if not canBuildSTBL:
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if not os.path.exists(package.STBLPath):
			continue

		for stblXMLFileName in os.listdir(package.STBLPath):  # type: str
			stblXMLFilePath = os.path.join(package.STBLPath, stblXMLFileName)  # type: str

			if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
				manifestFilePath = os.path.splitext(stblXMLFilePath)[0] + "_Manifest.json"  # type: str

				modifiedTime = os.path.getmtime(stblXMLFilePath)  # type: float
				builtModifiedTime = None  # type: typing.Optional[int]
				builtFileNames = list()  # type: typing.List[str]

				try:
					if os.path.exists(manifestFilePath):
						with open(manifestFilePath) as manifestFile:
							manifest = json.JSONDecoder().decode(manifestFile.read())  # type: typing.Dict[str, typing.Any]

						if not isinstance(manifest, dict):
							raise Exceptions.IncorrectTypeException(manifest, "Root", (dict,))

						if ManifestBuiltModifiedTimeKey in manifest:
							builtModifiedTime = manifest[ManifestBuiltModifiedTimeKey]

						if not isinstance(builtModifiedTime, float) and not isinstance(builtModifiedTime, int):
							incorrectValue = builtModifiedTime  # type: typing.Any
							builtModifiedTime = None
							raise Exceptions.IncorrectTypeException(incorrectValue, "Root[%s]" % ManifestBuiltModifiedTimeKey, (dict,))

						if ManifestBuiltFileNamesKey in manifest:
							builtFileNames = manifest[ManifestBuiltFileNamesKey]

						if not isinstance(builtFileNames, list):
							incorrectValue = builtFileNames  # type: typing.Any
							builtFileNames = list()
							raise Exceptions.IncorrectTypeException(incorrectValue, "Root[%s]" % ManifestBuiltFileNamesKey, (dict,))

						for builtFileNameIndex in range(len(builtFileNames)):  # type: int
							builtFileName = builtFileNames[builtFileNameIndex]  # type: str

							if not isinstance(builtFileName, str):
								builtFileNames = list()
								raise Exceptions.IncorrectTypeException(builtFileName, "Root[%s][%s]" % (ManifestBuiltFileNamesKey, builtFileNameIndex), (dict,))

				except Exception as e:
					print("Failed to read STBL manifest file at '" + manifestFilePath + "'\n" + str(e), file = sys.stderr)

				missingBuiltFile = False  # type: bool

				for builtFileName in builtFileNames:
					builtFilePath = os.path.join(package.SourceLoosePath, builtFileName)  # type: str

					if not os.path.exists(builtFilePath):
						missingBuiltFile = True
						break

				if missingBuiltFile or modifiedTime != builtModifiedTime:
					buildTempDirectory = stblXMLFilePath + "_Temp_Build"  # type: str

					if not os.path.exists(buildTempDirectory):
						os.makedirs(buildTempDirectory)

					try:
						STBL.BuildSTBL(buildTempDirectory, stblXMLFilePath)

						manifest = dict()  # type: typing.Dict[str, typing.Any]

						manifest[ManifestBuiltModifiedTimeKey] = modifiedTime
						builtFileNames = list()

						for builtFileName in os.listdir(buildTempDirectory):
							builtFilePath = os.path.join(buildTempDirectory, builtFileName)

							if os.path.isfile(builtFilePath):
								builtFileNames.append(builtFileName)

						manifest[ManifestBuiltFileNamesKey] = builtFileNames

						with open(manifestFilePath, "w+") as manifestFile:
							manifestFile.write(json.JSONEncoder(indent = "\t").encode(manifest))

						dir_util.copy_tree(buildTempDirectory, package.SourceLoosePath)
					finally:
						shutil.rmtree(buildTempDirectory)

	return True

def BuildSTBLEverything () -> bool:
	canBuildSTBL = STBL.CanBuildSTBL()  # type: bool

	if not canBuildSTBL:
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if not os.path.exists(package.STBLPath):
			continue

		for stblXMLFileName in os.listdir(package.STBLPath):  # type: str
			stblXMLFilePath = os.path.join(package.STBLPath, stblXMLFileName)  # type: str

			if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
				modifiedTime = os.path.getmtime(stblXMLFilePath)  # type: float
				manifestFilePath = os.path.splitext(stblXMLFilePath)[0] + "_Manifest.json"  # type: str

				buildTempDirectory = stblXMLFilePath + "_Temp_Build"  # type: str

				if not os.path.exists(buildTempDirectory):
					os.makedirs(buildTempDirectory)
				try:
					STBL.BuildSTBL(buildTempDirectory, stblXMLFilePath)

					manifest = dict()  # type: typing.Dict[str, typing.Any]

					manifest[ManifestBuiltModifiedTimeKey] = modifiedTime
					builtFileNames = list()

					for builtFileName in os.listdir(buildTempDirectory):
						builtFilePath = os.path.join(buildTempDirectory, builtFileName)

						if os.path.isfile(builtFilePath):
							builtFileNames.append(builtFileName)

					manifest[ManifestBuiltFileNamesKey] = builtFileNames

					with open(manifestFilePath, "w+") as manifestFile:
						manifestFile.write(json.JSONEncoder(indent = "\t").encode(manifest))

					dir_util.copy_tree(buildTempDirectory, package.SourceLoosePath)
				finally:
					shutil.rmtree(buildTempDirectory)

	return True
