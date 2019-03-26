import datetime
import os
import platform
import traceback
import types
import typing
import uuid
from xml.sax import saxutils

import enum
from NeonOcean.Debug import LoggingShared, Settings, This
from NeonOcean.Main import Debug, Language, LoadingShared, Paths
from NeonOcean.Main.Data import Global
from NeonOcean.Main.Tools import Parse, Patcher, Timer
from NeonOcean.Main.UI import Notifications
from sims4 import common, log
from ui import ui_dialog_notification

_preload = True  # type: bool
_exiting = False  # type: bool

_loggingEnabled = None  # type: bool
_loggingMode = None  # type: LoggingShared.LoggingModes
_writeChronological = None  # type: bool
_writeGroups = None  # type: bool
_burstLevel = None  # type: Debug.LogLevels
_burstInterval = None  # type: float
_continuousLevel = None  # type: Debug.LogLevels

_burstTimer = None  # type: Timer.Timer

_logger = None  # type: _Logger

class _Report:
	def __init__ (self, logNumber: int, logTime: str, message: str, level: Debug.LogLevels, group: str = None, owner: str = None, exception: BaseException = None, logStack: bool = False, stacktrace: str = None):
		self.LogNumber = logNumber  # type: int
		self.LogTime = logTime  # type: str
		self.Message = message  # type: str
		self.Level = level  # type: Debug.LogLevels
		self.Group = group  # type: typing.Optional[str]
		self.Owner = owner  # type: typing.Optional[str]
		self.Exception = exception  # type: typing.Optional[BaseException]
		self.LogStack = logStack  # type: bool
		self.Stacktrace = stacktrace  # type: typing.Optional[str]

	def GetBytes (self, writeTime: str = None) -> bytes:
		return self.GetText(writeTime).encode("utf-8")

	def GetText (self, writeTime: str = None) -> str:
		logTemplate = "\t<Log Number=\"{}\" Level=\"{}\" Group=\"{}\""  # type: str

		logFormatting = [
			str(self.LogNumber),
			self.Level.name,
			str(self.Group)
		]  # type: typing.List[str]

		if self.Owner is not None:
			logTemplate += " Owner=\"{}\""
			logFormatting.append(self.Owner)

		logTemplate += " LogTime=\"{}\""
		logFormatting.append(self.LogTime)

		if writeTime is not None:
			logTemplate += " WriteTime=\"{}\""
			logFormatting.append(writeTime)

		logTemplate += ">\n" \
					   "\t\t<Message><!--\n" \
					   "\t\t\t-->{}<!--\n" \
					   "\t\t--></Message>\n"

		messageText = str(self.Message)  # type: str
		messageText = messageText.replace("\r\n", "\n")
		messageText = saxutils.escape(messageText).replace("\n", "\n<!--\t\t-->")
		logFormatting.append(messageText)

		if self.Level <= Debug.LogLevels.Exception:
			logTemplate += "\t\t<Exception><!--\n" \
						   "\t\t\t-->{}<!--\n" \
						   "\t\t--></Exception>\n"

			exceptionText = Debug.FormatException(self.Exception)  # type: str
			exceptionText = exceptionText.replace("\r\n", "\n")
			exceptionText = saxutils.escape(exceptionText).replace("\n", "\n<!--\t\t-->")
			logFormatting.append(exceptionText)

		if self.Level <= Debug.LogLevels.Error or self.LogStack:
			logTemplate += "\t\t<Stacktrace><!--\n" \
						   "\t\t\t-->{}<!--\n" \
						   "\t\t--></Stacktrace>\n"

			stackTraceText = self.Stacktrace  # type: str
			stackTraceText = stackTraceText.replace("\r\n", "\n")
			stackTraceText = saxutils.escape(stackTraceText).replace("\n", "\n<!--\t\t-->")
			logFormatting.append(stackTraceText)

		logTemplate += "\t</Log>"

		logText = logTemplate.format(*logFormatting)  # type: str
		logText = logText.replace("\n", os.linesep)

		return logText

