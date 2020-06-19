import typing

from NeonOcean.S4.Debug import This
from NeonOcean.S4.Main import Debug, LoadingShared
from NeonOcean.S4.Main.Tools import Exceptions
from sims4 import commands

# noinspection PyTypeChecker
HelpCommand = None  # type: ConsoleCommand

_consoleCommands = list()  # type: typing.List[ConsoleCommand]

class ConsoleCommand:
	def __init__ (self, commandFunction: typing.Callable, *alias, showHelp: bool = False, helpAliasPosition: int = 0, helpInput: typing.Optional[str] = None):
		if not isinstance(commandFunction, typing.Callable):
			raise Exceptions.IncorrectTypeException(commandFunction, "commandFunction", ("Callable",))

		if not isinstance(alias, tuple):
			raise Exceptions.IncorrectTypeException(alias, "alias", (tuple,))

		if len(alias) == 0:
			raise Exception("Console command has not alias.")

		for aliasIndex in range(len(alias)):  # type: int
			if not isinstance(alias[aliasIndex], str):
				raise Exceptions.IncorrectTypeException(alias, "alias[%d]" % aliasIndex, (str,))

		if not isinstance(showHelp, bool):
			raise Exceptions.IncorrectTypeException(showHelp, "showHelp", (bool,))

		if not isinstance(helpAliasPosition, int):
			raise Exceptions.IncorrectTypeException(helpAliasPosition, "helpAliasPosition", (int,))

		if helpAliasPosition < 0 or helpAliasPosition > (len(alias) - 1):
			raise Exception("'helpAliasPosition' is out of bounds.")

		if not isinstance(helpInput, str) and helpInput is not None:
			raise Exceptions.IncorrectTypeException(helpInput, "helpInput", (str, "None"))

		self.CommandFunction = commandFunction  # type: typing.Callable
		self.Alias = alias  # type: typing.Tuple[str, ...]

		self.ShowHelp = showHelp  # type: bool

		self.HelpAliasPosition = helpAliasPosition  # type: int
		self.HelpInput = helpInput  # type: typing.Optional[str]

		_consoleCommands.append(self)

	def RegisterCommand (self):
		for alias in self.Alias:  # type: str
			commands.Command(alias, command_type = commands.CommandType.Live)(self.CommandFunction)

	def UnregisterCommand (self):
		for alias in self.Alias:  # type: str
			commands.unregister(alias)

def _Setup () -> None:
	global HelpCommand

	commandPrefix = This.Mod.Namespace.lower()

	HelpCommand = ConsoleCommand(_Help, commandPrefix + ".help", showHelp = True)

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	if cause:
		pass

	HelpCommand.RegisterCommand()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	HelpCommand.UnregisterCommand()

def _Help (_connection: int = None) -> None:
	try:
		helpText = ""

		for consoleCommand in _consoleCommands:  # type: ConsoleCommand
			if not consoleCommand.ShowHelp:
				continue

			if len(helpText) != 0:
				helpText += "\n"

			if consoleCommand.HelpInput is not None:
				helpText += consoleCommand.Alias[consoleCommand.HelpAliasPosition] + " " + consoleCommand.HelpInput
			else:
				helpText += consoleCommand.Alias[consoleCommand.HelpAliasPosition]

		commands.cheat_output(helpText + "\n", _connection)
	except Exception:
		output = commands.CheatOutput(_connection)
		output("Failed to show help information.")

		Debug.Log("Failed to show help information.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

_Setup()
