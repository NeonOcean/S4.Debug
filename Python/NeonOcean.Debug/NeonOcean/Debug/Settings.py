import math
import numbers
import os
import typing

from NeonOcean.Debug import This
from NeonOcean.Main import Debug, Language, LoadingShared, SettingsShared, Websites
from NeonOcean.Main.Data import Persistence
from NeonOcean.Main.Tools import Exceptions, Parse, Version
from NeonOcean.Main.UI import Settings as SettingsUI
from sims4 import localization
from sims4.tuning import tunable
from ui import ui_dialog

SettingsPath = os.path.join(This.Mod.PersistentPath, "Settings.json")  # type: str

_settings = None  # type: Persistence.PersistentFile
_allSettings = list()  # type: typing.List[typing.Type[Setting]]

class Setting(SettingsShared.SettingBase):
	IsSetting = False  # type: bool

	Key: str
	Type: typing.Type
	Default: typing.Any

	Dialog: typing.Type[SettingsUI.SettingDialog]

	def __init_subclass__ (cls, **kwargs):
		super().OnInitializeSubclass()

		if cls.IsSetting:
			cls.SetDefault()
			_allSettings.append(cls)

	@classmethod
	def Setup (cls) -> None:
		_Setup(cls.Key,
			   cls.Type,
			   cls.Default,
			   cls.Verify)

	@classmethod
	def IsSetup (cls) -> bool:
		return _isSetup(cls.Key)

	@classmethod
	def Get (cls):
		return _Get(cls.Key)

	@classmethod
	def Set (cls, value: typing.Any, autoSave: bool = True, autoUpdate: bool = True) -> None:
		return _Set(cls.Key, value, autoSave = autoSave, autoUpdate = autoUpdate)

	@classmethod
	def Reset (cls) -> None:
		_Reset(key = cls.Key)

	@classmethod
	def Verify (cls, value: typing.Any, lastChangeVersion: Version.Version = None) -> typing.Any:
		return value

	@classmethod
	def IsActive (cls) -> bool:
		return True

	@classmethod
	def ShowDialog (cls):
		if not hasattr(cls, "Dialog"):
			return

		if cls.Dialog is None:
			return

		settingWrapper = SettingsUI.SettingStandardWrapper(cls)  # type: SettingsUI.SettingStandardWrapper
		cls.Dialog.ShowDialog(settingWrapper)

	@classmethod
	def GetName (cls) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings.Values." + cls.Key + ".Name")

	@classmethod
	def _OnLoaded (cls) -> None:
		pass

