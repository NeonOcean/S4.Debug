import collections
import numbers
import os
import typing

from NeonOcean.Debug import LoggingShared, This
from NeonOcean.Main import Debug, Language, LoadingShared, SettingsShared
from NeonOcean.Main.Data import Persistence
from NeonOcean.Main.Tools import Exceptions, Parse, Version
from NeonOcean.Main.UI import Settings as SettingsUI
from sims4.tuning import tunable

SettingsPath = os.path.join(This.Mod.PersistentPath, "Settings.json")  # type: str

_settings = None  # type: Persistence.Persistent
_allSettings = list()  # type: typing.List[typing.Type[Setting]]

class Setting(SettingsShared.SettingBase):
	IsSetting = False  # type: bool

	Key: str
	Type: typing.Type
	Default: typing.Any

	Name: Language.String
	Description: Language.String
	DescriptionInput = None  # type: typing.Optional[Language.String]

	DialogType = SettingsShared.DialogTypes.Input  # type: SettingsShared.DialogTypes
	Values = dict()  # type: typing.Dict[typing.Any, Language.String]
	InputRestriction = None  # type: typing.Optional[str]

	DocumentationPage: str

	def __init_subclass__ (cls, **kwargs):
		if cls.IsSetting:
			cls.SetDefaults()
			_allSettings.append(cls)

	@classmethod
	def SetDefaults (cls) -> None:
		cls.Name = Language.String(This.Mod.Namespace + ".System.Settings.Values." + cls.Key + ".Name")  # type: Language.String
		cls.Description = Language.String(This.Mod.Namespace + ".System.Settings.Values." + cls.Key + ".Description")  # type: Language.String
		cls.DocumentationPage = cls.Key.replace("_", "-").lower()  # type: str

	@classmethod
	def Setup (cls) -> None:
		Setup(cls.Key,
			  cls.Type,
			  cls.Default,
			  cls.Verify)

	@classmethod
	def isSetup (cls) -> bool:
		return isSetup(cls.Key)

	@classmethod
	def Get (cls):
		return Get(cls.Key)

	@classmethod
	def Set (cls, value: typing.Any, autoSave: bool = True, autoUpdate: bool = True) -> None:
		return Set(cls.Key, value, autoSave = autoSave, autoUpdate = autoUpdate)

	@classmethod
	def Reset (cls) -> None:
		Reset(cls.Key)

	@classmethod
	def Verify (cls, value: typing.Any, lastChangeVersion: Version.Version = None) -> typing.Any:
		return value

	@classmethod
	def GetInputTokens (cls) -> typing.Tuple[typing.Any, ...]:
		return tuple()

	@classmethod
	def IsActive (cls) -> bool:
		return True

	@classmethod
	def ShowDialog (cls):
		SettingsUI.ShowSettingDialog(cls, This.Mod)

	@classmethod
	def GetInputString (cls, inputValue: typing.Any) -> str:
		raise NotImplementedError()

	@classmethod
	def ParseInputString (cls, inputString: str) -> typing.Any:
		raise NotImplementedError()

class BooleanSetting(Setting):
	Type = bool

	DialogType = SettingsShared.DialogTypes.Choice  # type: SettingsShared.DialogTypes

	Values = {
		True: Language.String(This.Mod.Namespace + ".System.Settings.Boolean.True"),
		False: Language.String(This.Mod.Namespace + ".System.Settings.Boolean.False")
	}

	@classmethod
	def GetInputString (cls, inputValue: bool) -> str:
		if not isinstance(inputValue, bool):
			raise Exceptions.IncorrectTypeException(inputValue, "inputValue", (bool,))

		return str(inputValue)

	@classmethod
	def ParseInputString (cls, inputString: str) -> bool:
		if not isinstance(inputString, str):
			raise Exceptions.IncorrectTypeException(inputString, "inputString", (str,))

		return Parse.ParseBool(inputString)

