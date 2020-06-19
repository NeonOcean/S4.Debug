from __future__ import annotations

import os
import sys
import types
import typing

from NeonOcean.S4.Main import Debug, Language, LoadingShared
from NeonOcean.S4.Main.Abstract import Settings as AbstractSettings
from NeonOcean.S4.Main.Data import Persistence
from NeonOcean.S4.Main.Tools import Events, Exceptions, Types, Version
from NeonOcean.S4.Main.UI import Settings as UISettings, SettingsShared as UISettingsShared
from NeonOcean.S4.Debug import This
from sims4 import localization

SettingsFilePath = os.path.join(This.Mod.PersistentPath, "Settings.json")  # type: str

SettingsPersistence = None  # type: typing.Optional[Persistence.PersistentFile]
AllSettings = list()  # type: typing.List[typing.Type[Setting]]

_previousValues = dict()  # type: typing.Dict[str, typing.Any]

_onUpdateWrapper = Events.EventHandler()  # type: Events.EventHandler
_onLoadWrapper = Events.EventHandler()  # type: Events.EventHandler

class UpdateEventArguments(Events.EventArguments):
	def __init__ (self, changedSettings: typing.Set[str]):
		self.ChangedSettings = changedSettings

	def Changed (self, key: str) -> bool:
		"""
		Get whether or not a setting has been changed between the last update and this one.
		"""

		return key in self.ChangedSettings

