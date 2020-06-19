from __future__ import annotations

import numbers
import typing

from NeonOcean.S4.Debug import This
from NeonOcean.S4.Debug.Settings import Base as SettingsBase, Dialogs as SettingsDialogs
from NeonOcean.S4.Main import Debug, Language
from NeonOcean.S4.Main.Tools import Exceptions, Numbers as ToolsNumbers, Parse, Version
from sims4 import localization

class BooleanYesNoSetting(SettingsBase.Setting):
	Type = bool

	@classmethod
	def Verify (cls, value: bool, lastChangeVersion: Version.Version = None) -> bool:
		if not isinstance(value, bool):
			raise Exceptions.IncorrectTypeException(value, "value", (bool,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

	@classmethod
	def GetValueText (cls, value: bool) -> localization.LocalizedString:
		if not isinstance(value, bool):
			raise Exceptions.IncorrectTypeException(value, "value", (bool,))

		valueString = str(value)  # type: str
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Boolean.Yes_No." + valueString, fallbackText = valueString)

class BooleanYesNoDialogSetting(BooleanYesNoSetting):
	Dialog = SettingsDialogs.BooleanYesNoDialog

class RealNumberSetting(SettingsBase.Setting):
	Type = numbers.Real

	@classmethod
	def Verify (cls, value: typing.Union[float, int], lastChangeVersion: Version.Version = None) -> typing.Union[float, int]:
		cls._TypeCheckValue(value)

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

	@classmethod
	def GetValueText (cls, value: typing.Union[float, int]) -> localization.LocalizedString:
		cls._TypeCheckValue(value)

		valueString = str(value)  # type: str
		return Language.CreateLocalizationString(valueString)

	@classmethod
	def _TypeCheckValue (cls, value: typing.Union[float, int]) -> None:
		if not isinstance(value, float) and not isinstance(value, int):
			raise Exceptions.IncorrectTypeException(value, "value", (float, int))

		if not ToolsNumbers.IsRealNumber(value):
			raise ValueError("Value is not a real number.")

class RealNumberDialogSetting(RealNumberSetting):
	Dialog = SettingsDialogs.RealNumberDialog

class TimeSecondsSetting(RealNumberSetting):
	@classmethod
	def GetValueText (cls, value: typing.Union[float, int]) -> localization.LocalizedString:
		cls._TypeCheckValue(value)

		valueString = str(value)  # type: str
		text = Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Time.Second_Template", fallbackText = "Second_Template")
		Language.AddTokens(text, valueString)
		return text

class TimeSecondsDialogSetting(TimeSecondsSetting):
	Dialog = SettingsDialogs.RealNumberDialog

class LogSizeLimitSetting(RealNumberSetting):
	@classmethod
	def GetValueText (cls, value: typing.Union[float, int]) -> localization.LocalizedString:
		cls._TypeCheckValue(value)

		valueString = str(value)  # type: str

		if value >= 0:
			text = Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.File_Size.Megabyte_Template", fallbackText = "Megabyte_Template")
		else:
			text = Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.File_Size.Disabled_Template", fallbackText = "Disabled_Template")

		Language.AddTokens(text, valueString)
		return text

class LogSizeLimitDialogSetting(LogSizeLimitSetting):
	Dialog = SettingsDialogs.RealNumberDialog

class LogLevelsSetting(SettingsBase.Setting):
	Type = str

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		cls._TypeCheckValue(value)

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

	@classmethod
	def GetValueText (cls, value: str) -> localization.LocalizedString:
		cls._TypeCheckValue(value)

		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.LogLevels." + value, fallbackText = "LogLevels." + value)

	@classmethod
	def _TypeCheckValue (cls, value: str) -> None:
		if not isinstance(value, str):
			raise Exceptions.IncorrectTypeException(value, "value", (str,))

		Parse.ParsePythonEnum(value, Debug.LogLevels)

class LogLevelsDialogSetting(LogLevelsSetting):
	class Dialog(SettingsDialogs.EnumDialog):
		EnumName = "LogLevels"  # type: str
		Values = []  # type: typing.List[str]

		@classmethod
		def _OnInitializeSubclass (cls):
			super()._OnInitializeSubclass()

			for logLevel in Debug.LogLevels:  # type: Debug.LogLevels
				cls.Values.append(logLevel.name)
