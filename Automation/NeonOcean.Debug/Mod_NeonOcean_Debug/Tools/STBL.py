import json
import os
import subprocess
import typing
from importlib import util
from xml.sax import saxutils

def ValidSTBLDirectory (directoryPath: str) -> bool:
	if not os.path.exists(directoryPath):
		return False

	if not os.path.exists(os.path.join(directoryPath, "STBL.json")):
		return False

	return True

def CanBuildSourceXML () -> bool:
	return True

def BuildSourceXML (buildFilePath: str, sourceDirectoryPath: str) -> None:
	entries = list()  # type: typing.List[str]

	keyDirectoryPath = os.path.join(sourceDirectoryPath, _keyDirectoryName)  # type: str

	if os.path.exists(keyDirectoryPath):
		for entryName in os.listdir(keyDirectoryPath):  # type: str
			entryName, entryExtension = os.path.splitext(entryName)  # type: str

			if entryExtension.lower() != ".txt":
				continue

			entryKeyPath = os.path.join(keyDirectoryPath, entryName) + ".txt"  # type: str

			if os.path.exists(entryKeyPath) and os.path.isfile(entryKeyPath):
				entryIsValid = True  # type: bool

				for languageName in _languageNames:  # type: str
					entryLanguagePath = os.path.join(sourceDirectoryPath, languageName, entryName) + ".txt"  # type: str

					if not os.path.exists(entryLanguagePath) or not os.path.isfile(entryLanguagePath):
						entryIsValid = False

				if entryIsValid:
					entries.append(entryName)

	# noinspection SpellCheckingInspection
	buildText = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + \
				"<File xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">\n"

	with open(os.path.join(sourceDirectoryPath, "STBL.json")) as stblInformationFile:
		stblInformation = json.JSONDecoder().decode(stblInformationFile.read())  # type: dict

	buildText += "\t<Group>" + stblInformation["Source File"]["Group"] + "</Group>\n"
	buildText += "\t<Instance>" + stblInformation["Source File"]["Instance"] + "</Instance>\n"
	buildText += "\t<Name>" + stblInformation["Source File"]["Name"] + "</Name>\n"

	identifierPrefix = stblInformation["Identifier Prefix"]  # type: str

	if len(entries) == 0:
		buildText += "\t<Entries />\n"
	else:
		buildText += "\t<Entries>\n"

		for entryName in entries:  # type: str
			with open(os.path.join(sourceDirectoryPath, _keyDirectoryName, entryName) + ".txt") as entryKeyFile:
				entryKey = int(entryKeyFile.read())

			buildText += "\t\t<Entry>\n"
			buildText += "\t\t\t<Key>" + str(entryKey) + "</Key>\n"
			buildText += "\t\t\t<Identifier>" + saxutils.escape(identifierPrefix + entryName) + "</Identifier>\n"

			mainLanguageXMLName = _mainLanguage.replace(" ", "")  # type: str

			entryMainLanguageFilePath = os.path.join(sourceDirectoryPath, _mainLanguage, entryName) + ".txt"

			with open(entryMainLanguageFilePath) as entryMainLanguageFile:
				entryMainLanguageText = entryMainLanguageFile.read()  # type: str

				entryMainLanguageText = entryMainLanguageText.replace("\r\n", "\\n")
				entryMainLanguageText = entryMainLanguageText.replace("\n", "\\n")
				entryMainLanguageText = saxutils.escape(entryMainLanguageText)

				if not entryMainLanguageText or entryMainLanguageText.isspace():
					entryMainLanguageText = None

				if entryMainLanguageText is not None:
					buildText += "\t\t\t<" + mainLanguageXMLName + ">" + entryMainLanguageText + "</" + mainLanguageXMLName + ">\n"

			for languageName in _languageNames:  # type: str
				if languageName == _mainLanguage:
					continue

				languageXMLName = languageName.replace(" ", "")  # type: str

				entryLanguageFilePath = os.path.join(sourceDirectoryPath, languageName, entryName) + ".txt"  # type: str

				with open(entryLanguageFilePath) as entryLanguageFile:
					entryLanguageText = entryLanguageFile.read()  # type: str

					entryLanguageText = entryLanguageText.replace("\r\n", "\\n")
					entryLanguageText = entryLanguageText.replace("\n", "\\n")
					entryLanguageText = saxutils.escape(entryLanguageText)

					if not entryLanguageText or entryLanguageText.isspace():
						entryLanguageText = None

					if entryLanguageText is not None:
						buildText += "\t\t\t<" + languageXMLName + ">" + entryLanguageText + "</" + languageXMLName + ">\n"

			buildText += "\t\t</Entry>\n"

		buildText += "\t</Entries>\n"

	buildText += "</File>"

	buildDirectoryPath = os.path.dirname(buildFilePath)  # type: str

	if not os.path.exists(buildDirectoryPath):
		os.makedirs(buildDirectoryPath)

	with open(buildFilePath, "w+") as buildFile:
		buildFile.write(buildText)

def CanBuildIdentifiersXML () -> bool:
	return True

def GetIdentifiersFileName (identifierName: str) -> str:
	return identifierName + ".xml"

def GetIdentifiersSourceInfoFileName (identifierName: str) -> str:
	# noinspection SpellCheckingInspection
	return GetIdentifiersFileName(identifierName) + ".sourceinfo"

