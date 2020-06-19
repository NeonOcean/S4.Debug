import types
import typing

from NeonOcean.S4.Debug.Settings import Base as SettingsBase, Dialogs as SettingsDialogs, Types as SettingsTypes
from NeonOcean.S4.Main.Tools import Events, Version

class LoggingEnabled(SettingsTypes.BooleanYesNoDialogSetting):
	IsSetting = True  # type: bool

	Key = "Logging_Enabled"  # type: str
	Default = True  # type: bool

class WriteChronological(SettingsTypes.BooleanYesNoDialogSetting):
	IsSetting = True  # type: bool

	Key = "Write_Chronological"  # type: str
	Default = True  # type: bool

class WriteGroups(SettingsTypes.BooleanYesNoDialogSetting):
	IsSetting = True  # type: bool

	Key = "Write_Groups"  # type: str
	Default = False  # type: bool

class LogLevel(SettingsTypes.LogLevelsDialogSetting):
	IsSetting = True  # type: bool

	Key = "Log_Level"  # type: str
	Default = "Warning"  # type: str

class LogInterval(SettingsTypes.TimeSecondsDialogSetting):
	IsSetting = True  # type: bool

	Key = "Log_Interval"  # type: str
	Default = 20  # type: float

	Minimum = 0  # type: float
	Maximum = 86400  # type: float
	LowValueCutoff = 0.05  # type: float

	@classmethod
	def Verify (cls, value: float, lastChangeVersion: Version.Version = None) -> float:
		value = super().Verify(value, lastChangeVersion = lastChangeVersion)

		if not (cls.Minimum <= value <= cls.Maximum):
			raise ValueError("Value must be greater than '" + str(cls.Minimum) + "' and less than '" + str(cls.Maximum) + "'.")

		if value < cls.LowValueCutoff:
			return 0

		return value

class LogSizeLimit(SettingsTypes.LogSizeLimitDialogSetting):
	IsSetting = True  # type: bool

	Key = "Log_Size_Limit"  # type: str
	Default = 5  # type: float

def GetSettingsFilePath () -> str:
	return SettingsBase.SettingsFilePath

def GetAllSettings () -> typing.List[typing.Type[SettingsBase.Setting]]:
	return list(SettingsBase.AllSettings)

def Load () -> None:
	SettingsBase.Load()

def Save () -> None:
	SettingsBase.Save()

def Update () -> None:
	SettingsBase.Update()

def RegisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, SettingsBase.UpdateEventArguments], None]) -> None:
	SettingsBase.RegisterOnUpdateCallback(updateCallback)

def UnregisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, SettingsBase.UpdateEventArguments], None]) -> None:
	SettingsBase.UnregisterOnUpdateCallback(updateCallback)

def RegisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	SettingsBase.RegisterOnLoadCallback(loadCallback)

def UnregisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	SettingsBase.UnregisterOnLoadCallback(loadCallback)
