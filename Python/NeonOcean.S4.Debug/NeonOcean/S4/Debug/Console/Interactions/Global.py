from NeonOcean.S4.Debug import This
from NeonOcean.S4.Debug.Console import Command
from NeonOcean.S4.Main import Debug, LoadingShared, Websites
from NeonOcean.S4.Main.UI import Generic
from sims4 import commands

SupportNeonOceanCommand: Command.ConsoleCommand
VisitNeonOceanSiteCommand: Command.ConsoleCommand

def _Setup () -> None:
	global SupportNeonOceanCommand, VisitNeonOceanSiteCommand

	commandPrefix = This.Mod.Namespace.lower() + ".global"  # type: str

	# noinspection SpellCheckingInspection
	SupportNeonOceanCommand = Command.ConsoleCommand(_SupportNeonOcean, commandPrefix + ".support_neonocean")
	# noinspection SpellCheckingInspection
	VisitNeonOceanSiteCommand = Command.ConsoleCommand(_VisitNeonOceanSite, commandPrefix + ".visit_neonocean_site")

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	if cause:
		pass

	SupportNeonOceanCommand.RegisterCommand()
	VisitNeonOceanSiteCommand.RegisterCommand()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	SupportNeonOceanCommand.UnregisterCommand()
	VisitNeonOceanSiteCommand.UnregisterCommand()

def _SupportNeonOcean (_connection: int = None) -> None:
	try:
		Generic.ShowOpenBrowserDialog(Websites.GetNOSupportURL())
	except:
		output = commands.CheatOutput(_connection)
		output("Failed to show the support site with the open browser dialog.")

		Debug.Log("Failed to show the support site with the open browser dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

def _VisitNeonOceanSite (_connection: int = None) -> None:
	try:
		Generic.ShowOpenBrowserDialog(Websites.GetNOMainURL())
	except:
		output = commands.CheatOutput(_connection)
		output("Failed to show the NeonOcean site with the open browser dialog.")

		Debug.Log("Failed to show the NeonOcean site with the open browser dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

_Setup()