def BuildIdentifiersXML (buildFilePath: str, sourceInfoFilePath: str, sourceDirectoryPath: str) -> None:
	entries = list()  # type: typing.List[str]

	keyDirectoryPath = os.path.join(sourceDirectoryPath, _keyDirectoryName)  # type: str

	if os.path.exists(keyDirectoryPath):
		for entryName in os.listdir(keyDirectoryPath):  # type: str
			entryName, entryExtension = os.path.splitext(entryName)  # type: str

			if entryExtension.lower() != ".txt":
				continue

			entryKeyPath = os.path.join(keyDirectoryPath, entryName) + ".txt"  # type: str

			if os.path.exists(entryKeyPath) and os.path.isfile(entryKeyPath):
				entryIsValid = True  # type: bool

				for languageName in _languageNames:  # type: str
					entryLanguagePath = os.path.join(sourceDirectoryPath, languageName, entryName) + ".txt"  # type: str

					if not os.path.exists(entryLanguagePath) or not os.path.isfile(entryLanguagePath):
						entryIsValid = False

				if entryIsValid:
					entries.append(entryName)

	with open(os.path.join(sourceDirectoryPath, "STBL.json")) as stblInformationFile:
		stblInformation = json.JSONDecoder().decode(stblInformationFile.read())  # type: dict

	identifiersFileName = stblInformation["Identifiers File"]["Name"]  # type: str
	identifiersFileGroup = stblInformation["Identifiers File"]["Group"]  # type: str
	identifiersFileInstance = stblInformation["Identifiers File"]["Instance"]  # type: str

	identifierPrefix = stblInformation["Identifier Prefix"]  # type: str

	buildText = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
	# noinspection SpellCheckingInspection
	buildText += "<I n=\"" + identifiersFileName + "\" s=\"" + str(int(identifiersFileInstance, 16)) + "\" i=\"snippet\" m=\"snippets\" c=\"NeonoceanGlobalLanguageIdentifiers\">\n"
	buildText += "\t<L n=\"value\">\n"

	for entryName in entries:  # type: str
		with open(os.path.join(sourceDirectoryPath, _keyDirectoryName, entryName) + ".txt") as entryKeyFile:
			entryKey = int(entryKeyFile.read())

		buildText += "\t\t<U>\n"
		buildText += "\t\t\t<T n=\"key\">" + saxutils.escape(identifierPrefix + entryName) + "</T>\n"
		buildText += "\t\t\t<T n=\"value\">" + str(entryKey) + "</T>\n"
		buildText += "\t\t</U>\n"

	buildText += "\t</L>\n" \
				 "</I>"

	buildDirectoryPath = os.path.dirname(buildFilePath)  # type: str

	if not os.path.exists(buildDirectoryPath):
		os.makedirs(buildDirectoryPath)

	with open(buildFilePath, "w+") as buildFile:
		buildFile.write(buildText)

	# noinspection SpellCheckingInspection
	sourceInfoFormatting = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<SourceInfo xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">\n" \
						   "\t<Name>{0}</Name>\n" \
						   "\t<Type>{1}</Type>\n" \
						   "\t<Group>{2}</Group>\n" \
						   "\t<Instance>{3}</Instance>\n" \
						   "</SourceInfo>"

	sourceInfoText = sourceInfoFormatting.format(identifiersFileName, "7DF2169C", identifiersFileGroup, identifiersFileInstance)

	with open(sourceInfoFilePath, "w+") as sourceInfoFile:
		sourceInfoFile.write(sourceInfoText)

def CanBuildSTBL () -> bool:
	automationModule = util.find_spec("Automation")

	if automationModule is None:
		return False

	from Automation import Applications

	for applicationName, applicationFunction in BuildSTBLApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			return True

	return False

def BuildSTBL (buildDirectoryPath: str, sourceFilePath: str) -> None:
	from Automation import Applications

	for applicationName, applicationFunction in BuildSTBLApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			if applicationFunction(application, buildDirectoryPath, sourceFilePath):
				break

def STBLSourceFilesExists (sourceNameTemplate: str, buildDirectoryPath: str) -> bool:
	for languageName in _languageNames:  # type: str
		languageName = languageName.replace(" ", "_")

		languageSourceFilePath = os.path.join(buildDirectoryPath, sourceNameTemplate.format(languageName) + ".stbl")  # type: str
		# noinspection SpellCheckingInspection
		languageSourceInfoFilePath = languageSourceFilePath + ".sourceinfo"  # type: str

		if not os.path.exists(languageSourceFilePath) or not os.path.exists(languageSourceInfoFilePath):
			return False

	return True

def _BuildSTBLSTBLBuilder (application, buildDirectoryPath: str, sourceFilePath: str) -> bool:
	stblBuilderExitCode = subprocess.call([application.ExecutablePath, "-t", buildDirectoryPath, "-s", sourceFilePath, "-p"])  # type: int

	if stblBuilderExitCode != 0:
		raise Exception("STBLBuilder failed to complete a task.")

	return True

BuildSTBLApplications = {
	"STBLBuilder-v1.1.0": _BuildSTBLSTBLBuilder
}  # type: typing.Dict[str, typing.Callable]

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

_keyDirectoryName = "Keys"  # type: str

_mainLanguage = _languageNames[5]  # type: str
