from NeonOcean.S4.Debug import This
from NeonOcean.S4.Debug.Console import Command
from NeonOcean.S4.Main import Debug, LoadingShared, Resetting
from sims4 import commands

ResetCommand: Command.ConsoleCommand

def _Setup () -> None:
	global ResetCommand

	commandPrefix = This.Mod.Namespace.lower()

	ResetCommand = Command.ConsoleCommand(_Reset, commandPrefix + ".reset")

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	if cause:
		pass

	ResetCommand.RegisterCommand()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	ResetCommand.UnregisterCommand()

def _Reset (_connection: int = None) -> None:
	try:
		Resetting.ShowResetDialog(This.Mod)
	except Exception as e:
		output = commands.CheatOutput(_connection)
		output("Failed to show reset dialog.")

		Debug.Log("Failed to show reset dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)

_Setup()
