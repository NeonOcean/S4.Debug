from __future__ import annotations

import datetime
import enum_lib
import os
import shutil
import sys
import traceback
import types
import typing

import singletons
from NeonOcean.S4.Debug import Settings, This
from NeonOcean.S4.Debug.Settings import Base as SettingsBase
from NeonOcean.S4.Main import Debug, DebugShared, Language, LoadingShared, Paths, Reporting
from NeonOcean.S4.Main.Tools import Exceptions, Parse, Patcher, Timer, Python
from sims4 import log

_preload = True  # type: bool
_exiting = False  # type: bool

_loggingEnabled = None  # type: typing.Optional[bool]
_writeChronological = None  # type: typing.Optional[bool]
_writeGroups = None  # type: typing.Optional[bool]
_logLevel = None  # type: typing.Optional[Debug.LogLevels]
_logInterval = None  # type: typing.Optional[float]
_logSizeLimit = None  # type: typing.Optional[float]

_flushTicker = None  # type: typing.Optional[Timer.Timer]

# noinspection PyTypeChecker
_logger = None  # type: _Logger

class _Logger(DebugShared.Logger):
	WriteFailureNotificationTitle = Language.String(This.Mod.Namespace + ".Write_Failure_Notification.Title")
	WriteFailureNotificationText = Language.String(This.Mod.Namespace + ".Write_Failure_Notification.Text")

	def __init__ (self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.LogCount = 0

	def Log (self, message, level: Debug.LogLevels, group: str = None,
			 owner: str = None, logStack: bool = False, exception: BaseException = None,
			 frame: types.FrameType = None) -> None:

		if not isinstance(level, int):
			raise Exceptions.IncorrectTypeException(level, "level", (int,))

		if not isinstance(group, str) and group is not None:
			raise Exceptions.IncorrectTypeException(group, "group", (str,))

		if not isinstance(owner, str) and owner is not None:
			raise Exceptions.IncorrectTypeException(owner, "owner", (str,))

		if not isinstance(exception, BaseException) and exception is not None:
			raise Exceptions.IncorrectTypeException(exception, "exception", (BaseException,))

		if not isinstance(logStack, bool):
			raise Exceptions.IncorrectTypeException(logStack, "logStack", (bool,))

		if isinstance(frame, singletons.DefaultType):
			frame = None

		if not isinstance(frame, types.FrameType) and frame is not None:
			raise Exceptions.IncorrectTypeException(frame, "frame", (types.FrameType,))

		if self._writeFailureCount >= self._writeFailureLimit:
			return

		if not _loggingEnabled and _loggingEnabled is not None:
			return

		if frame is log.DEFAULT:
			frame = None

		if exception is None:
			exception = sys.exc_info()[1]

		logCount = self.LogCount  # type: int
		self.LogCount += 1

		if _logLevel is not None:
			if level > _logLevel:
				return

		report = DebugShared.Report(None, logCount + 1, datetime.datetime.now().isoformat(),
									str(message), level = level, group = str(group),
									owner = owner, exception = exception, logStack = logStack,
									stacktrace = str.join("", traceback.format_stack(f = frame)))  # type: DebugShared.Report

		self._reportStorage.append(report)

		if _logInterval == 0:
			self.Flush()

	def GetLogSizeLimit (self) -> int:
		return int(_logSizeLimit * 1000000)

	def GetLogFilesToBeReported (self) -> typing.List[str]:
		"""
		Get the logs to be included in a report archive file. This should be limited to only some of the more recent logs.
		"""

		reportingLogFiles = list()  # type: typing.List[str]

		loggingRootPath = self.GetLoggingRootPath()  # type: str

		reportingLogDirectories = list()  # type: typing.List[str]

		latestLogFilePath = os.path.join(loggingRootPath, "Latest.xml")  # type: str

		if os.path.exists(latestLogFilePath):
			reportingLogFiles.append(latestLogFilePath)

		for logDirectoryName in reversed(os.listdir(loggingRootPath)):  # type: str
			if len(reportingLogDirectories) >= 10:
				break

			logDirectoryPath = os.path.join(loggingRootPath, logDirectoryName)  # type: str

			if not os.path.isdir(logDirectoryPath):
				continue

			try:
				datetime.datetime.strptime(logDirectoryName, "%Y-%m-%d %H.%M.%S.%f").timestamp()  # type: float
			except ValueError:
				Debug.Log("Found a directory in a logging namespace that did not meet the naming convention of 'Year-Month-Day Hour.Minute.Second.Microsecond'.\nDirectory Name: %s" % logDirectoryName,
						  This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__, lockIdentifier = __name__ + ":" + str(Python.GetLineNumber()), lockThreshold = 1)
				continue

			reportingLogDirectories.append(logDirectoryPath)

		for reportingLogDirectory in reportingLogDirectories:  # type: str
			reportingLogFilePath = os.path.join(reportingLogDirectory, "Log.xml")  # type: str

			if os.path.exists(reportingLogFilePath):
				reportingLogFiles.append(reportingLogFilePath)

			reportingSessionFilePath = os.path.join(reportingLogDirectory, "Session.json")  # type: str

			if os.path.exists(reportingSessionFilePath):
				reportingLogFiles.append(reportingSessionFilePath)

			reportingModFilePath = os.path.join(reportingLogDirectory, "Mods.txt")  # type: str

			if os.path.exists(reportingModFilePath):
				reportingLogFiles.append(reportingModFilePath)

		return reportingLogFiles

	def _FilterReports (self, reports: typing.List[DebugShared.Report]) -> typing.List[DebugShared.Report]:
		def Filter (report: DebugShared.Report) -> bool:
			if _logLevel is not None:
				if report.Level > _logLevel:
					return False

			return True

		return list(filter(Filter, reports))

	def _LogAllReports (self, reports: typing.List[DebugShared.Report]) -> None:
		if not _writeChronological and not _writeGroups:
			return

		if len(reports) == 0:
			return

		chronologicalTextBytes = bytes()  # type: bytes
		groupsTextBytes = dict()  # type: typing.Dict[str, bytes]

		writeTime = datetime.datetime.now().isoformat()  # type: str

		for report in reports:  # type: DebugShared.Report
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

		loggingRoot = self.GetLoggingRootPath()  # type: str

		loggingDirectory = os.path.join(loggingRoot, self.GetLoggingDirectoryName())  # type: str
		chronologicalFilePath = os.path.join(loggingDirectory, "Log.xml")  # type: str
		chronologicalFirstWrite = False  # type: bool
		latestChronologicalFilePath = os.path.join(loggingRoot, "Latest.xml")  # type: str

		groupsLoggingDirectory = os.path.join(loggingDirectory, "Groups")  # type: str

		sessionFilePath = os.path.join(loggingDirectory, "Session.txt")  # type: str
		modsDirectoryFilePath = os.path.join(loggingDirectory, "Mods Directory.txt")  # type: str

		logSizeLimit = self.GetLogSizeLimit()  # type: int
		logSizeLimitReachedBytes = "<!--Log file size limit reached-->".encode("utf-8")  # type: bytes

		logStartBytes = self.GetLogStartBytes()  # type: bytes
		logEndBytes = self.GetLogEndBytes()  # type: bytes

		lineSeparatorBytes = (os.linesep + os.linesep).encode("utf-8")  # type: bytes

		try:
			if not os.path.exists(loggingDirectory):
				os.makedirs(loggingDirectory)

			if _writeGroups:
				if not os.path.exists(groupsLoggingDirectory):
					os.makedirs(groupsLoggingDirectory)

			if not os.path.exists(sessionFilePath):
				with open(sessionFilePath, mode = "w+") as sessionFile:
					sessionFile.write(self._sessionInformation)

			if not os.path.exists(modsDirectoryFilePath):
				with open(modsDirectoryFilePath, mode = "w+") as modsFile:
					modsFile.write(self._modsDirectoryInformation)

			if _writeChronological:
				if not os.path.exists(chronologicalFilePath):
					chronologicalFirstWrite = True
				else:
					self._VerifyLogFile(chronologicalFilePath)

				if chronologicalFirstWrite:
					if len(logStartBytes) + len(chronologicalTextBytes) + len(logEndBytes) >= logSizeLimit >= 0:
						chronologicalTextBytes += logSizeLimitReachedBytes

					with open(chronologicalFilePath, mode = "wb+") as chronologicalFile:
						chronologicalFile.write(logStartBytes)
						chronologicalFile.write(chronologicalTextBytes)
						chronologicalFile.write(logEndBytes)

					if os.path.exists(latestChronologicalFilePath):
						os.remove(latestChronologicalFilePath)

					with open(latestChronologicalFilePath, mode = "wb+") as latestChronologicalFile:
						latestChronologicalFile.write(logStartBytes)
						latestChronologicalFile.write(chronologicalTextBytes)
						latestChronologicalFile.write(logEndBytes)
				else:
					logSize = os.path.getsize(chronologicalFilePath)  # type: int

					if logSizeLimit < 0 or logSize < logSizeLimit:
						if logSize + len(lineSeparatorBytes) + len(chronologicalTextBytes) + len(logEndBytes) >= logSizeLimit >= 0:
							chronologicalTextBytes += logSizeLimitReachedBytes

						with open(chronologicalFilePath, "r+b") as chronologicalFile:
							chronologicalFile.seek(-len(logEndBytes), os.SEEK_END)
							chronologicalFile.write(lineSeparatorBytes)
							chronologicalFile.write(chronologicalTextBytes)
							chronologicalFile.write(logEndBytes)

						try:
							self._VerifyLogFile(latestChronologicalFilePath)

							with open(latestChronologicalFilePath, "r+b") as latestChronologicalFile:
								latestChronologicalFile.seek(-len(logEndBytes), os.SEEK_END)
								latestChronologicalFile.write(lineSeparatorBytes)
								latestChronologicalFile.write(chronologicalTextBytes)
								latestChronologicalFile.write(logEndBytes)
						except:
							shutil.copy(chronologicalFilePath, latestChronologicalFilePath)

			for groupName, groupTextBytes in groupsTextBytes.items():  # type: str, bytes
				groupFilePath = os.path.join(groupsLoggingDirectory, groupName + ".xml")  # type: str
				groupFirstWrite = False  # type: bool

				if _writeGroups:
					if not os.path.exists(groupFilePath):
						groupFirstWrite = True
					else:
						self._VerifyLogFile(groupFilePath)

					if groupFirstWrite:
						if len(logStartBytes) + len(groupsTextBytes) + len(logEndBytes) >= logSizeLimit >= 0:
							groupsTextBytes += logSizeLimitReachedBytes

						with open(groupFilePath, mode = "wb+") as groupFile:
							groupFile.write(logStartBytes)
							groupFile.write(groupTextBytes)
							groupFile.write(logEndBytes)
					else:
						logSize = os.path.getsize(chronologicalFilePath)  # type: int

						if logSizeLimit < 0 or logSize < logSizeLimit:
							if logSize + len(lineSeparatorBytes) + len(groupsTextBytes) + len(logEndBytes) >= logSizeLimit >= 0:
								groupsTextBytes += logSizeLimitReachedBytes

							with open(groupFilePath, "r+b") as groupFile:
								groupFile.seek(-len(logEndBytes), os.SEEK_END)
								groupFile.write((os.linesep + os.linesep).encode("utf-8") + groupTextBytes)
								groupFile.write(logEndBytes)
		except Exception as e:
			self._writeFailureCount += 1

			if not getattr(self.DebugGlobal, self._globalShownWriteFailureNotification):
				self._ShowWriteFailureDialog(e)
				setattr(self.DebugGlobal, self._globalShownWriteFailureNotification, True)

			if self._writeFailureCount < self._writeFailureLimit:
				self.ChangeLogFile()

				retryingReports = list(filter(lambda filterReport: filterReport.RetryOnError, reports))  # type: typing.List[DebugShared.Report]
				retryingReportsLength = len(retryingReports)  # type: int

				Debug.Log("Forced to start a new log file after encountering a write error. " + str(len(reports) - retryingReportsLength) + " reports where lost because of this.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, retryOnError = False)

				for retryingReport in retryingReports:
					retryingReport.RetryOnError = False

				if retryingReportsLength != 0:
					self._LogAllReports(reports)

			return

def _Setup () -> None:
	global _logger

	_logger = _Logger(os.path.join(Paths.DebugPath, "Logs"))

def _DebugLogCollector () -> typing.List[str]:
	return _logger.GetLogFilesToBeReported()

def _OnStart (cause: LoadingShared.LoadingCauses) -> None:
	global _preload, _loggingEnabled, _writeChronological, _writeGroups, _logLevel, _logInterval

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
	Settings.RegisterOnUpdateCallback(_UpdateSettingsCallback)

	_preload = False
	_logger.Flush()

	Reporting.RegisterReportFileCollector(_DebugLogCollector)

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	global _exiting

	Settings.UnregisterOnUpdateCallback(_UpdateSettingsCallback)

	_logger.Flush()

	if cause == LoadingShared.UnloadingCauses.Exiting:
		_exiting = True

	Reporting.UnregisterReportFileCollector(_DebugLogCollector)

def _UpdateSettings () -> None:
	global _loggingEnabled, _writeChronological, _writeGroups, _logLevel, _logInterval, _logSizeLimit

	loggingEnabledChange = Settings.LoggingEnabled.Get()  # type: bool
	writeChronologicalChange = Settings.WriteChronological.Get()  # type: bool
	writeGroupsChange = Settings.WriteGroups.Get()  # type: bool
	logLevelChange = Settings.LogLevel.Get()  # type: str
	logLevelChange = Parse.ParsePythonEnum(logLevelChange, Debug.LogLevels)  # type: Debug.LogLevels
	logIntervalChange = Settings.LogInterval.Get()  # type: float
	logSizeLimitChange = Settings.LogSizeLimit.Get()  # type: float

	loggingEnabledLast = _loggingEnabled  # type: bool
	writeChronologicalLast = _writeChronological  # type: bool
	writeGroupsLast = _writeGroups  # type: bool
	logLevelLast = _logLevel  # type: enum_lib.Enum
	logIntervalLast = _logInterval  # type: float
	logSizeLimitLast = _logSizeLimit  # type: float

	if loggingEnabledLast != loggingEnabledChange:
		if loggingEnabledLast is not None:
			Debug.Log("Updating setting '" + Settings.LoggingEnabled.Key + "' to '" + str(loggingEnabledChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_loggingEnabled = loggingEnabledChange

	if writeChronologicalLast != writeChronologicalChange:
		if writeChronologicalLast is not None:
			Debug.Log("Updating setting '" + Settings.WriteChronological.Key + "' to '" + str(writeChronologicalChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_writeChronological = writeChronologicalChange

	if writeGroupsLast != writeGroupsChange:
		if writeGroupsLast is not None:
			Debug.Log("Updating setting '" + Settings.WriteGroups.Key + "' to '" + str(writeGroupsChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_writeGroups = writeGroupsChange

	if logLevelLast != logLevelChange:
		if logLevelLast is not None:
			Debug.Log("Updating setting '" + Settings.LogLevel.Key + "' to '" + str(logLevelChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_logLevel = logLevelChange

	if logIntervalLast != logIntervalChange:
		if logIntervalLast is not None:
			Debug.Log("Updating setting '" + Settings.LogInterval.Key + "' to '" + str(logIntervalChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_logInterval = logIntervalChange

	if logSizeLimitLast != logSizeLimitChange:
		if logSizeLimitLast is not None:
			Debug.Log("Updating setting '" + Settings.LogSizeLimit.Key + "' to '" + str(logSizeLimitChange) + "'.", This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

		_logSizeLimit = logSizeLimitChange

	global _flushTicker

	if not loggingEnabledLast and loggingEnabledChange:
		if loggingEnabledLast is not None:
			_logger.ChangeLogFile()

		if _flushTicker is not None:
			_flushTicker.Stop()
			_flushTicker = None

		if _logInterval != 0:
			_flushTicker = Timer.Timer(_logInterval, _logger.Flush, repeat = True)
			_flushTicker.start()

	elif loggingEnabledLast and not loggingEnabledChange:
		if _flushTicker is not None:
			_flushTicker.Stop()
			_flushTicker = None

		_logger.Flush()

	elif (logIntervalLast == 0 or logIntervalLast is None) and logIntervalChange != 0:
		if _flushTicker is not None:
			_flushTicker.Stop()
			_flushTicker = None

		_flushTicker = Timer.Timer(_logInterval, _logger.Flush, repeat = True)
		_flushTicker.start()

	elif logIntervalLast != 0 and logIntervalChange == 0:
		if _flushTicker is not None:
			_flushTicker.Stop()
			_flushTicker = None

		_logger.Flush()

	elif logIntervalLast != logIntervalChange:
		if logIntervalChange != 0:
			if _flushTicker is None:
				_flushTicker = Timer.Timer(_logInterval, _logger.Flush, repeat = True)
				_flushTicker.start()
			else:
				_flushTicker.Interval = _logInterval

	if loggingEnabledLast is None and not loggingEnabledChange:
		_logger._reportStorage = list()

	if logIntervalLast != 0 and ((writeChronologicalLast and not writeChronologicalChange) or (writeGroupsLast and not writeGroupsChange)):
		_logger.Flush()

# noinspection PyUnusedLocal
def _UpdateSettingsCallback (owner: types.ModuleType, eventArguments: SettingsBase.UpdateEventArguments) -> None:
	_UpdateSettings()

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

	_logger.Log(message, DebugShared.ConvertEALevelToLogLevel(level), group = group, owner = owner, exception = exc, logStack = log_current_callstack, frame = frame)

_Setup()