class RealNumberSetting(Setting):
	Type = numbers.Real

	@classmethod
	def SetDefaults (cls) -> None:
		super().SetDefaults()
		cls.DescriptionInput = Language.String(This.Mod.Namespace + ".System.Settings.Values." + cls.Key + ".DescriptionInput")  # type: Language.String

	@classmethod
	def GetInputString (cls, inputValue: numbers.Real) -> str:
		if not isinstance(inputValue, numbers.Real):
			raise Exceptions.IncorrectTypeException(inputValue, "inputValue", (numbers.Real,))

		return str(inputValue)

	@classmethod
	def ParseInputString (cls, inputString: str) -> numbers.Real:
		if not isinstance(inputString, str):
			raise Exceptions.IncorrectTypeException(inputString, "inputString", (str,))

		parsedInput = Parse.ParseNumber(inputString)  # type: numbers.Real

		if not isinstance(parsedInput, numbers.Real):
			raise Exception("Input string cannot be converted to a real number.")

		return parsedInput

class LoggingModesSetting(Setting):
	Type = str

	DialogType = SettingsShared.DialogTypes.Choice  # type: SettingsShared.DialogTypes

	Values = {
		"Continuous": Language.String(This.Mod.Namespace + ".System.Settings.LoggingModes.Continuous"),
		"Burst": Language.String(This.Mod.Namespace + ".System.Settings.LoggingModes.Burst")
	}

	@classmethod
	def GetInputString (cls, inputValue: LoggingShared.LoggingModes) -> str:
		if not isinstance(inputValue, LoggingShared.LoggingModes):
			raise Exceptions.IncorrectTypeException(inputValue, "inputValue", (LoggingShared.LoggingModes,))

		return inputValue.name

	@classmethod
	def ParseInputString (cls, inputString: str) -> str:
		if not isinstance(inputString, str):
			raise Exceptions.IncorrectTypeException(inputString, "inputString", (str,))

		parsedInput = Parse.ParseEnum(inputString, LoggingShared.LoggingModes, ignoreCase = True)  # type: LoggingShared.LoggingModes
		return parsedInput.name

class LogLevelsSetting(Setting):
	Type = str

	DialogType = SettingsShared.DialogTypes.Choice  # type: SettingsShared.DialogTypes

	Values = {
		"Debug": Language.String(This.Mod.Namespace + ".System.Settings.LogLevels.Debug"),
		"Info": Language.String(This.Mod.Namespace + ".System.Settings.LogLevels.Info"),
		"Warning": Language.String(This.Mod.Namespace + ".System.Settings.LogLevels.Warning"),
		"Error": Language.String(This.Mod.Namespace + ".System.Settings.LogLevels.Error"),
		"Exception": Language.String(This.Mod.Namespace + ".System.Settings.LogLevels.Exception")
	}

	@classmethod
	def GetInputString (cls, inputValue: Debug.LogLevels) -> str:
		if not isinstance(inputValue, Debug.LogLevels):
			raise Exceptions.IncorrectTypeException(inputValue, "inputValue", (Debug.LogLevels,))

		return inputValue.name

	@classmethod
	def ParseInputString (cls, inputString: str) -> str:
		if not isinstance(inputString, str):
			raise Exceptions.IncorrectTypeException(inputString, "inputString", (str,))

		parsedInput = Parse.ParseEnum(inputString, Debug.LogLevels, ignoreCase = True)  # type: Debug.LogLevels
		return parsedInput.name

