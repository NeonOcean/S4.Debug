import json
import os
import typing

from Mod_NeonOcean_Debug import Mod

def GetEntries () -> typing.List[typing.Tuple[str, int]]:
	entries = list()  # type: typing.List[typing.Tuple[str, int]]

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if not os.path.exists(package.STBLPath):
			continue

		if os.path.exists(package.STBLSourcePath):
			for sourceName in os.listdir(package.STBLSourcePath):  # type: str
				sourceDirectoryPath = os.path.join(package.STBLSourcePath, sourceName)

				with open(os.path.join(sourceDirectoryPath, "STBL.json")) as stblInformationFile:
					stblInformation = json.JSONDecoder().decode(stblInformationFile.read())  # type: dict

				identifierPrefix = stblInformation["Identifier Prefix"]  # type: str

				hashDirectoryPath = os.path.join(sourceDirectoryPath, _keyDirectoryName)  # type: str

				for entryName in os.listdir(hashDirectoryPath):  # type: str
					entryName, entryExtension = os.path.splitext(entryName)  # type: str

					if entryExtension.lower() != ".txt":
						continue

					entryHashPath = os.path.join(hashDirectoryPath, entryName) + ".txt"  # type: str

					if os.path.exists(entryHashPath) and os.path.isfile(entryHashPath):
						entryIsValid = True  # type: bool

						for languageName in _languageNames:  # type: str
							entryLanguagePath = os.path.join(package.STBLSourcePath, sourceName, languageName, entryName) + ".txt"  # type: str

							if not os.path.exists(entryLanguagePath) or not os.path.isfile(entryLanguagePath):
								entryIsValid = False

						if entryIsValid:
							with open(entryHashPath) as entryHashFile:
								entryHashString = entryHashFile.read()  # type: str

								try:
									entryHash = int(entryHashString)  # type: int
								except Exception as e:
									raise Exception("Failed to read hash for entry '" + entryName + "'.") from e

							entries.append((identifierPrefix + entryName, entryHash))

	return entries

_keyDirectoryName = "Keys"  # type: str

_languageNames = [
	"Chinese Simplified",
	"Chinese Traditional",
	"Czech",
	"Danish",
	"Dutch",
	"English",
	"Finnish",
	"French",
	"German",
	"Greek",
	"Hungarian",
	"Italian",
	"Japanese",
	"Korean",
	"Norwegian",
	"Polish",
	"Portuguese Brazil",
	"Portuguese Portugal",
	"Russian",
	"Spanish Mexico",
	"Spanish Spain",
	"Swedish",
	"Thai"
]  # type: typing.List[str]