import os
import platform
import re

from Mod_NeonOcean_S4_Debug.Tools import Registry

def _GetS4UserDataPath () -> str:
	if platform.system() == "Windows":
		import winreg

		pathPrefix = Registry.ReadRegistry(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders", "Personal")  # type: str

		# noinspection SpellCheckingInspection
		if pathPrefix.lower().startswith("%userprofile%"):
			# noinspection SpellCheckingInspection
			pathPrefix = re.sub(re.escape("%userprofile%"), re.escape(os.getenv("UserProfile")), pathPrefix, count = 1, flags = re.IGNORECASE)
	else:
		pathPrefix = os.path.join(os.path.expanduser('~'), "Documents")

	return os.path.join(os.path.normpath(pathPrefix), "Electronic Arts", "The Sims 4")

S4UserDataPath = _GetS4UserDataPath()  # type: str
S4ModsPath = os.path.join(S4UserDataPath, "Mods")  # type: str

AutomationPath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.normpath(__file__))))  # type: str
RootPath = os.path.dirname(AutomationPath)  # type: str
BuildPath = os.path.join(RootPath, "Build")  # type: str
LoosePath = os.path.join(RootPath, "Loose")  # type: str
InformationPath = os.path.join(RootPath, "Information")  # type: str
InformationBuildPath = os.path.join(InformationPath, "Build")  # type: str
InformationSourcesPath = os.path.join(InformationPath, "Sources")  # type: str
MiscPath = os.path.join(RootPath, "Misc")  # type: str
PackagePath = os.path.join(RootPath, "Packages")  # type: str

PublishingPath = os.path.join(RootPath, "Publishing")  # type: str
PublishingAdditionalInstallerPath = os.path.join(PublishingPath, "Additional", "Installer")  # type: str
PublishingDistributionInstallerPath = os.path.join(PublishingPath, "Distribution", "Installer")  # type: str
PublishingDistributionFilesPath = os.path.join(PublishingPath, "Distribution", "Files")  # type: str

PythonPath = os.path.join(RootPath, "Python")  # type: str
PythonBuildPath = os.path.join(PythonPath, "Build")  # type: str
PythonBuildLoosePath = os.path.join(PythonBuildPath, "Loose")  # type: str
PythonBuildArchivePath = os.path.join(PythonBuildPath, "Archive")  # type: str