class Setting(AbstractSettings.SettingAbstract):
	IsSetting = False  # type: bool

	Key: str
	Type: typing.Type
	Default: typing.Any

	Dialog: typing.Type[UISettings.SettingDialogBase]

	ListPath = "Root"  # type: str
	ListPriority = 0  # type: typing.Union[float, int]

	_overrides = None  # type: typing.Optional[typing.List[_SettingOverride]]

	def __init_subclass__ (cls, **kwargs):
		super().OnInitializeSubclass()

		if cls.IsSetting:
			cls.SetDefault()
			AllSettings.append(cls)

	@classmethod
	def Setup (cls) -> None:
		"""
		Setup this setting with the underlying persistence object.
		"""

		_Setup(cls.Key,
			   cls.Type,
			   cls.Default,
			   cls.Verify)

	@classmethod
	def IsSetup (cls) -> bool:
		return _isSetup(cls.Key)

	@classmethod
	def IsHidden (cls) -> bool:
		"""
		Get whether or not this setting should be visible to the user.
		"""

		return False

	@classmethod
	def Get (cls, ignoreOverride: bool = False) -> typing.Any:
		"""
		Get the setting's value.
		:param ignoreOverride: If true we will ignore any value overrides will be ignored when retrieving the value.
		:type ignoreOverride: bool
		:return: The setting's value.
		"""

		if not isinstance(ignoreOverride, bool):
			raise Exceptions.IncorrectTypeException(ignoreOverride, "ignoreOverride", (bool,))

		if ignoreOverride:
			return _Get(cls.Key)

		if not cls.IsOverridden():
			return _Get(cls.Key)

		activeOverrideIdentifier = cls.GetActiveOverrideIdentifier()  # type: str
		activeOverrideValue = cls.GetOverrideValue(activeOverrideIdentifier)  # type: typing.Any
		return activeOverrideValue

	@classmethod
	def Set (cls, value: typing.Any, autoSave: bool = True, autoUpdate: bool = True) -> None:
		"""
		Set the setting's value.
		:param value: The new setting value. An exception will be raised if this doesn't match the setting's type or has an incorrect
		value.
		:type value: typing.Any
		:param autoSave: If true we will automatically save changes to the save file.
		:type autoSave: bool
		:param autoUpdate: If true we will automatically trigger update callbacks.
		:type autoUpdate: bool
		"""

		return _Set(cls.Key, value, autoSave = autoSave, autoUpdate = autoUpdate)

	@classmethod
	def Reset (cls, autoSave: bool = True, autoUpdate: bool = True) -> None:
		"""
		Reset to the default value.
		"""

		_Reset(key = cls.Key, autoSave = autoSave, autoUpdate = autoUpdate)

	@classmethod
	def Verify (cls, value: typing.Any, lastChangeVersion: typing.Optional[Version.Version] = None) -> typing.Any:
		"""
		Check whether a value is valid. This method should return the value if it is correct, return a corrected version, or raise
		an exception if the value cannot reasonably be fixed.
		:param value: A value to be verified.
		:type value: typing.Any
		:param lastChangeVersion: The last version of the mod that the value was checked.
		:type lastChangeVersion: Version.Version
		:return: The input value or a corrected version of it.
		:rtype: typing.Any
		"""

		return value

	@classmethod
	def Override (cls, value: typing.Any, overrideIdentifier: str, overridePriority: typing.Union[float, int],
				  overrideReasonText: typing.Optional[typing.Callable[[], localization.LocalizedString]] = None) -> None:
		"""
		Force this setting to take on a value temporarily. The setting must be setup before this method can be called.
		:param value: The value forced onto the setting, this must be able to pass the verify method's tests.
		:type value: typing.Any
		:param overrideIdentifier: A unique identifier for this override. This needs to be unique within this setting, no two overrides
		can share an identifier.
		:type overrideIdentifier: str
		:param overridePriority: The priority of this override. If multiple overrides are imposed on this setting at once the one with the
		highest priority will be active.
		:type overridePriority: float | int
		:param overrideReasonText: A function that will return a sims 4 localization string explaining to the player why this setting cannot
		be changed.
		:type overrideReasonText: typing.Optional[typing.Callable[[], localization.LocalizedString]]
		"""

		if not isinstance(value, cls.Type):
			raise Exceptions.IncorrectTypeException(value, "value", (cls.Type,))

		if not isinstance(overrideIdentifier, str):
			raise Exceptions.IncorrectTypeException(overrideIdentifier, "overrideIdentifier", (str,))

		if not isinstance(overridePriority, (float, int)):
			raise Exceptions.IncorrectTypeException(overridePriority, "overridePriority", (float, int))

		if not isinstance(overrideReasonText, typing.Callable) and overrideReasonText is not None:
			raise Exceptions.IncorrectTypeException(overrideReasonText, "reasonText", ("Callable", None))

		if not cls.IsSetup():
			raise Exception("Cannot override the non setup setting '%s'." % cls.Key)

		value = cls.Verify(value)

		if cls._overrides is None:
			cls._overrides = list()

		if any(testingOverride.Identifier == overrideIdentifier for testingOverride in cls._overrides):
			raise Exception("The identifier '" + overrideIdentifier + "' has already been taken by another override.")

		cls._overrides.append(_SettingOverride(value, overrideIdentifier, overridePriority, overrideReasonText))
		cls._overrides.sort(key = lambda sortingOverride: sortingOverride.Priority, reverse = True)
		Update()

	@classmethod
	def RemoveOverride (cls, overrideIdentifier: str) -> None:
		"""
		Deactivate an override. If no such override is set nothing will happen. The setting must be setup before this method can be called.
		:param overrideIdentifier: The identifier given to the override to be removed.
		:type overrideIdentifier: str
		"""

		if not isinstance(overrideIdentifier, str):
			raise Exceptions.IncorrectTypeException(overrideIdentifier, "overrideIdentifier", (str,))

		if not cls.IsSetup():
			raise Exception("Cannot remove override of the non setup setting '%s'." % cls.Key)

		if cls._overrides is None:
			return

		if len(cls._overrides) == 0:
			return

		for overrideIndex in range(len(cls._overrides)):
			if cls._overrides[overrideIndex].Identifier == overrideIdentifier:
				cls._overrides.pop(overrideIndex)
				Update()
				return

	@classmethod
	def ClearAllOverrides (cls) -> None:
		"""
		Clear all set overrides.
		"""

		cls._overrides = None

	@classmethod
	def IsOverridden (cls) -> bool:
		"""
		Whether or not this setting's value is overridden.
		"""

		if cls._overrides is None:
			return False

		if len(cls._overrides) == 0:
			return False

		return True

	@classmethod
	def IsOverriddenBy (cls, overrideIdentifier: str) -> bool:
		"""
		Whether or not this setting has an override with this identifier.
		"""

		if not isinstance(overrideIdentifier, str):
			raise Exceptions.IncorrectTypeException(overrideIdentifier, "overrideIdentifier", (str,))

		if not cls.IsOverridden():
			return False

		for override in cls._overrides:  # type: _SettingOverride
			if override.Identifier == overrideIdentifier:
				return True

		return False

	@classmethod
	def GetActiveOverrideIdentifier (cls) -> str:
		"""
		Get the active override's identifier. An exception will be raised if no override is active.
		:return: The active override's identifier.
		:rtype: str
		"""

		if not cls.IsOverridden():
			raise Exception("No overrides exist for the setting '" + cls.Key + "'.")

		return cls._overrides[0].Identifier

	@classmethod
	def GetAllOverrideIdentifiers (cls) -> typing.Set[str]:
		"""
		Get the identifier of all registered overrides in this setting as a set.
		"""

		allIdentifiers = set()  # type: typing.Set[str]

		if cls._overrides is not None:
			for override in cls._overrides:  # type: _SettingOverride
				allIdentifiers.add(override.Identifier)

		return allIdentifiers

	@classmethod
	def GetOverrideValue (cls, overrideIdentifier: str) -> typing.Any:
		"""
		Get the value of the targeted override. An exception will be raised if no such override is set.
		:param overrideIdentifier: The identifier of the targeted override.
		:type overrideIdentifier: str
		:return: The value of the override specified.
		:rtype: str
		"""

		if not isinstance(overrideIdentifier, str):
			raise Exceptions.IncorrectTypeException(overrideIdentifier, "overrideIdentifier", (str,))

		if cls._overrides is not None:
			for override in cls._overrides:  # type: _SettingOverride
				if override.Identifier == overrideIdentifier:
					return override.Value

		raise Exception("No override with the identifier '" + overrideIdentifier + "' in the setting '" + cls.Key + "'.")

	@classmethod
	def GetOverridePriority (cls, overrideIdentifier: str) -> typing.Union[float, int]:
		"""
		Get the priority of the targeted override. An exception will be raised if no such override is set.
		:param overrideIdentifier: The identifier of the targeted override.
		:type overrideIdentifier: str
		:return: The priority of the override specified.
		:rtype: float | int
		"""

		if not isinstance(overrideIdentifier, str):
			raise Exceptions.IncorrectTypeException(overrideIdentifier, "overrideIdentifier", (str,))

		if cls._overrides is not None:
			for override in cls._overrides:  # type: _SettingOverride
				if override.Identifier == overrideIdentifier:
					return override.Priority

		raise Exception("No override with the identifier '" + overrideIdentifier + "' in the setting '" + cls.Key + "'.")

	@classmethod
	def GetOverrideReasonText (cls, overrideIdentifier: str) -> typing.Callable[[], localization.LocalizedString]:
		"""
		Get the reason text of the targeted override. An exception will be raised if no such override is set.
		:param overrideIdentifier: The identifier of the targeted override.
		:type overrideIdentifier: str
		:return: The reason text function of the override specified.
		:rtype: typing.Callable[[], localization.LocalizedString]
		"""

		if not isinstance(overrideIdentifier, str):
			raise Exceptions.IncorrectTypeException(overrideIdentifier, "overrideIdentifier", (str,))

		if cls._overrides is not None:
			for override in cls._overrides:  # type: _SettingOverride
				if override.Identifier == overrideIdentifier:
					return override.ReasonText

		raise Exception("No override with the identifier '" + overrideIdentifier + "' in the setting '" + cls.Key + "'.")

	@classmethod
	def CanShowDialog (cls) -> bool:
		"""
		Get whether or not this setting can show a dialog to change it.
		"""

		if not hasattr(cls, "Dialog"):
			return False

		return True

	@classmethod
	def ShowDialog (cls, returnCallback: typing.Optional[typing.Callable[[], None]] = None) -> None:
		"""
		Show the dialog to change this setting.
		:param returnCallback: The return callback will be triggered after the setting dialog is closed.
		:type returnCallback: typing.Callable[[], None]
		"""

		if not isinstance(returnCallback, typing.Callable) and returnCallback is not None:
			raise Exceptions.IncorrectTypeException(returnCallback, "returnCallback", ("Callable", None))

		if not cls.CanShowDialog():
			return

		if cls.Dialog is None:
			return

		settingWrapper = UISettingsShared.SettingStandardWrapper(cls)  # type: UISettingsShared.SettingStandardWrapper
		settingDialog = cls.Dialog()  # type: UISettings.SettingDialogBase
		settingDialog.ShowDialog(settingWrapper, returnCallback = returnCallback)

	@classmethod
	def GetNameText (cls) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Mod_Settings.Values." + cls.Key + ".Name", fallbackText = cls.Key)

	@classmethod
	def GetDefaultText (cls) -> localization.LocalizedString:
		return Language.CreateLocalizationString("**")

	@classmethod
	def GetValueText (cls, value: typing.Any) -> localization.LocalizedString:
		return Language.CreateLocalizationString("**")

	@classmethod
	def GetSettingIconKey (cls) -> typing.Optional[str]:
		return None

	@classmethod
	def _OnLoad (cls) -> None:
		pass

