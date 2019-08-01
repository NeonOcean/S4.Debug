import os
import json

from Mod_NeonOcean_Debug import Mod
from Mod_NeonOcean_Debug.Tools import STBL

def BuildSTBLChanges () -> bool:
	canBuildSourceXML = STBL.CanBuildSourceXML()  # type: bool
	canBuildIdentifiersXML = STBL.CanBuildIdentifiersXML()  # type: bool
	canBuildSTBL = STBL.CanBuildSTBL()  # type: bool

	if not canBuildSourceXML or not canBuildIdentifiersXML or not canBuildSTBL:
		return False

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if not os.path.exists(package.STBLSourcePath):
			continue

		buildSTBLSources = False  # type: bool

		for sourceName in os.listdir(package.STBLSourcePath):  # type: str
			sourceDirectoryPath = os.path.join(package.STBLSourcePath, sourceName)  # type: str

			if os.path.isdir(sourceDirectoryPath):
				if not STBL.ValidSTBLDirectory(sourceDirectoryPath):
					continue

				with open(os.path.join(sourceDirectoryPath, "STBL.json")) as stblInformationFile:
					stblInformation = json.JSONDecoder().decode(stblInformationFile.read())  # type: dict

				stblSourceFileName = stblInformation["Source File"]["Name"]  # type: str

				if not STBL.STBLSourceFilesExists(stblSourceFileName, package.SourceLoosePath):
					buildSTBLSources = True

				sourceBuildFilePath = os.path.join(package.STBLBuildPath, os.path.splitext(sourceName)[0] + ".xml")  # type: str

				if not os.path.exists(sourceBuildFilePath):
					STBL.BuildSourceXML(sourceBuildFilePath, sourceDirectoryPath)
					buildSTBLSources = True
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

							buildSTBLSources = True

					os.remove(sourceTempFilePath)

				identifiersFileName = stblInformation["Identifiers File"]["Name"]   # type: str

				identifiersBuildFilePath = os.path.join(package.SourceLoosePath, STBL.GetIdentifiersFileName(identifiersFileName))  # type: str
				identifiersSourceInfoBuildFilePath = os.path.join(package.SourceLoosePath, STBL.GetIdentifiersSourceInfoFileName(identifiersFileName))  # type: str

				if not os.path.exists(identifiersBuildFilePath) or not os.path.exists(identifiersSourceInfoBuildFilePath):
					STBL.BuildIdentifiersXML(identifiersBuildFilePath, identifiersSourceInfoBuildFilePath, sourceDirectoryPath)
				else:
					identifiersTempFilePath = identifiersBuildFilePath + ".temp"
					identifiersSourceInfoTempFilePath = identifiersSourceInfoBuildFilePath + ".temp"  # type: str

					STBL.BuildIdentifiersXML(identifiersTempFilePath, identifiersSourceInfoTempFilePath, sourceDirectoryPath)

					with open(identifiersBuildFilePath, newline = "") as identifiersBuildFile:
						currentIdentifiersBuild = identifiersBuildFile.read()

					with open(identifiersTempFilePath, newline = "") as identifiersTempFile:
						newIdentifiersBuild = identifiersTempFile.read()

					if currentIdentifiersBuild != newIdentifiersBuild:
						with open(identifiersBuildFilePath, "w+", newline = "") as identifiersBuildFile:
							identifiersBuildFile.write(newIdentifiersBuild)

						buildSTBLSources = True

					with open(identifiersSourceInfoBuildFilePath, newline = "") as identifiersSourceInfoBuildFile:
						currentIdentifiersSourceInfoBuild = identifiersSourceInfoBuildFile.read()

					with open(identifiersSourceInfoTempFilePath, newline = "") as identifiersSourceInfoTempFile:
						newIdentifiersSourceInfoBuild = identifiersSourceInfoTempFile.read()

					if currentIdentifiersSourceInfoBuild != newIdentifiersSourceInfoBuild:
						with open(identifiersSourceInfoBuildFilePath, "w+", newline = "") as identifiersSourceInfoBuildFile:
							identifiersSourceInfoBuildFile.write(newIdentifiersSourceInfoBuild)

						buildSTBLSources = True

					os.remove(identifiersTempFilePath)
					os.remove(identifiersSourceInfoTempFilePath)

		if buildSTBLSources and os.path.exists(package.STBLBuildPath):
			for stblXMLFileName in os.listdir(package.STBLBuildPath):  # type: str
				stblXMLFilePath = os.path.join(package.STBLBuildPath, stblXMLFileName)  # type: str

				if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
					STBL.BuildSTBL(package.SourceLoosePath, stblXMLFilePath)

	return True

def BuildSTBLEverything () -> bool:
	canBuildSourceXML = STBL.CanBuildSourceXML()  # type: bool
	canBuildIdentifiersXML = STBL.CanBuildIdentifiersXML()  # type: bool
	canBuildSTBL = STBL.CanBuildSTBL()  # type: bool

	if not canBuildSourceXML or not canBuildIdentifiersXML or not canBuildSTBL:
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

					with open(os.path.join(sourceDirectoryPath, "STBL.json")) as stblInformationFile:
						stblInformation = json.JSONDecoder().decode(stblInformationFile.read())  # type: dict

					identifiersFileName = stblInformation["Identifiers File"]["Name"]  # type: str

					identifiersBuildFilePath = os.path.join(package.SourceLoosePath, STBL.GetIdentifiersFileName(identifiersFileName))  # type: str
					identifiersSourceInfoFilePath = os.path.join(package.SourceLoosePath, STBL.GetIdentifiersSourceInfoFileName(identifiersFileName))  # type: str

					STBL.BuildIdentifiersXML(identifiersBuildFilePath, identifiersSourceInfoFilePath, sourceDirectoryPath)

		if os.path.exists(package.STBLBuildPath):
			for stblXMLFileName in os.listdir(package.STBLBuildPath):  # type: str
				stblXMLFilePath = os.path.join(package.STBLBuildPath, stblXMLFileName)  # type: str

				if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
					STBL.BuildSTBL(package.SourceLoosePath, stblXMLFilePath)

	return True
