import os
import py_compile
import shutil
import typing
import zipfile

def CanBuildPython () -> bool:
	return True

def BuildPython (buildLoosePath: str, buildArchivePath: str, sourceRootPath: str, sourceTargetPath: str, excludedFiles: typing.List[str]) -> bool:
	if os.path.exists(buildLoosePath):
		shutil.rmtree(buildLoosePath)

	os.makedirs(buildLoosePath)

	for i in _GetUncompiledFiles(sourceTargetPath, excludedFiles):
		destination = i.replace(sourceRootPath, buildLoosePath) + "c"  # type: str

		if not os.path.exists(os.path.dirname(destination)):
			os.makedirs(os.path.dirname(destination))

		py_compile.compile(i, cfile = destination)

	_ZipDirectory(buildLoosePath, buildArchivePath)

	return True

def _GetUncompiledFiles (path: str, excludedFiles: typing.List[str]) -> typing.List[str]:
	excludedFilesLower = list(excludedFiles)  # type: typing.List[str]

	for excludedFileLowerIndex in range(0, len(excludedFilesLower)):
		excludedFilesLower[excludedFileLowerIndex] = excludedFilesLower[excludedFileLowerIndex].lower()

	uncompiledFiles = list()  # type: typing.List[str]

	for directoryRoot, directoryNames, fileNames in os.walk(path):  # type: str, typing.List[str], typing.List[str]
		for fileName in fileNames:
			filePath = os.path.join(directoryRoot, fileName)  # type: str
			if os.path.splitext(fileName)[1].casefold() == ".py" and not filePath.lower() in excludedFilesLower:
				uncompiledFiles.append(filePath)

	return uncompiledFiles

def _ZipDirectory (root: str, destination: str) -> None:
	if not os.path.exists(os.path.dirname(destination)):
		os.makedirs(os.path.dirname(destination))

	archive = zipfile.ZipFile(destination, "w")  # type: zipfile.ZipFile

	for directoryRoot, directoryNames, fileNames in os.walk(root):  # type: str, typing.List[str], typing.List[str]
		if directoryRoot != root:
			archive.write(directoryRoot, arcname = directoryRoot.replace(root + os.path.sep, ""))

		for i in fileNames:
			path = os.path.join(directoryRoot, i)  # type: str
			archive.write(path, arcname = path.replace(root + os.path.sep, ""))

	archive.close()
