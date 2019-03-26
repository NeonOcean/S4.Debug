import os
import json

from Mod_NeonOcean_Debug import Mod
from Mod_NeonOcean_Debug.Tools import STBL

def BuildSTBLChanges () -> bool:
	canBuildSourceXML = STBL.CanBuildSourceXML()  # type: bool
	canBuildIdentifierXML = STBL.CanBuildIdentifierXML()  # type: bool
	canBuildSTBL = STBL.CanBuildSTBL()  # type: bool

	if not canBuildSourceXML or not canBuildIdentifierXML or not canBuildSTBL:
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if not os.path.exists(package.STBLSourcePath):
			continue

		builtSourceXML = False  # type: bool

		for sourceName in os.listdir(package.STBLSourcePath):  # type: str
			sourceDirectoryPath = os.path.join(package.STBLSourcePath, sourceName)  # type: str

			if os.path.isdir(sourceDirectoryPath):
				if not STBL.ValidSTBLDirectory(sourceDirectoryPath):
					continue

				sourceBuildFilePath = os.path.join(package.STBLBuildPath, os.path.splitext(sourceName)[0] + ".xml")  # type: str

				if not os.path.exists(sourceBuildFilePath):
					STBL.BuildSourceXML(sourceBuildFilePath, sourceDirectoryPath)
					builtSourceXML = True
				else:
					sourceTempFilePath = os.path.splitext(sourceBuildFilePath)[0] + ".temp"

					STBL.BuildSourceXML(sourceTempFilePath, sourceDirectoryPath)

					with open(sourceBuildFilePath, newline = "") as sourceBuildFile:
						currentSourceBuild = sourceBuildFile.read()

					with open(sourceTempFilePath, newline = "") as sourceTempFile:
						newSourceBuild = sourceTempFile.read()

						if currentSourceBuild != newSourceBuild:
							with open(sourceBuildFilePath, "w+", newline = "") as sourceBuildFile:
								sourceBuildFile.write(newSourceBuild)

							builtSourceXML = True

					os.remove(sourceTempFilePath)

				with open(os.path.join(sourceDirectoryPath, "STBL.json")) as stblInformationFile:
					stblInformation = json.JSONDecoder().decode(stblInformationFile.read())  # type: dict

				identifiersFileGroup = stblInformation["Identifiers File"]["Group"]  # type: str
				identifiersFileInstance = stblInformation["Identifiers File"]["Instance"]  # type: str
				identifiersFileName = stblInformation["Identifiers File"]["Name"]   # type: str

				identifierBuildFilePath = os.path.join(package.SourceLoosePath, STBL.GetIdentifierFileName(identifiersFileGroup, identifiersFileInstance, identifiersFileName))  # type: str

				if not os.path.exists(identifierBuildFilePath):
					STBL.BuildIdentifierXML(identifierBuildFilePath, sourceDirectoryPath)
				else:
					identifierTempFilePath = os.path.splitext(identifierBuildFilePath)[0] + ".temp"

					STBL.BuildIdentifierXML(identifierTempFilePath, sourceDirectoryPath)

					with open(identifierBuildFilePath, newline = "") as identifierBuildFile:
						currentIdentifierBuild = identifierBuildFile.read()

					with open(identifierTempFilePath, newline = "") as identifierTempFile:
						newIdentifierBuild = identifierTempFile.read()

					if currentIdentifierBuild != newIdentifierBuild:
						with open(identifierBuildFilePath, "w+", newline = "") as identifierBuildFile:
							identifierBuildFile.write(newIdentifierBuild)

						builtSourceXML = True

					os.remove(identifierTempFilePath)

		if builtSourceXML and os.path.exists(package.STBLBuildPath):
			for stblXMLFileName in os.listdir(package.STBLBuildPath):  # type: str
				stblXMLFilePath = os.path.join(package.STBLBuildPath, stblXMLFileName)  # type: str

				if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
					STBL.BuildSTBL(package.SourceLoosePath, stblXMLFilePath)

	return True

def BuildSTBLEverything () -> bool:
	canBuildSourceXML = STBL.CanBuildSourceXML()  # type: bool
	canBuildIdentifierXML = STBL.CanBuildIdentifierXML()  # type: bool
	canBuildSTBL = STBL.CanBuildSTBL()  # type: bool

	if not canBuildSourceXML or not canBuildIdentifierXML or not canBuildSTBL:
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if os.path.exists(package.STBLSourcePath):
			for sourceName in os.listdir(package.STBLSourcePath):  # type: str
				sourceDirectoryPath = os.path.join(package.STBLSourcePath, sourceName)  # type: str

				if os.path.isdir(sourceDirectoryPath):
					if not STBL.ValidSTBLDirectory(sourceDirectoryPath):
						continue

					sourceBuildFilePath = os.path.join(package.STBLBuildPath, os.path.splitext(sourceName)[0] + ".xml")  # type: str

					STBL.BuildSourceXML(sourceBuildFilePath, sourceDirectoryPath)

		if os.path.exists(package.STBLBuildPath):
			for stblXMLFileName in os.listdir(package.STBLSourcePath):  # type: str
				stblXMLFilePath = os.path.join(package.STBLSourcePath, stblXMLFileName)  # type: str

				if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
					STBL.BuildSTBL(package.SourceLoosePath, stblXMLFilePath)

	return True