class Logging_Enabled(BooleanSetting):
	IsSetting = True  # type: bool

	Key = "Logging_Enabled"  # type: str
	Default = True  # type: bool

	@classmethod
	def Verify (cls, value: bool, lastChangeVersion: Version.Version = None) -> bool:
		if not isinstance(value, bool):
			raise Exceptions.IncorrectTypeException(value, "value", (bool,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

class Logging_Mode(LoggingModesSetting):
	IsSetting = True  # type: bool

	Key = "Logging_Mode"  # type: str
	Default = "Burst"  # type: str

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		Parse.ParseEnum(value, LoggingShared.LoggingModes)
		return value

class Write_Chronological(BooleanSetting):
	IsSetting = True  # type: bool

	Key = "Write_Chronological"  # type: str
	Default = True  # type: bool

	@classmethod
	def Verify (cls, value: bool, lastChangeVersion: Version.Version = None) -> bool:
		if not isinstance(value, bool):
			raise Exceptions.IncorrectTypeException(value, "value", (bool,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

class Write_Groups(BooleanSetting):
	IsSetting = True  # type: bool

	Key = "Write_Groups"  # type: str
	Default = False  # type: bool

	@classmethod
	def Verify (cls, value: bool, lastChangeVersion: Version.Version = None) -> bool:
		if not isinstance(value, bool):
			raise Exceptions.IncorrectTypeException(value, "value", (bool,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

class Burst_Level(LogLevelsSetting):
	IsSetting = True  # type: bool

	Key = "Burst_Level"  # type: str
	Default = "Warning"  # type: str

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		if not isinstance(value, str):
			raise Exceptions.IncorrectTypeException(value, "value", (str,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		Parse.ParseEnum(value, Debug.LogLevels)
		return value

class Burst_Interval(RealNumberSetting):
	IsSetting = True  # type: bool

	Key = "Burst_Interval"  # type: str
	Default = 20  # type: float

	Minimum = tunable.Tunable(description = "The minimum value for this setting.",
							  tunable_type = float,
							  default = 0)  # type: float

	Maximum = tunable.Tunable(description = "The maximum value for this setting.",
							  tunable_type = float,
							  default = 86400)  # type: float

	LowValueCutoff = tunable.Tunable(description = "Setting values less than the cutoff will be replaced with zero.",
									 tunable_type = float,
									 default = 0.0005)  # type: float

	@classmethod
	def Verify (cls, value: float, lastChangeVersion: Version.Version = None) -> float:
		if not isinstance(value, numbers.Real):
			raise Exceptions.IncorrectTypeException(value, "value", (numbers.Real,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		if not (cls.Minimum <= value <= cls.Maximum):
			raise ValueError("Value must be greater than '" + str(cls.Minimum) + "' and less than '" + str(cls.Maximum) + "'.")

		if value < cls.LowValueCutoff:
			return 0

		return value

class Continuous_Level(LogLevelsSetting):
	IsSetting = True  # type: bool

	Key = "Continuous_Level"  # type: str
	Default = "Warning"  # type: str

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		if not isinstance(value, str):
			raise Exceptions.IncorrectTypeException(value, "value", (str,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		Parse.ParseEnum(value, Debug.LogLevels)
		return value

def GetAllSettings () -> typing.List[typing.Type[Setting]]:
	return _allSettings

def Load () -> None:
	_settings.Load()

def Save () -> None:
	_settings.Save()

def Setup (key: str, valueType: type, default, verify: collections.Callable) -> None:
	_settings.Setup(key, valueType, default, verify)

def isSetup (key: str) -> bool:
	return _settings.isSetup(key)

def Get (key: str) -> typing.Any:
	return _settings.Get(key)

def Set (key: str, value: typing.Any, autoSave: bool = True, autoUpdate: bool = True) -> None:
	_settings.Set(key, value, autoSave = autoSave, autoUpdate = autoUpdate)

def Reset (key: str = None) -> None:
	_settings.Reset(key = key)

def Update () -> None:
	_settings.Update()

def RegisterUpdate (update: collections.Callable) -> None:
	_settings.RegisterUpdate(update)

def UnregisterUpdate (update: collections.Callable) -> None:
	_settings.UnregisterUpdate(update)

def _OnInitiate (cause: LoadingShared.LoadingCauses) -> None:
	global _settings

	if cause:
		pass

	if _settings is None:
		_settings = Persistence.Persistent(SettingsPath, This.Mod.Version, hostNamespace = This.Mod.Namespace)

		for setting in _allSettings:
			setting.Setup()

	Load()

def _OnUnload (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	try:
		Save()
	except Exception as e:
		Debug.Log("Failed to save settings.\n" + Debug.FormatException(e), This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__)

def _OnReset () -> None:
	Reset()

def _OnResetSettings () -> None:
	Reset()
