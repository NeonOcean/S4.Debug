import subprocess
import typing
from importlib import util

def CanBuildPackage () -> bool:
	automationModule = util.find_spec("Automation")

	if automationModule is None:
		return False

	from Automation import Applications

	for applicationName, applicationFunction in BuildPackageApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			return True

	return False

def BuildPackage (buildFilePath: str, baseFilePath: typing.Optional[str] = None, addingFilePaths: typing.Optional[typing.List[str]] = None) -> None:
	from Automation import Applications

	for applicationName, applicationFunction in BuildPackageApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			if applicationFunction(application,
								   buildFilePath,
								   baseFilePath = baseFilePath,
								   addingFilePaths = addingFilePaths):
				break

def _BuildPackagePackageBuilder (application, buildFilePath: str, baseFilePath: typing.Optional[str] = None, addingFilePaths: typing.Optional[typing.List[str]] = None) -> None:
	packageBuilderArguments = [application.ExecutablePath, "-t", buildFilePath]

	if baseFilePath is not None:
		packageBuilderArguments.append("-b")
		packageBuilderArguments.append(baseFilePath)

	if addingFilePaths is not None and len(addingFilePaths) != 0:
		sourceFilesCommand = ""  # type: str

		for sourceFilePath in addingFilePaths:  # type: str
			if sourceFilesCommand == "":
				sourceFilesCommand = sourceFilePath
			else:
				sourceFilesCommand += ";" + sourceFilePath

		packageBuilderArguments.append("-s")
		packageBuilderArguments.append(sourceFilesCommand)

	packageBuilderExitCode = subprocess.call(packageBuilderArguments)  # type: int

	if packageBuilderExitCode != 0:
		raise Exception("PackageBuilder failed to complete a task.")

BuildPackageApplications = { "PackageBuilder-v1.1.0": _BuildPackagePackageBuilder }  # type: typing.Dict[str, typing.Callable]
