import os
import random

def Run ():
	sourcePath = os.path.dirname(__file__)  # type: str

	print("Generating a new string key...")
	entryName = input("Input the targeted localization entry's identifier\n")  # type: str
	
	keyDirectoryPath = os.path.join(sourcePath, _keyDirectoryName)  # type: str
	keyPath = os.path.join(keyDirectoryPath, entryName) + ".txt"  # type: str
	
	if not os.path.exists(keyDirectoryPath):
		os.makedirs(keyDirectoryPath)

	with open(keyPath, "w+") as keyFile:
		keyFile.write(str(random.randint(1, 2 ** 32 - 1)))

_keyDirectoryName = "Keys"  # type: str
		
if __name__ == "__main__":
	Run()