from __future__ import annotations

import typing

from NeonOcean.S4.Debug import This
from NeonOcean.S4.Main import Debug
from NeonOcean.S4.Main.Interactions.Support import Dependent, Events, Registration
from interactions.base import immediate_interaction

ModSettingsInteractions = list()  # type: typing.List[typing.Type[ModSettingsInteraction]]

class ModSettingsInteraction(Dependent.DependentExtension, Events.EventsExtension, Registration.RegistrationExtension, immediate_interaction.ImmediateSuperInteraction):
	DependentMod = This.Mod

	def __init_subclass__ (cls, *args, **kwargs):
		try:
			super().__init_subclass__(*args, **kwargs)

			ModSettingsInteractions.append(cls)
		except Exception as e:
			Debug.Log("Failed to initialize new sub class for '" + cls.__name__ + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
			raise e
