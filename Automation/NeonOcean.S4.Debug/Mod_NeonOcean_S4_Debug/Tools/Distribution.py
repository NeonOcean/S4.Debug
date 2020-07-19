import glob
import os
import shutil
import subprocess
import typing
from distutils import dir_util
from importlib import util

def CanBuildInstaller () -> bool:
	automationModule = util.find_spec("Automation")

	if automationModule is None:
		return False

	from Automation import Applications

	for applicationName, applicationFunction in BuildInstallerApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			return True

	return False

def BuildInstaller (buildDirectoryPath: str, buildExecutableName: str) -> None:
	"""
	:param buildDirectoryPath:
	:param buildExecutableName: Exclude the extension
	:return:
	"""

	from Automation import Applications

	for applicationName, applicationFunction in BuildInstallerApplications.items():  # type: str, typing.Callable
		application = Applications.GetApplication(applicationName)  # type: Applications.Application

		if application.ExecutablePath is not None:
			if applicationFunction(application,
								   buildDirectoryPath,
								   buildExecutableName):
				break

def CanSendToInstaller () -> bool:
	automationModule = util.find_spec("Automation")

	if automationModule is None:
		return False

	return True

def SendToNOModInstaller (archiveFilePath: str, additionalDirectoryPath: str) -> None:
	from Automation import Applications

	installerApplication = Applications.GetApplication("NOModInstaller-v1.3.0")  # type: Applications.Application
	installerSourceDirectoryPath = os.path.join(installerApplication.PointerDirectoryPath, os.path.dirname(installerApplication.Special))  # type: str
	installerModDirectoryPath = os.path.join(installerSourceDirectoryPath, "Mod")

	files = glob.glob(installerModDirectoryPath + os.path.sep + "*")

	for file in files:  # type: str
		if os.path.isdir(file):
			shutil.rmtree(file)
		else:
			os.remove(file)

	shutil.copy(archiveFilePath, os.path.join(installerModDirectoryPath, "Files.zip"))
	dir_util.copy_tree(additionalDirectoryPath, installerSourceDirectoryPath, )

def _BuildInstallerMSBuild (application, buildDirectoryPath: str, buildExecutableName: str) -> None:
	from Automation import Applications

	installerApplication = Applications.GetApplication("NOModInstaller-v1.3.0")  # type: Applications.Application
	sourceProjectFilePath = os.path.join(installerApplication.PointerDirectoryPath, installerApplication.Special)  # type: str

	msBuildExitCode = subprocess.call([application.ExecutablePath, sourceProjectFilePath, "-p:Configuration=Release;OutputPath=" + buildDirectoryPath + ";AssemblyName=" + buildExecutableName])  # type: int

	if msBuildExitCode != 0:
		raise Exception("MSBuild failed to complete a task.")

BuildInstallerApplications = {
	"MSBuild": _BuildInstallerMSBuild
}  # type: typing.Dict[str, typing.Callable]
