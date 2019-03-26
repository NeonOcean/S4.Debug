import typing

from NeonOcean.Debug import This
from NeonOcean.Main import Debug, Resetting, Websites
from NeonOcean.Main.Interactions.Support import Dependent, Events, Registration
from NeonOcean.Main.UI import Generic
from interactions.base import immediate_interaction

ResetInteractions = list()  # type: typing.List[typing.Type[ResetInteraction]]
DocumentationInteractions = list()  # type: typing.List[typing.Type[DocumentationInteraction]]
VisitModPageInteractions = list()  # type: typing.List[typing.Type[VisitModPageInteraction]]

class ResetInteraction(Dependent.DependentExtension, Events.EventsExtension, Registration.RegistrationExtension, immediate_interaction.ImmediateSuperInteraction):
	DependentMod = This.Mod

	def __init_subclass__ (cls, *args, **kwargs):
		try:
			super().__init_subclass__(*args, **kwargs)

			ResetInteractions.append(cls)
		except Exception as e:
			Debug.Log("Failed to initialize new sub class for '" + cls.__name__ + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)
			raise e

	def OnStarted (self) -> None:
		try:
			Resetting.ShowResetDialog(This.Mod)
		except Exception as e:
			Debug.Log("Failed to show reset dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)

class DocumentationInteraction(Dependent.DependentExtension, Events.EventsExtension, Registration.RegistrationExtension, immediate_interaction.ImmediateSuperInteraction):
	DependentMod = This.Mod

	def __init_subclass__ (cls, *args, **kwargs):
		try:
			super().__init_subclass__(*args, **kwargs)

			DocumentationInteractions.append(cls)
		except Exception as e:
			Debug.Log("Failed to initialize new sub class for '" + cls.__name__ + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)
			raise e

	def OnStarted (self) -> None:
		try:
			Generic.ShowOpenBrowserDialog(Websites.GetNODocumentationModURL(This.Mod))
		except Exception as e:
			Debug.Log("Failed to show mod documentation with the open browser dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)

class VisitModPageInteraction(Dependent.DependentExtension, Events.EventsExtension, Registration.RegistrationExtension, immediate_interaction.ImmediateSuperInteraction):
	DependentMod = This.Mod

	def __init_subclass__ (cls, *args, **kwargs):
		try:
			super().__init_subclass__(*args, **kwargs)

			VisitModPageInteractions.append(cls)
		except Exception as e:
			Debug.Log("Failed to initialize new sub class for '" + cls.__name__ + "'.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)
			raise e

	def OnStarted (self) -> None:
		try:
			Generic.ShowOpenBrowserDialog(Websites.GetNOMainModURL(This.Mod))
		except Exception as e:
			Debug.Log("Failed to show the mod page dac with the open browser dialog.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)
