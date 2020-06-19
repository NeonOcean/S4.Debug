import datetime
import json
import os
from importlib import util

def CanBuildInformation () -> bool:
	automationModule = util.find_spec("Automation")

	if automationModule is None:
		return False

	return True

def BuildInformation (informationSourceFilePath: str, informationBuildFilePath: str) -> None:
	from Automation import S4

	with open(informationSourceFilePath) as informationSourceFile:
		information = json.JSONDecoder().decode(informationSourceFile.read())  # type: dict

	information["BuildDate"] = datetime.datetime.now().date().isoformat()
	information["BuildGameVersion"] = S4.Version

	informationBuildDirectoryPath = os.path.dirname(informationBuildFilePath)  # type: str

	if not os.path.exists(informationBuildDirectoryPath):
		os.makedirs(informationBuildDirectoryPath)

	with open(informationBuildFilePath, "w+") as informationBuildFile:
		informationBuildFile.write(json.JSONEncoder(indent = "\t").encode(information))
