import os
import typing

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Deleting entry...")
	entryName = input("Input the targeted localization entry's identifier\n")  # type: str
	
	keyPath = os.path.join(sourcePath, _keyDirectoryName, entryName) + ".txt"  # type: str
	
	if os.path.exists(keyPath):
		os.remove(keyPath)
	
	for languageName in _languageNames:  # type: str
		entryPath = os.path.join(sourcePath, languageName, entryName) + ".txt"  # type: str

		if os.path.exists(entryPath):
			os.remove(entryPath)

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