class _Logger:
	_logStartBytes = ("<?xml version=\"1.0\" encoding=\"utf-8\"?>" + os.linesep + "<LogFile>" + os.linesep).encode("utf-8")  # type: bytes
	_logEndBytes = (os.linesep + "</LogFile>").encode("utf-8")  # type: bytes

	_globalSessionID = "SessionID"  # type: str
	_globalSessionStartTime = "SessionStartTime"  # type: str
	_globalLoggingCount = "LoggingCount"  # type: str
	_globalLoggingNamespaceCounts = "LoggingNamespaceCounts"  # type: str
	_globalShownWriteFailureNotification = "ShownWriteFailureNotification"  # type: str

	def __init__ (self, loggingRootPath: str):
		"""
		An object for logging debug information.
		Logs will be written to a folder named either by the global NeonOcean debugging start time, or the time ChangeLogFile() was last called for this object.

		:param loggingRootPath: The root path all logs sent to this logger object will be written.
		:type loggingRootPath: str
		"""

		self.DebugGlobal = Global.GetModule("Debug")

		if not hasattr(self.DebugGlobal, self._globalSessionID):
			setattr(self.DebugGlobal, self._globalSessionID, uuid.UUID)

		if not hasattr(self.DebugGlobal, self._globalSessionStartTime):
			setattr(self.DebugGlobal, self._globalSessionStartTime, datetime.datetime.now())

		if not hasattr(self.DebugGlobal, self._globalLoggingCount):
			setattr(self.DebugGlobal, self._globalLoggingCount, 0)

		if not hasattr(self.DebugGlobal, self._globalLoggingNamespaceCounts):
			setattr(self.DebugGlobal, self._globalLoggingNamespaceCounts, dict())

		if not hasattr(self.DebugGlobal, self._globalShownWriteFailureNotification):
			setattr(self.DebugGlobal, self._globalShownWriteFailureNotification, False)

		self.ReportStorage = list()  # type: typing.List[_Report]
		self.PreloadReportStorage = list()  # type: typing.List[_Report]

		self.CurrentLogNumber = 0  # type: int

		self._loggingRootPath = loggingRootPath  # type: str
		self._loggingDirectoryName = Debug.GetDateTimePathString(getattr(self.DebugGlobal, self._globalSessionStartTime))  # type: str

		self._writeFailureCount = 0  # type: int
		self._writeFailureLimit = 2  # type: int
		self._isContinuation = False  # type: bool

		self._sessionInformation = self._CreateSessionInformation()  # type: str
		self._modInformation = self._CreateModsInformation()  # type: str

	def Log (self, message, level: Debug.LogLevels, group: str = None, owner: str = None, logStack: bool = False, exception: BaseException = None, frame: types.FrameType = None) -> None:
		if self._writeFailureCount >= self._writeFailureLimit:
			return

		if not _loggingEnabled and _loggingEnabled is not None:
			return

		if frame is log.DEFAULT:
			frame = None

		report = _Report(self.CurrentLogNumber, datetime.datetime.now().isoformat(), str(message), level = level, group = str(group), owner = owner, exception = exception, logStack = logStack, stacktrace = str.join("", traceback.format_stack(f = frame)))  # type: _Report
		self.CurrentLogNumber += 1

		if This.Mod.Loading and _preload:
			self.PreloadReportStorage.append(report)
			return

		if _loggingMode == LoggingShared.LoggingModes.Burst:
			if level > _burstLevel:
				return
		elif _loggingMode == LoggingShared.LoggingModes.Continuous:
			if level > _continuousLevel:
				return

		if _exiting:
			self.LogReport(report)

		if _loggingMode == LoggingShared.LoggingModes.Burst:
			self.ReportStorage.append(report)

			if level <= Debug.LogLevels.Error:
				self.Flush()
		elif _loggingMode == LoggingShared.LoggingModes.Continuous:
			self.LogReport(report)

	def Flush (self) -> None:
		if _loggingEnabled:
			self.LogAllReports(self.ReportStorage)

		self.ReportStorage = list()

	def FlushPreload (self) -> None:
		if _loggingEnabled:
			reportIndex = 0  # type: int
			while reportIndex < len(self.PreloadReportStorage):
				if _loggingMode == LoggingShared.LoggingModes.Burst:
					if self.PreloadReportStorage[reportIndex].Level > _burstLevel:
						self.PreloadReportStorage.pop(reportIndex)
						continue
				elif _loggingMode == LoggingShared.LoggingModes.Continuous:
					if self.PreloadReportStorage[reportIndex].Level > _continuousLevel:
						self.PreloadReportStorage.pop(reportIndex)
						continue

				reportIndex += 1

			self.LogAllReports(self.PreloadReportStorage)

		self.PreloadReportStorage = list()

	def LogReport (self, report: _Report, retryOnError: bool = True) -> None:
		if not _writeChronological and not _writeGroups:
			return

		logTextBytes = report.GetBytes()  # type: bytes

		logDirectory = os.path.join(self.GetLoggingRootPath(), self.GetLoggingDirectoryName())  # type: str
		groupsLogDirectory = os.path.join(logDirectory, "Groups")  # type: str

		try:
			if not os.path.exists(logDirectory):
				os.makedirs(logDirectory)

			sessionFilePath = os.path.join(logDirectory, "Session.txt")  # type: str
			modsFilePath = os.path.join(logDirectory, "Mods.txt")  # type: str

			if not os.path.exists(sessionFilePath):
				with open(sessionFilePath, mode = "w+") as sessionFile:
					sessionFile.write(self._sessionInformation)

			if not os.path.exists(modsFilePath):
				with open(modsFilePath, mode = "w+") as modsFile:
					modsFile.write(self._modInformation)

			chronologicalFilePath = os.path.join(logDirectory, "Log.xml")  # type: str
			chronologicalFirstWrite = False  # type: bool

			if _writeChronological:
				if not os.path.exists(chronologicalFilePath):
					chronologicalFirstWrite = True
				else:
					self._VerifyLogFile(chronologicalFilePath)

				if chronologicalFirstWrite:
					with open(chronologicalFilePath, mode = "wb+") as chronologicalFile:
						chronologicalFile.write(self._logStartBytes)
						chronologicalFile.write(logTextBytes)
						chronologicalFile.write(self._logEndBytes)
				else:
					with open(chronologicalFilePath, "r+b") as chronologicalFile:
						chronologicalFile.seek(-len(self._logEndBytes), os.SEEK_END)
						chronologicalFile.write((os.linesep + os.linesep).encode("utf-8") + logTextBytes)
						chronologicalFile.write(self._logEndBytes)

			groupFilePath = os.path.join(groupsLogDirectory, str(report.Group) + ".xml")  # type: str
			groupFirstWrite = False  # type: bool

			if _writeGroups:
				if not os.path.exists(groupFilePath):
					groupFirstWrite = True
				else:
					self._VerifyLogFile(chronologicalFilePath)

				if groupFirstWrite:
					with open(groupFilePath, mode = "wb+") as groupFile:
						groupFile.write(self._logStartBytes)
						groupFile.write(logTextBytes)
						groupFile.write(self._logEndBytes)
				else:
					with open(groupFilePath, "r+b") as groupFile:
						groupFile.seek(-len(self._logEndBytes), os.SEEK_END)
						groupFile.write((os.linesep + os.linesep).encode("utf-8") + logTextBytes)
						groupFile.write(self._logEndBytes)
		except Exception as e:
			self._writeFailureCount += 1

			if not getattr(self.DebugGlobal, self._globalShownWriteFailureNotification):
				self._ShowWriteFailureDialog(e)
				setattr(self.DebugGlobal, self._globalShownWriteFailureNotification, True)

			if self._writeFailureCount < self._writeFailureLimit:
				self.ChangeLogFile()

				Debug.Log("Forced to start a new log file after encountering a write error.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e, retryOnError = False)

				if retryOnError:
					self.LogReport(report, retryOnError = False)

			return

	def LogAllReports (self, reports: typing.List[_Report], retryOnError: bool = True) -> None:
		if not _writeChronological and not _writeGroups:
			return

		if len(reports) == 0:
			return

		chronologicalTextBytes = bytes()  # type: bytes
		groupsTextBytes = dict()  # type: typing.Dict[str, bytes]

		writeTime = datetime.datetime.now().isoformat()  # type: str

		for report in reports:  # type: _Report
			group = str(report.Group)  # type: str
			reportTextBytes = report.GetBytes(writeTime = writeTime)  # type: bytes

			if _writeChronological:
				if len(chronologicalTextBytes) != 0:
					chronologicalTextBytes += (os.linesep + os.linesep).encode("utf-8") + reportTextBytes
				else:
					chronologicalTextBytes = reportTextBytes

			if _writeGroups:
				if group in groupsTextBytes:
					groupsTextBytes[group] += (os.linesep + os.linesep).encode("utf-8") + reportTextBytes
				else:
					groupsTextBytes[group] = reportTextBytes

		logDirectory = os.path.join(self.GetLoggingRootPath(), self.GetLoggingDirectoryName())  # type: str
		groupsLogDirectory = os.path.join(logDirectory, "Groups")  # type: str

		try:
			if not os.path.exists(logDirectory):
				os.makedirs(logDirectory)

			sessionFilePath = os.path.join(logDirectory, "Session.txt")  # type: str
			modsFilePath = os.path.join(logDirectory, "Mods.txt")  # type: str

			if not os.path.exists(sessionFilePath):
				with open(sessionFilePath, mode = "w+") as sessionFile:
					sessionFile.write(self._sessionInformation)

			if not os.path.exists(modsFilePath):
				with open(modsFilePath, mode = "w+") as modsFile:
					modsFile.write(self._modInformation)

			chronologicalFilePath = os.path.join(logDirectory, "Log.xml")  # type: str
			chronologicalFirstWrite = False  # type: bool

			if _writeChronological:
				if not os.path.exists(chronologicalFilePath):
					chronologicalFirstWrite = True
				else:
					self._VerifyLogFile(chronologicalFilePath)

				if chronologicalFirstWrite:
					with open(chronologicalFilePath, mode = "wb+") as chronologicalFile:
						chronologicalFile.write(self._logStartBytes)
						chronologicalFile.write(chronologicalTextBytes)
						chronologicalFile.write(self._logEndBytes)
				else:
					with open(chronologicalFilePath, "r+b") as chronologicalFile:
						chronologicalFile.seek(-len(self._logEndBytes), os.SEEK_END)
						chronologicalFile.write((os.linesep + os.linesep).encode("utf-8") + chronologicalTextBytes)
						chronologicalFile.write(self._logEndBytes)

			for groupName, groupTextBytes in groupsTextBytes.items():  # type: str, bytes
				groupFilePath = os.path.join(groupsLogDirectory, groupName + ".xml")  # type: str
				groupFirstWrite = False  # type: bool

				if _writeGroups:
					if not os.path.exists(groupFilePath):
						groupFirstWrite = True
					else:
						self._VerifyLogFile(groupFilePath)

					if groupFirstWrite:
						with open(groupFilePath, mode = "wb+") as groupFile:
							groupFile.write(self._logStartBytes)
							groupFile.write(groupTextBytes)
							groupFile.write(self._logEndBytes)
					else:
						with open(groupFilePath, "r+b") as groupFile:
							groupFile.seek(-len(self._logEndBytes), os.SEEK_END)
							groupFile.write((os.linesep + os.linesep).encode("utf-8") + groupTextBytes)
							groupFile.write(self._logEndBytes)
		except Exception as e:
			self._writeFailureCount += 1

			if not getattr(self.DebugGlobal, self._globalShownWriteFailureNotification):
				self._ShowWriteFailureDialog(e)
				setattr(self.DebugGlobal, self._globalShownWriteFailureNotification, True)

			if self._writeFailureCount < self._writeFailureLimit:
				self.ChangeLogFile()

				Debug.Log("Forced to start a new log file after encountering a write error.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e, retryOnError = False)

				if retryOnError:
					self.LogAllReports(reports, retryOnError = False)

			return

	def GetLoggingRootPath (self) -> str:
		return self._loggingRootPath

	def GetLoggingDirectoryName (self) -> str:
		return self._loggingDirectoryName

	def IsContinuation (self) -> bool:
		return self._isContinuation

	def ChangeLogFile (self) -> None:
		"""
		Change the current directory name for a new one. The new directory name will be the time this method was called.
		:rtype: None
		"""

		self._loggingDirectoryName = Debug.GetDateTimePathString(datetime.datetime.now())
		self._isContinuation = True

		self._sessionInformation = self._CreateSessionInformation()
		self._modInformation = self._CreateModsInformation()

	def _CreateSessionInformation (self) -> str:
		try:
			sessionTemplate = "Debugging session ID '{}'\n" \
							  "Debugging session start time '{}'\n" \
							  "Log is a continuation of another '{}'\n" \
							  "\n" \
							  "Operation system '{}'\n\n" \
							  "Version '{}'\n" \
							  "\n" \
							  "Installed Packs:\n" \
							  "{}"  # type: str

			installedPacksText = ""  # type: str

			for packTuple in common.Pack.items():  # type: typing.Tuple[str, common.Pack]
				if packTuple[1] == common.Pack.BASE_GAME:
					continue

				packAvailable = common.is_available_pack(packTuple[1])

				if packAvailable:
					if installedPacksText != "":
						installedPacksText += "\n"

					installedPacksText += packTuple[0]

			sessionFormatting = (str(getattr(self.DebugGlobal, self._globalSessionID)),
								 str(getattr(self.DebugGlobal, self._globalSessionStartTime)),
								 self.IsContinuation(),
								 platform.system(),
								 platform.version(),
								 installedPacksText)

			return sessionTemplate.format(*sessionFormatting)
		except Exception as e:
			Debug.Log("Failed to get session information", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)
			return "Failed to get session information"

	def _CreateModsInformation (self) -> str:
		try:
			modFolderString = os.path.split(Paths.ModsPath)[1] + " {" + os.path.split(Paths.ModsPath)[1] + "}"  # type: str

			for directoryRoot, directoryNames, fileNames in os.walk(Paths.ModsPath):  # type: str, list, list
				depth = 1

				if directoryRoot != Paths.ModsPath:
					depth = len(directoryRoot.replace(Paths.ModsPath + os.path.sep, "").split(os.path.sep)) + 1  # type: int

				indention = "\t" * depth  # type: str

				newString = ""  # type: str

				for directory in directoryNames:
					newString += "\n" + indention + directory + " {" + directory + "}"

				for file in fileNames:
					newString += "\n" + indention + file + " (" + str(os.path.getsize(os.path.join(directoryRoot, file))) + " B)"

				if len(newString) == 0:
					newString = "\n"

				newString += "\n"

				modFolderString = modFolderString.replace("{" + os.path.split(directoryRoot)[1] + "}", "{" + newString + "\t" * (depth - 1) + "}", 1)

			return modFolderString
		except Exception as e:
			Debug.Log("Failed to get mod information", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, exception = e)
			return "Failed to get mod information"

	def _VerifyLogFile (self, logFilePath: str) -> None:
		with open(logFilePath, "rb") as logFile:
			if self._logStartBytes != logFile.read(len(self._logStartBytes)):
				raise Exception("The start of the log file doesn't match what was expected.")

			logFile.seek(-len(self._logEndBytes), os.SEEK_END)

			if self._logEndBytes != logFile.read():
				raise Exception("The end of the log file doesn't match what was expected.")

	@staticmethod
	def _ShowWriteFailureDialog (exception: Exception) -> None:
		Notifications.ShowNotification(queue = True,
									   title = lambda *args, **kwargs: Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Debug.Write_Notification.Title"),
									   text = lambda *args, **kwargs: Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".System.Debug.Write_Notification.Text", Debug.FormatException(exception)),
									   expand_behavior = ui_dialog_notification.UiDialogNotification.UiDialogNotificationExpandBehavior.FORCE_EXPAND,
									   urgency = ui_dialog_notification.UiDialogNotification.UiDialogNotificationUrgency.URGENT)

def _Setup () -> None:
	global _logger

	_logger = _Logger(os.path.join(Paths.DebugPath, "Logs"))

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	global _preload, _loggingEnabled, _loggingMode, _writeChronological, _writeGroups, _burstLevel, _burstInterval, _continuousLevel

	if cause != LoadingShared.LoadingCauses.Reloading:
		Patcher.Patch(log, "debug", _Debug)
		Patcher.Patch(log.Logger, "debug", _LoggerDebug)

		Patcher.Patch(log, "info", _Info)
		Patcher.Patch(log.Logger, "info", _LoggerInfo)

		Patcher.Patch(log, "warn", _Warning)
		Patcher.Patch(log.Logger, "warn", _LoggerWarning)

		Patcher.Patch(log, "error", _Error)
		Patcher.Patch(log.Logger, "error", _LoggerError)

		Patcher.Patch(log, "exception", _Exception)

	_UpdateSettings()
	Settings.RegisterUpdate(_UpdateSettings)

	_preload = False
	_logger.FlushPreload()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	global _exiting

	Settings.UnregisterUpdate(_UpdateSettings)

	_logger.Flush()

	if cause == LoadingShared.UnloadingCauses.Exiting:
		_exiting = True

def _UpdateSettings () -> None:
	global _loggingEnabled, _loggingMode, _writeChronological, _writeGroups, _burstLevel, _burstInterval, _continuousLevel

	loggingEnabledChange = Settings.Get(Settings.Logging_Enabled.Key)  # type: bool
	loggingModeChange = Settings.Get(Settings.Logging_Mode.Key)  # type: str
	loggingModeChange = Parse.ParseEnum(loggingModeChange, LoggingShared.LoggingModes)  # type: LoggingShared.LoggingModes
	writeChronologicalChange = Settings.Get(Settings.Write_Chronological.Key)  # type: bool
	writeGroupsChange = Settings.Get(Settings.Write_Groups.Key)  # type: bool
	burstLevelChange = Settings.Get(Settings.Burst_Level.Key)  # type: str
	burstLevelChange = Parse.ParseEnum(burstLevelChange, Debug.LogLevels)  # type: LoggingShared.LoggingModes
	burstIntervalChange = Settings.Get(Settings.Burst_Interval.Key)  # type: float
	continuousLevelChange = Settings.Get(Settings.Continuous_Level.Key)  # type: str
	continuousLevelChange = Parse.ParseEnum(continuousLevelChange, Debug.LogLevels)  # type: LoggingShared.LoggingModes

	loggingEnabledLast = _loggingEnabled  # type: bool
	loggingModeLast = _loggingMode  # type: enum.EnumBase
	writeChronologicalLast = _writeChronological  # type: bool
	writeGroupsLast = _writeGroups  # type: bool
	burstLevelLast = _burstLevel  # type: enum.EnumBase
	burstIntervalLast = _burstInterval  # type: float
	continuousLevelLast = _continuousLevel  # type: enum.EnumBase

	if loggingEnabledLast != loggingEnabledChange:
		if loggingEnabledLast is not None:
			Debug.Log("Updating setting '" + Settings.Logging_Enabled.Key + "' to '" + str(loggingEnabledChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_loggingEnabled = loggingEnabledChange

	if loggingModeLast != loggingModeChange:
		if loggingModeLast is not None:
			Debug.Log("Updating setting '" + Settings.Logging_Mode.Key + "' to '" + str(loggingModeChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_loggingMode = loggingModeChange

	if writeChronologicalLast != writeChronologicalChange:
		if writeChronologicalLast is not None:
			Debug.Log("Updating setting '" + Settings.Write_Chronological.Key + "' to '" + str(writeChronologicalChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_writeChronological = writeChronologicalChange

	if writeGroupsLast != writeGroupsChange:
		if writeGroupsLast is not None:
			Debug.Log("Updating setting '" + Settings.Write_Groups.Key + "' to '" + str(writeGroupsChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_writeGroups = writeGroupsChange

	if burstLevelLast != burstLevelChange:
		if burstLevelLast is not None:
			Debug.Log("Updating setting '" + Settings.Burst_Level.Key + "' to '" + str(burstLevelChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_burstLevel = burstLevelChange

	if burstIntervalLast != burstIntervalChange:
		if burstIntervalLast is not None:
			Debug.Log("Updating setting '" + Settings.Burst_Interval.Key + "' to '" + str(burstIntervalChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_burstInterval = burstIntervalChange

	if continuousLevelLast != continuousLevelChange:
		if continuousLevelLast is not None:
			Debug.Log("Updating setting '" + Settings.Continuous_Level.Key + "' to '" + str(continuousLevelChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_continuousLevel = continuousLevelChange

	global _burstTimer

	if not loggingEnabledLast and loggingEnabledChange:
		_logger.ChangeLogFile()

		if _loggingMode == LoggingShared.LoggingModes.Burst:
			if _burstInterval > 0:
				if _burstTimer is not None:
					_burstTimer.Stop()
					_burstTimer = None

				_burstTimer = Timer.Timer(_burstInterval, _logger.Flush, repeat = True)
				_burstTimer.start()
	elif loggingEnabledLast and not loggingEnabledChange:
		if _loggingMode == LoggingShared.LoggingModes.Burst:
			if _burstInterval > 0 and _burstTimer is not None:
				_burstTimer.Stop()
				_burstTimer = None

			_logger.Flush()

	elif (loggingModeLast == LoggingShared.LoggingModes.Continuous or loggingModeLast is None) and loggingModeChange == LoggingShared.LoggingModes.Burst:
		if _burstInterval > 0:
			if _burstTimer is not None:
				_burstTimer.Stop()
				_burstTimer = None

			_burstTimer = Timer.Timer(_burstInterval, _logger.Flush, repeat = True)
			_burstTimer.start()
	elif loggingModeLast == LoggingShared.LoggingModes.Burst and loggingModeChange == LoggingShared.LoggingModes.Continuous:
		if _burstInterval > 0 and _burstTimer is not None:
			_burstTimer.Stop()
			_burstTimer = None

		_logger.Flush()

	elif burstIntervalLast != burstIntervalChange:
		if _loggingMode == LoggingShared.LoggingModes.Burst:
			if burstIntervalChange > 0:
				if _burstTimer is None:
					_burstTimer = Timer.Timer(_burstInterval, _logger.Flush, repeat = True)
					_burstTimer.start()
				else:
					_burstTimer.Interval = _burstInterval

	if loggingModeLast == LoggingShared.LoggingModes.Burst and ((writeChronologicalLast and not writeChronologicalChange) or (writeGroupsLast and not writeGroupsChange)):
		_logger.Flush()

def _Debug (group: str, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	if args:
		message = message.format(*args)

	if trigger_breakpoint:
		pass

	_logger.Log(message, Debug.LogLevels.Debug, group = group, owner = owner)

def _LoggerDebug (self: log.Logger, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	owner = owner or self.default_owner
	_Debug(self.group, message, *args, owner = owner, trigger_breakpoint = trigger_breakpoint)

def _Info (group: str, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	if args:
		message = message.format(*args)

	if trigger_breakpoint:
		pass

	_logger.Log(message, Debug.LogLevels.Info, group = group, owner = owner)

def _LoggerInfo (self: log.Logger, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	owner = owner or self.default_owner
	_Info(self.group, message, *args, owner = owner, trigger_breakpoint = trigger_breakpoint)

def _Warning (group: str, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	if args:
		message = message.format(*args)

	if trigger_breakpoint:
		pass

	_logger.Log(message, Debug.LogLevels.Warning, group = group, owner = owner)

def _LoggerWarning (self: log.Logger, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	owner = owner or self.default_owner
	_Warning(self.group, message, *args, owner = owner, trigger_breakpoint = trigger_breakpoint)

def _Error (group: str, message: str, *args, owner: str = None, trigger_breakpoint: bool = False) -> None:
	if args:
		message = message.format(*args)

	if trigger_breakpoint:
		pass

	_logger.Log(message, Debug.LogLevels.Error, group = group, owner = owner)

def _LoggerError (self: log.Logger, message: str, *args, owner: str = None, trigger_breakpoint: bool = False, trigger_callback_on_error_or_exception: bool = True) -> None:
	owner = owner or self.default_owner

	if trigger_callback_on_error_or_exception:
		pass

	_Error(self.group, message, *args, owner = owner, trigger_breakpoint = trigger_breakpoint)

# noinspection SpellCheckingInspection
def _Exception (group: str, message: str, *args, exc: BaseException = None, log_current_callstack: bool = True, frame: types.FrameType = log.DEFAULT, use_format_stack: bool = False, level: int = log.LEVEL_EXCEPTION, owner: str = None):
	if args:
		message = message.format(*args)

	if use_format_stack:
		pass

	_logger.Log(message, Debug.ConvertEALevelToLogLevel(level), group = group, owner = owner, exception = exc, logStack = log_current_callstack, frame = frame)

_Setup()
