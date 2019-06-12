"""
This module allows you to print and change settings through console commands.
The S4 console will always change inputs to be lower case, so this module must be case-insensitive.
If more than one settings exist with the same name the first found will be used.
"""

from NeonOcean.Debug import Settings, This
from NeonOcean.Debug.Console import Command
from NeonOcean.Main import Debug, LoadingShared
from sims4 import commands

PrintNamesCommand = None  # type: Command.ConsoleCommand
ShowDialogCommand = None  # type: Command.ConsoleCommand

def _Setup () -> None:
	global PrintNamesCommand, ShowDialogCommand

	commandPrefix = This.Mod.Namespace.lower() + ".settings"

	PrintNamesCommand = Command.ConsoleCommand(_PrintNames, commandPrefix + ".print_names", showHelp = True)
	ShowDialogCommand = Command.ConsoleCommand(_ShowDialog, commandPrefix + ".show_dialog", showHelp = True, helpInput = "{ setting name }")

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	if cause:
		pass

	PrintNamesCommand.RegisterCommand()
	ShowDialogCommand.RegisterCommand()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	PrintNamesCommand.UnregisterCommand()
	ShowDialogCommand.UnregisterCommand()

def _PrintNames (_connection: int = None) -> None:
	try:
		allSettings = Settings.GetAllSettings()

		settingKeysString = ""

		for setting in allSettings:  # type: Settings.Setting
			if len(settingKeysString) == 0:
				settingKeysString += setting.Key
			else:
				settingKeysString += "\n" + setting.Key

		commands.cheat_output(settingKeysString + "\n", _connection)
	except:
		commands.cheat_output("Failed to print setting names.", _connection)
		Debug.Log("Failed to print setting names.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
		return

def _ShowDialog (key: str, _connection: int = None) -> None:
	try:
		allSettings = Settings.GetAllSettings()

		for setting in allSettings:  # type: Settings.Setting
			if setting.Key.lower() == key:
				setting.ShowDialog()
				return

	except:
		commands.cheat_output("Failed to show dialog for setting '" + key + "'.", _connection)
		Debug.Log("Failed to show dialog for setting '" + key + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
		return

	commands.cheat_output("Cannot find setting '" + key + "'.\n", _connection)

_Setup()
