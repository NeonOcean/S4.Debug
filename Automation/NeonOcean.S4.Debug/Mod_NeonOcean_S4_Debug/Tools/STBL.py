import subprocess
import typing
from importlib import util

def CanBuildSTBL () -> bool:
	automationModule = util.find_spec("Automation")

	if automationModule is None:
		return False

	from Automation import Applications

	for applicationName, applicationFunction in BuildSTBLApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			return True

	return False

def BuildSTBL (buildDirectoryPath: str, sourceFilePath: str) -> None:
	from Automation import Applications

	for applicationName, applicationFunction in BuildSTBLApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			if applicationFunction(application, buildDirectoryPath, sourceFilePath):
				break

def _BuildSTBLSTBLBuilder (application, buildDirectoryPath: str, sourceFilePath: str) -> bool:
	stblBuilderExitCode = subprocess.call([application.ExecutablePath, "-t", buildDirectoryPath, "-p", sourceFilePath])  # type: int

	if stblBuilderExitCode != 0:
		raise Exception("STBLBuilder failed to complete a task.")

	return True

BuildSTBLApplications = {
	"STBLBuilder-v1.3.0": _BuildSTBLSTBLBuilder
}  # type: typing.Dict[str, typing.Callable]
