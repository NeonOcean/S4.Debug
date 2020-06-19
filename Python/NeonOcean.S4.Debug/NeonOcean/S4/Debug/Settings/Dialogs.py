from __future__ import annotations

import typing

from NeonOcean.S4.Debug import This
from NeonOcean.S4.Main import Language, Websites
from NeonOcean.S4.Main.Tools import Exceptions, Numbers, Parse
from NeonOcean.S4.Main.UI import Settings as UISettings, SettingsShared as UISettingsShared
from sims4 import localization
from ui import ui_dialog

class BooleanYesNoDialog(UISettings.StandardDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	Values = [True, False]  # type: typing.List[bool]

	def _GetDescriptionSettingText (self, setting: UISettingsShared.SettingStandardWrapper) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Mod_Settings.Values." + setting.Key + ".Description")

	def _GetDescriptionDocumentationURL (self, setting: UISettingsShared.SettingStandardWrapper) -> typing.Optional[str]:
		return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

	def _GetValueText (self, value: bool) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Boolean.Yes_No." + str(value), fallbackText = str(value))

	def _CreateButtons (self,
						setting: UISettingsShared.SettingStandardWrapper,
						currentValue: typing.Any,
						showDialogArguments: typing.Dict[str, typing.Any],
						returnCallback: typing.Callable[[], None] = None,
						*args, **kwargs):

		buttons = super()._CreateButtons(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogButton]

		for valueIndex in range(len(self.Values)):  # type: int
			def CreateValueButtonCallback (value: typing.Any) -> typing.Callable:

				# noinspection PyUnusedLocal
				def ValueButtonCallback (dialog: ui_dialog.UiDialog) -> None:
					self._ShowDialogInternal(setting, value, showDialogArguments, returnCallback = returnCallback)

				return ValueButtonCallback

			valueButtonArguments = {
				"responseID": 50000 + valueIndex * -5,
				"sortOrder": -(500 + valueIndex * -5),
				"callback": CreateValueButtonCallback(self.Values[valueIndex]),
				"text": self._GetValueText(self.Values[valueIndex]),
			}

			if currentValue == self.Values[valueIndex]:
				valueButtonArguments["selected"] = True

			valueButton = UISettings.ChoiceDialogButton(**valueButtonArguments)
			buttons.append(valueButton)

		return buttons

class RealNumberDialog(UISettings.InputDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	def _GetDescriptionSettingText (self, setting: UISettingsShared.SettingStandardWrapper) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Mod_Settings.Values." + setting.Key + ".Description")

	def _GetDescriptionDocumentationURL (self, setting: UISettingsShared.SettingStandardWrapper) -> typing.Optional[str]:
		return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

	def _ParseValueString (self, valueString: str) -> typing.Union[float, int]:
		if not isinstance(valueString, str):
			raise Exceptions.IncorrectTypeException(valueString, "valueString", (str,))

		parsedInput = Parse.ParseNumber(valueString)  # type: typing.Union[float, int]

		if not Numbers.IsRealNumber(parsedInput):
			raise Exception("Input string cannot be parsed to a real number.")

		return parsedInput

	def _ValueToString (self, value: typing.Union[float, int]) -> str:
		if not isinstance(value, float) and not isinstance(value, int):
			raise Exceptions.IncorrectTypeException(value, "value", (float, int))

		if not Numbers.IsRealNumber(value):
			raise Exception("'value' is not a real number.")

		return str(value)

class EnumDialog(UISettings.StandardDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	EnumName: str  # type: str
	Values: typing.List[str]

	def _GetDescriptionSettingText (self, setting: UISettingsShared.SettingStandardWrapper) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Mod_Settings.Values." + setting.Key + ".Description")

	def _GetDescriptionDocumentationURL (self, setting: UISettingsShared.SettingStandardWrapper) -> typing.Optional[str]:
		return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

	def _GetValueText (self, value: str) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings." + self.EnumName + ".Types." + value, fallbackText = value)

	def _CreateButtons (self,
						setting: UISettingsShared.SettingStandardWrapper,
						currentValue: typing.Any,
						showDialogArguments: typing.Dict[str, typing.Any],
						returnCallback: typing.Callable[[], None] = None,
						*args, **kwargs):

		buttons = super()._CreateButtons(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogButton]

		for valueIndex in range(len(self.Values)):  # type: int
			def CreateValueButtonCallback (value: typing.Any) -> typing.Callable:

				# noinspection PyUnusedLocal
				def ValueButtonCallback (dialog: ui_dialog.UiDialog) -> None:
					self._ShowDialogInternal(setting, value, showDialogArguments = showDialogArguments, returnCallback = returnCallback)

				return ValueButtonCallback

			valueButtonArguments = {
				"responseID": 50000 + valueIndex * -5,
				"sortOrder": -(500 + valueIndex * -5),
				"callback": CreateValueButtonCallback(self.Values[valueIndex]),
				"text": self._GetValueText(self.Values[valueIndex])
			}

			if currentValue == self.Values[valueIndex]:
				valueButtonArguments["selected"] = True

			valueButton = UISettings.ChoiceDialogButton(**valueButtonArguments)
			buttons.append(valueButton)

		return buttons
