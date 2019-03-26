import os
import typing

def BuildManifest (buildFileRelativePath: str, targetDirectoryPath: str) -> bool:
	manifest = list()  # type: typing.List[str]

	for directoryRoot, directoryNames, fileNames in os.walk(targetDirectoryPath):  # type: str, typing.List[str], typing.List[str]
		relativeDirectoryRoot = directoryRoot.replace(targetDirectoryPath, "").lstrip(os.path.sep + os.path.altsep)  # type: str

		for fileName in fileNames:
			manifest.append(os.path.join(relativeDirectoryRoot, fileName))

	buildFileRelativePathLower = buildFileRelativePath.lower()  # type: str
	buildFileDuplicate = False  # type: bool

	for manifestPath in manifest:  # type: str
		manifestPathLower = manifestPath.lower()

		if buildFileRelativePathLower == manifestPathLower:
			buildFileDuplicate = True

	if not buildFileDuplicate:
		manifest.append(buildFileRelativePath)

	manifest.sort(key = str.lower)

	buildFilePath = os.path.join(targetDirectoryPath, buildFileRelativePath)

	with open(buildFilePath, mode = "+w") as buildFile:
		for manifestIndex in range(len(manifest)):  # type: int
			if manifestIndex == 0:
				buildFile.write(manifest[manifestIndex])
			else:
				buildFile.write("\n" + manifest[manifestIndex])

	return True