class _SettingOverride:
	def __init__ (self,
				  value: typing.Any,
				  identifier: str,
				  priority: typing.Union[float, int],
				  reasonText: typing.Optional[typing.Callable[[], localization.LocalizedString]] = None):

		self.Value = value  # type: typing.Any
		self.Identifier = identifier  # type: str
		self.Priority = priority  # type: typing.Union[float, int]

		if reasonText is not None:
			self.ReasonText = reasonText  # type: typing.Callable[[], localization.LocalizedString]
		else:
			self.ReasonText = lambda *args, **kwargs: Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Misc.Override.Unknown_Reason")  # type: typing.Callable[[], localization.LocalizedString]

def GetAllSettings () -> typing.List[typing.Type[Setting]]:
	return list(AllSettings)

def Load () -> None:
	SettingsPersistence.Load()

def Save () -> None:
	SettingsPersistence.Save()

def Update () -> None:
	SettingsPersistence.Update()

def RegisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, UpdateEventArguments], None]) -> None:
	global _onUpdateWrapper
	_onUpdateWrapper += updateCallback

def UnregisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, UpdateEventArguments], None]) -> None:
	global _onUpdateWrapper
	_onUpdateWrapper -= updateCallback

def RegisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	global _onLoadWrapper
	_onLoadWrapper += loadCallback

def UnregisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	global _onLoadWrapper
	_onLoadWrapper -= loadCallback

def _OnInitiate (cause: LoadingShared.LoadingCauses) -> None:
	global SettingsPersistence

	if cause:
		pass

	if SettingsPersistence is None:
		SettingsPersistence = Persistence.PersistentFile(SettingsFilePath, This.Mod.Version, hostNamespace = This.Mod.Namespace, alwaysSaveValues = True)

		for setting in AllSettings:
			setting.Setup()

		SettingsPersistence.OnUpdate += _OnUpdateCallback
		SettingsPersistence.OnLoad += _OnLoadCallback

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
	SettingsPersistence.Setup(key, valueType, default, verify)

def _isSetup (key: str) -> bool:
	if SettingsPersistence is None:
		return False

	return SettingsPersistence.IsSetup(key)

def _Get (key: str) -> typing.Any:
	return SettingsPersistence.Get(key)

def _Set (key: str, value: typing.Any, autoSave: bool = True, autoUpdate: bool = True) -> None:
	SettingsPersistence.Set(key, value, autoSave = autoSave, autoUpdate = autoUpdate)

def _Reset (key: str = None, autoSave: bool = True, autoUpdate: bool = True) -> None:
	SettingsPersistence.Reset(key = key, autoSave = autoSave, autoUpdate = autoUpdate)

def _InvokeOnUpdateWrapperEvent (changedSettings: typing.Set[str]) -> UpdateEventArguments:
	updateEventArguments = UpdateEventArguments(changedSettings)  # type: UpdateEventArguments

	for updateCallback in _onUpdateWrapper:  # type: typing.Callable[[types.ModuleType, Events.EventArguments], None]
		try:
			updateCallback(sys.modules[__name__], updateEventArguments)
		except:
			Debug.Log("Failed to run the 'OnUpdateWrapper' callback '" + Types.GetFullName(updateCallback) + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

	return updateEventArguments

def _InvokeOnLoadWrapperEvent () -> Events.EventArguments:
	eventArguments = Events.EventArguments()  # type: Events.EventArguments

	for updateCallback in _onUpdateWrapper:  # type: typing.Callable[[types.ModuleType, Events.EventArguments], None]
		try:
			updateCallback(sys.modules[__name__], eventArguments)
		except:
			Debug.Log("Failed to run the 'OnLoadWrapper' callback '" + Types.GetFullName(updateCallback) + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

	return eventArguments

# noinspection PyUnusedLocal
def _OnUpdateCallback (owner: Persistence.Persistent, eventArguments: Events.EventArguments) -> None:
	global _previousValues

	allSettings = GetAllSettings()  # type: typing.List[typing.Type[Setting]]

	currentValues = dict()  # type: typing.Dict[str, typing.Any]
	changedSettings = set()  # type: typing.Set[str]

	for setting in allSettings:  # type: typing.Type[Setting]
		settingValue = setting.Get()  # type: typing.Any
		currentValues[setting.Key] = settingValue

		if not setting.Key in _previousValues:
			changedSettings.add(setting.Key)
			continue

		if _previousValues[setting.Key] != settingValue:
			changedSettings.add(setting.Key)

	_previousValues = currentValues

	_InvokeOnUpdateWrapperEvent(changedSettings)

# noinspection PyUnusedLocal
def _OnLoadCallback (owner: Persistence.Persistent, eventArguments: Events.EventArguments) -> None:
	for setting in AllSettings:  # type: Setting
		try:
			# noinspection PyProtectedMember
			setting._OnLoad()
		except Exception:
			Debug.Log("Failed to notify the setting '" + setting.Key + "' of a load event.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

	_InvokeOnLoadWrapperEvent()
