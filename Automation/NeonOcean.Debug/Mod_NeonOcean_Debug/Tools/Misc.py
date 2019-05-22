import os
from importlib import util

def CanBuildMarkdown () -> bool:
	markdownModule = util.find_spec("markdown")

	if markdownModule is None:
		return False

	return True

def BuildMarkdown (buildFilePath: str, targetFilePath: str) -> None:
	import markdown

	with open(targetFilePath) as targetFile:
		target = targetFile.read()  # type: str

	buildDirectoryPath = os.path.split(buildFilePath)[0]  # type: str

	if not os.path.exists(buildDirectoryPath):
		os.makedirs(buildDirectoryPath)

	with open(buildFilePath, "w+") as buildFile:
		buildFile.write(markdown.markdown(target, output_format = 'html5'))