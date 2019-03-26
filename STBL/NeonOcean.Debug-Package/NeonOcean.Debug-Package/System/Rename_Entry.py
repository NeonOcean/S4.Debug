import os
import typing

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Renaming entry...")
	currentEntryName = input("Input the localization entry's current identifier.\n")  # type: str
	desiredEntryName = input("Input the localization entry's new identifier.\n")  # type: str

	for languageName in _languageNames:  # type: str
		desiredEntryPath = os.path.join(sourcePath, languageName, desiredEntryName) + ".txt"  # type: str

		if os.path.exists(desiredEntryPath):
			while True:
				overrideAnswer = input("The desired entry name already exists for at least one language\nExisting files will be overridden\nContinue? (Y/N)\n")  # type: str
				overrideAnswer = overrideAnswer.lower()

				if overrideAnswer == "y":
					break
				elif overrideAnswer == "n":
					return

				input("Invalid input")

			break
	
	keyDirectoryPath = os.path.join(sourcePath, _keyDirectoryName)  # type: str
	currentKeyPath = os.path.join(keyDirectoryPath, currentEntryName) + ".txt"  # type: str
	desiredKeyPath = os.path.join(keyDirectoryPath, desiredEntryName) + ".txt"  # type: str
	
	if not os.path.exists(keyDirectoryPath):
		os.makedirs(keyDirectoryPath)
	
	if not os.path.exists(currentKeyPath):
		with open(desiredKeyPath, "w+"):
			pass
	else:
		if os.path.exists(desiredKeyPath):
			os.remove(desiredKeyPath)

		os.rename(currentKeyPath, desiredKeyPath)
	
	for languageName in _languageNames:  # type: str
		languagePath = os.path.join(sourcePath, languageName)  # type: str

		if not os.path.exists(languagePath):
			os.makedirs(languagePath)

		currentEntryPath = os.path.join(languagePath, currentEntryName) + ".txt"  # type: str
		desiredEntryPath = os.path.join(languagePath, desiredEntryName) + ".txt"  # type: str

		if not os.path.exists(currentEntryPath):
			with open(desiredEntryPath, "w+"):
				pass
		else:
			if os.path.exists(desiredEntryPath):
				os.remove(desiredEntryPath)

			os.rename(currentEntryPath, desiredEntryPath)

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

if __name__ == "__main__":
	Run()
