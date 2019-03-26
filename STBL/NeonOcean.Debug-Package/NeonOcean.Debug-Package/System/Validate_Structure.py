import os
import typing

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Validating structure...")

	keyDirectoryPath = os.path.join(sourcePath, _keyDirectoryName)  # type: str

	invalidEntries = list()  # type: typing.List[str]
	validEntries = list()  # type: typing.List[str]

	for entryName in os.listdir(keyDirectoryPath):  # type: str
		entryName, entryExtension = os.path.splitext(entryName)  # type: str

		if entryExtension.lower() != ".txt":
			continue

		entryKeyPath = os.path.join(keyDirectoryPath, entryName) + ".txt"  # type: str

		if os.path.exists(entryKeyPath) and os.path.isfile(entryKeyPath):
			entryIsValid = True  # type: bool

			for languageName in _languageNames:  # type: str
				entryLanguagePath = os.path.join(sourcePath, languageName, entryName) + ".txt"  # type: str

				if not os.path.exists(entryLanguagePath) or not os.path.isfile(entryLanguagePath):
					entryIsValid = False

			if entryIsValid:
				validEntries.append(entryName)
			else:
				invalidEntries.append(entryName)

	for languageName in _languageNames:
		if languageName == _mainLanguage:
			continue

		languagePath = os.path.join(sourcePath, languageName)  # type: str

		for entryName in os.listdir(languagePath):
			entryName = os.path.splitext(entryName)[0]
			entryNameLower = entryName.lower()

			entryIsValid = False  # type: bool

			for validEntryName in validEntries:  # type: str
				validEntryNameLower = validEntryName.lower()  # type: str

				if entryNameLower == validEntryNameLower:
					entryIsValid = True
					continue

			if not entryIsValid:
				appendInvalidEntry = True  # type: bool

				for invalidEntryName in invalidEntries:  # type: str
					invalidEntryNameLower = invalidEntryName.lower()  # type: str

					if entryNameLower == invalidEntryNameLower:
						appendInvalidEntry = False
						continue

				if appendInvalidEntry:
					invalidEntries.append(entryName)

	if len(invalidEntries) == 0:
		print("No structure problems detected.")
	else:
		invalidText = "The following entries exist but are missing for one or more languages:\n"

		for invalidEntryName in invalidEntries:  # type: str
			invalidText += invalidEntryName + "\n"

		print(invalidText)

	input("Press enter to continue\n")

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

_keyDirectoryName = "Hash"  # type: str

_mainLanguage = _languageNames[5]  # type: str

if __name__ == "__main__":
	Run()
