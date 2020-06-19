"""
This module allows you to print and change settings through console commands.
The S4 console will always change inputs to be lower case, so this module must be case-insensitive.
If more than one settings exist with the same name the first found will be used.
"""

from NeonOcean.S4.Debug import Settings, This
from NeonOcean.S4.Debug.Console import Command
from NeonOcean.S4.Debug.Settings import Base as SettingsBase, List as SettingsList
from NeonOcean.S4.Main import Debug, LoadingShared
from sims4 import commands

PrintNamesCommand: Command.ConsoleCommand
ShowDialogCommand: Command.ConsoleCommand
ShowListCommand: Command.ConsoleCommand

def _Setup () -> None:
	global PrintNamesCommand, ShowDialogCommand, ShowListCommand

	commandPrefix = This.Mod.Namespace.lower() + ".settings"

	PrintNamesCommand = Command.ConsoleCommand(_PrintNames, commandPrefix + ".print_names", showHelp = True)
	ShowDialogCommand = Command.ConsoleCommand(_ShowDialog, commandPrefix + ".show_dialog", showHelp = True, helpInput = "{ setting name }")
	ShowListCommand = Command.ConsoleCommand(_ShowList, commandPrefix + ".show_list", showHelp = True)

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	if cause:
		pass

	PrintNamesCommand.RegisterCommand()
	ShowDialogCommand.RegisterCommand()
	ShowListCommand.RegisterCommand()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	PrintNamesCommand.UnregisterCommand()
	ShowDialogCommand.UnregisterCommand()
	ShowListCommand.UnregisterCommand()

def _PrintNames (_connection: int = None) -> None:
	try:
		allSettings = Settings.GetAllSettings()

		settingKeysString = ""

		for setting in allSettings:  # type: SettingsBase.Setting
			if len(settingKeysString) == 0:
				settingKeysString += setting.Key
			else:
				settingKeysString += "\n" + setting.Key

		commands.cheat_output(settingKeysString + "\n", _connection)
	except Exception:
		commands.cheat_output("Failed to print setting names.", _connection)
		Debug.Log("Failed to print setting names.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
		return

def _ShowDialog (key: str, _connection: int = None) -> None:
	try:
		allSettings = Settings.GetAllSettings()

		for setting in allSettings:  # type: SettingsBase.Setting
			if setting.Key.lower() == key:
				setting.ShowDialog()
				return

	except Exception:
		commands.cheat_output("Failed to show dialog for setting '" + key + "'.", _connection)
		Debug.Log("Failed to show dialog for setting '" + key + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
		return

	commands.cheat_output("Cannot find setting '" + key + "'.\n", _connection)


def _ShowList (_connection: int = None) -> None:
	try:
		SettingsList.ShowListDialog()
	except Exception:
		commands.cheat_output("Failed to show settings list dialog.", _connection)
		Debug.Log("Failed to show settings list dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
		return

_Setup()
