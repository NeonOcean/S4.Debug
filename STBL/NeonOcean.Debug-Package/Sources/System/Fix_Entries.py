import os
import random
import typing

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Fixing broken entries...")

	for languageName in _languageNames:  # type: str
		languagePath = os.path.join(sourcePath, languageName)  # type: str

		if not os.path.exists(languagePath):
			continue

		for entryName in os.listdir(languagePath):  # type: str
			entryName, entryExtension = os.path.splitext(entryName)  # type: str, str

			if entryExtension.lower() != ".txt":
				continue

			keyDirectoryPath = os.path.join(sourcePath, _keyDirectoryName)  # type: str
			keyPath = os.path.join(keyDirectoryPath, entryName) + ".txt"  # type: str

			if not os.path.exists(keyDirectoryPath):
				os.makedirs(keyDirectoryPath)

				with open(keyPath, "w+") as keyFile:
					keyFile.write(str(random.randint(1, 2 ** 32 - 1)))
			else:
				if not os.path.exists(keyPath):
					with open(keyPath, "w+") as keyFile:
						keyFile.write(str(random.randint(1, 2 ** 32 - 1)))

			for checkingLanguageName in _languageNames:
				checkingLanguagePath = os.path.join(sourcePath, checkingLanguageName)  # type: str

				if languageName == checkingLanguageName:
					continue

				checkingEntryPath = os.path.join(checkingLanguagePath, entryName) + ".txt"

				if not os.path.exists(checkingLanguagePath):
					os.makedirs(checkingLanguagePath)

					with open(checkingEntryPath, "w+"):
						pass
				else:
					if not os.path.exists(checkingEntryPath):
						with open(checkingEntryPath, "w+"):
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