class BooleanSetting(Setting):
	Type = bool

	class Dialog(SettingsUI.StandardDialog):
		HostNamespace = This.Mod.Namespace  # type: str
		HostName = This.Mod.Name  # type: str

		Values = [False, True]  # type: typing.List[bool]

		@classmethod
		def GetTitleText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return setting.Setting.GetName()

		@classmethod
		def GetDescriptionText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings.Values." + setting.Key + ".Description")

		@classmethod
		def GetDefaultText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings.Boolean." + str(setting.Setting.Default))

		@classmethod
		def GetDocumentationURL (cls, setting: SettingsUI.SettingStandardWrapper) -> typing.Optional[str]:
			return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

		@classmethod
		def _CreateButtons (cls,
							setting: SettingsUI.SettingStandardWrapper,
							currentValue: typing.Any,
							showDialogArguments: typing.Dict[str, typing.Any],
							returnCallback: typing.Callable[[], None] = None,
							*args, **kwargs):

			buttons = super()._CreateButtons(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[SettingsUI.DialogButton]

			for valueIndex in range(len(cls.Values)):  # type: int
				def CreateValueButtonCallback (value: typing.Any) -> typing.Callable:

					# noinspection PyUnusedLocal
					def ValueButtonCallback (dialog: ui_dialog.UiDialog) -> None:
						cls._ShowDialogInternal(setting, value, showDialogArguments, returnCallback = returnCallback)

					return ValueButtonCallback

				valueButtonArguments = {
					"responseID": 50000 + valueIndex + -1,
					"sortOrder": -(500 + valueIndex + -1),
					"callback": CreateValueButtonCallback(cls.Values[valueIndex]),
					"text": Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings.Boolean." + str(cls.Values[valueIndex])),
				}

				if currentValue == cls.Values[valueIndex]:
					valueButtonArguments["selected"] = True

				valueButton = SettingsUI.ChoiceDialogButton(**valueButtonArguments)
				buttons.append(valueButton)

			return buttons

	@classmethod
	def Verify (cls, value: bool, lastChangeVersion: Version.Version = None) -> bool:
		if not isinstance(value, bool):
			raise Exceptions.IncorrectTypeException(value, "value", (bool,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

class RealNumberSetting(Setting):
	Type = numbers.Real

	class Dialog(SettingsUI.InputDialog):
		HostNamespace = This.Mod.Namespace  # type: str
		HostName = This.Mod.Name  # type: str

		@classmethod
		def GetTitleText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return setting.Setting.GetName()

		@classmethod
		def GetDescriptionText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings.Values." + setting.Key + ".Description")

		@classmethod
		def GetDefaultText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return Language.CreateLocalizationString(str(setting.Setting.Default))

		@classmethod
		def GetDocumentationURL (cls, setting: SettingsUI.SettingStandardWrapper) -> typing.Optional[str]:
			return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

		@classmethod
		def _ParseValueString (cls, valueString: str) -> numbers.Real:
			if not isinstance(valueString, str):
				raise Exceptions.IncorrectTypeException(valueString, "valueString", (str,))

			parsedInput = Parse.ParseNumber(valueString)  # type: numbers.Real

			if not isinstance(parsedInput, numbers.Real):
				raise Exception("Input string cannot be converted to a real number.")

			return parsedInput

		@classmethod
		def _ValueToString (cls, value: numbers.Real) -> str:
			if not isinstance(value, numbers.Real):
				raise Exceptions.IncorrectTypeException(value, "value", (numbers.Real,))

			return str(value)

	@classmethod
	def Verify (cls, value: float, lastChangeVersion: Version.Version = None) -> float:
		if not isinstance(value, numbers.Real):
			raise Exceptions.IncorrectTypeException(value, "value", (numbers.Real,))

		if math.isnan(value):
			raise ValueError("Value cannot be 'not a number'.")

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

class EnumSetting(Setting):
	Type = str

	class Dialog(SettingsUI.StandardDialog):
		HostNamespace = This.Mod.Namespace  # type: str
		HostName = This.Mod.Name  # type: str

		EnumName: str  # type: str
		Values: typing.List[str]

		@classmethod
		def GetTitleText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return setting.Setting.GetName()

		@classmethod
		def GetDescriptionText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings.Values." + setting.Key + ".Description")

		@classmethod
		def GetDefaultText (cls, setting: SettingsUI.SettingStandardWrapper) -> localization.LocalizedString:
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings." + cls.EnumName + "." + str(setting.Setting.Default))

		@classmethod
		def GetDocumentationURL (cls, setting: SettingsUI.SettingStandardWrapper) -> typing.Optional[str]:
			return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

		@classmethod
		def _CreateButtons (cls,
							setting: SettingsUI.SettingStandardWrapper,
							currentValue: typing.Any,
							showDialogArguments: typing.Dict[str, typing.Any],
							returnCallback: typing.Callable[[], None] = None,
							*args, **kwargs):

			buttons = super()._CreateButtons(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[SettingsUI.DialogButton]

			for valueIndex in range(len(cls.Values)):  # type: int
				def CreateValueButtonCallback (value: typing.Any) -> typing.Callable:

					# noinspection PyUnusedLocal
					def ValueButtonCallback (dialog: ui_dialog.UiDialog) -> None:
						cls._ShowDialogInternal(setting, value, showDialogArguments = showDialogArguments, returnCallback = returnCallback)

					return ValueButtonCallback

				valueButtonArguments = {
					"responseID": 50000 + valueIndex + -1,
					"sortOrder": -(500 + valueIndex + -1),
					"callback": CreateValueButtonCallback(cls.Values[valueIndex]),
					"text": Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Settings." + cls.EnumName + "." + cls.Values[valueIndex]),
				}

				if currentValue == cls.Values[valueIndex]:
					valueButtonArguments["selected"] = True

				valueButton = SettingsUI.ChoiceDialogButton(**valueButtonArguments)
				buttons.append(valueButton)

			return buttons

class LogLevelsSetting(EnumSetting):
	class Dialog(EnumSetting.Dialog):
		EnumName = "LogLevels"  # type: str
		Values = []  # type: typing.List[str]

		@classmethod
		def OnInitializeSubclass (cls):
			super().OnInitializeSubclass()

			for value in Debug.LogLevels.values:  # type: Debug.LogLevels
				cls.Values.append(value.name)

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		if not isinstance(value, str):
			raise Exceptions.IncorrectTypeException(value, "value", (str,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		Parse.ParseEnum(value, Debug.LogLevels)
		return value

class LoggingEnabled(BooleanSetting):
	IsSetting = True  # type: bool

	Key = "Logging_Enabled"  # type: str
	Default = True  # type: bool

class WriteChronological(BooleanSetting):
	IsSetting = True  # type: bool

	Key = "Write_Chronological"  # type: str
	Default = True  # type: bool

class WriteGroups(BooleanSetting):
	IsSetting = True  # type: bool

	Key = "Write_Groups"  # type: str
	Default = False  # type: bool

class LogLevel(LogLevelsSetting):
	IsSetting = True  # type: bool

	Key = "Log_Level"  # type: str
	Default = "Warning"  # type: str

class LogInterval(RealNumberSetting):
	IsSetting = True  # type: bool

	Key = "Log_Interval"  # type: str
	Default = 20  # type: float

	Minimum = tunable.Tunable(description = "The minimum value for this setting.",
							  tunable_type = float,
							  default = 0)  # type: float

	Maximum = tunable.Tunable(description = "The maximum value for this setting.",
							  tunable_type = float,
							  default = 86400)  # type: float

	LowValueCutoff = tunable.Tunable(description = "Setting values less than the cutoff will be replaced with zero.",
									 tunable_type = float,
									 default = 0.05)  # type: float

	@classmethod
	def Verify (cls, value: float, lastChangeVersion: Version.Version = None) -> float:
		value = super().Verify(value, lastChangeVersion = lastChangeVersion)

		if not (cls.Minimum <= value <= cls.Maximum):
			raise ValueError("Value must be greater than '" + str(cls.Minimum) + "' and less than '" + str(cls.Maximum) + "'.")

		if value < cls.LowValueCutoff:
			return 0

		return value

def GetAllSettings () -> typing.List[typing.Type[Setting]]:
	return list(_allSettings)

def Load () -> None:
	_settings.Load()

def Save () -> None:
	_settings.Save()

def Update () -> None:
	_settings.Update()

def RegisterUpdate (update: typing.Callable) -> None:
	_settings.RegisterUpdate(update)

def UnregisterUpdate (update: typing.Callable) -> None:
	_settings.UnregisterUpdate(update)

def RegisterLoadCallback (callback: typing.Callable) -> None:
	_settings.RegisterLoadCallback(callback)

def UnregisterLoadCallback (callback: typing.Callable) -> None:
	_settings.UnregisterLoadCallback(callback)

def _OnInitiate (cause: LoadingShared.LoadingCauses) -> None:
	global _settings

	if cause:
		pass

	if _settings is None:
		_settings = Persistence.PersistentFile(SettingsPath, This.Mod.Version, hostNamespace = This.Mod.Namespace, alwaysSaveValues = True)

		for setting in _allSettings:
			setting.Setup()

		RegisterLoadCallback(_LoadCallback)

	Load()

def _OnUnload (cause: LoadingShared.UnloadingCauses) -> None:
	if cause:
		pass

	try:
		Save()
	except Exception:
		Debug.Log("Failed to save settings.", This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__)

def _OnReset () -> None:
	for setting in GetAllSettings():  # type: Setting
		setting.Reset()

def _OnResetSettings () -> None:
	for setting in GetAllSettings():  # type: Setting
		setting.Reset()

def _Setup (key: str, valueType: type, default, verify: typing.Callable) -> None:
	_settings.Setup(key, valueType, default, verify)

def _isSetup (key: str) -> bool:
	return _settings.IsSetup(key)

def _Get (key: str) -> typing.Any:
	return _settings.Get(key)

def _Set (key: str, value: typing.Any, autoSave: bool = True, autoUpdate: bool = True) -> None:
	_settings.Set(key, value, autoSave = autoSave, autoUpdate = autoUpdate)

def _Reset (key: str = None) -> None:
	_settings.Reset(key = key)

def _LoadCallback () -> None:
	for setting in _allSettings:  # type: Setting
		try:
			setting._OnLoaded()
		except Exception:
			Debug.Log("Failed to call the on loaded event for the setting '" + setting.Key + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
