import os
import shutil
import typing

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Duplicating entry...")
	entryName = input("Input the target localization entry's identifier\n")  # type: str

	duplicatePath = os.path.join(sourcePath, _duplicateDirectoryName)  # type: str

	for languageName in _languageNames:  # type: str
		duplicateEntryPath = os.path.join(duplicatePath, languageName, entryName) + ".txt"  # type: str

		if os.path.exists(duplicateEntryPath):
			while True:
				overrideAnswer = input("A duplicate of the same name already exists for at least one language\nExisting files will be overridden\nContinue? (Y/N)\n")  # type: str
				overrideAnswer = overrideAnswer.lower()

				if overrideAnswer == "y":
					break
				elif overrideAnswer == "n":
					return

				input("Invalid input")

			break

	for languageName in _languageNames:  # type: str
		languagePath = os.path.join(sourcePath, languageName)  # type: str
		duplicateLanguagePath = os.path.join(duplicatePath, languageName)  # type: str

		entryPath = os.path.join(languagePath, entryName) + ".txt"  # type: str
		duplicateEntryPath = os.path.join(duplicateLanguagePath, entryName) + ".txt"  # type: str

		if not os.path.exists(entryPath):
			continue

		if not os.path.exists(duplicateLanguagePath):
			os.makedirs(duplicateLanguagePath)

		shutil.copyfile(entryPath, duplicateEntryPath)

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

_duplicateDirectoryName = "Duplicates"  # type: str

if __name__ == "__main__":
	Run()
