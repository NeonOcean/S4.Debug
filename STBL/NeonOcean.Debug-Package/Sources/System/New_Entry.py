import os
import random
import typing

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Creating new entry...")
	entryName = input("Input the new localization entry's identifier\n")  # type: str

	for languageName in _languageNames:  # type: str
		entryPath = os.path.join(sourcePath, languageName, entryName) + ".txt"  # type: str

		if os.path.exists(entryPath):
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
	keyPath = os.path.join(keyDirectoryPath, entryName) + ".txt"  # type: str
	
	if not os.path.exists(keyDirectoryPath):
		os.makedirs(keyDirectoryPath)

	with open(keyPath, "w+") as keyFile:
		keyFile.write(str(random.randint(1, 2 ** 32 - 1)))

	for languageName in _languageNames:  # type: str
		languagePath = os.path.join(sourcePath, languageName)  # type: str

		if not os.path.exists(languagePath):
			os.makedirs(languagePath)

		entryPath = os.path.join(languagePath, entryName) + ".txt"  # type: str

		with open(entryPath, "w+"):
			pass
			
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
