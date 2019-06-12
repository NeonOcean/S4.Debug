import typing

import services
from NeonOcean.Debug import Settings, This
from NeonOcean.Main import Debug, Director, SettingsShared
from NeonOcean.Main.Interactions.Support import Categories, Dependent, Events, Registration
from interactions.base import immediate_interaction
from objects import script_object
from sims4 import resources
from sims4.tuning import instance_manager

ModSettingInteractions = list()  # type: typing.List[typing.Type[ModSettingInteraction]]

class ModSettingInteraction(Dependent.DependentExtension, Events.EventsExtension, Registration.RegistrationExtension, immediate_interaction.ImmediateSuperInteraction):
	DependentMod = This.Mod

	def __init_subclass__ (cls, *args, **kwargs):
		try:
			super().__init_subclass__(*args, **kwargs)

			ModSettingInteractions.append(cls)
		except Exception as e:
			Debug.Log("Failed to initialize new sub class for '" + cls.__name__ + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
			raise e

class _Announcer(Director.Announcer):
	Host = This.Mod

	@classmethod
	def OnInstanceManagerLoaded (cls, instanceManager: instance_manager.InstanceManager):
		if instanceManager.TYPE != resources.Types.OBJECT:
			return

		modSettingCategory = services.get_instance_manager(resources.Types.PIE_MENU_CATEGORY).get(Categories.DebugModSettingsID)  # type: script_object.ScriptObject

		for setting in Settings.GetAllSettings():  # type: SettingsShared.SettingBase
			if not hasattr(setting, "Dialog"):
				continue

			if setting.Dialog is None:
				continue

			settingInteraction = ModSettingInteraction.generate_tuned_type(This.Mod.Namespace + ".Interactions.ModSetting." + setting.Key)  # type: typing.Type[ModSettingInteraction]

			def CreateSettingDisplayNameCallable (displayNameSetting: SettingsShared.SettingBase) -> typing.Callable:

				# noinspection PyUnusedLocal
				def SettingDisplayNameCallable (*args, **kwargs):
					return displayNameSetting.GetName()

				return SettingDisplayNameCallable

			settingInteraction.display_name = CreateSettingDisplayNameCallable(setting)
			settingInteraction.category = modSettingCategory

			# noinspection SpellCheckingInspection
			settingInteraction._saveable = None

			settingInteraction.OnStarted = CreateOnStartedMethod(setting)

			Registration.RegisterAllObjectsInteraction(settingInteraction)

def CreateOnStartedMethod (setting: SettingsShared.SettingBase):
	# noinspection PyUnusedLocal
	def OnStarted (self) -> None:
		setting.ShowDialog()

	return OnStarted
