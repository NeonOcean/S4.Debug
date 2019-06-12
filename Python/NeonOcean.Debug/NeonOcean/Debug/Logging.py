import datetime
import os
import sys
import traceback
import types
import typing
from xml.sax import saxutils

import enum
import singletons
from NeonOcean.Debug import Settings, This
from NeonOcean.Main import Debug, DebugShared, LoadingShared, Paths, Language
from NeonOcean.Main.Tools import Exceptions, Parse, Patcher, Timer
from sims4 import log

_preload = True  # type: bool
_exiting = False  # type: bool

_loggingEnabled = None  # type: bool
_writeChronological = None  # type: bool
_writeGroups = None  # type: bool
_logLevel = None  # type: Debug.LogLevels
_logInterval = None  # type: float

_flushTicker = None  # type: Timer.Timer

_logger = None  # type: _Logger

class Report:
	def __init__ (self, logNumber: int, logTime: str, message: str,
				  level: Debug.LogLevels, group: str = None, owner: str = None,
				  exception: BaseException = None, logStack: bool = False,
				  stacktrace: str = None, retryOnError: bool = False):
		self.LogNumber = logNumber  # type: int
		self.LogTime = logTime  # type: str
		self.Message = message  # type: str
		self.Level = level  # type: Debug.LogLevels
		self.Group = group  # type: typing.Optional[str]
		self.Owner = owner  # type: typing.Optional[str]
		self.Exception = exception  # type: typing.Optional[BaseException]
		self.LogStack = logStack  # type: bool
		self.Stacktrace = stacktrace  # type: typing.Optional[str]
		self.RetryOnError = retryOnError  # type: bool

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

		if self.Exception is not None:
			logTemplate += "\t\t<Exception><!--\n" \
						   "\t\t\t-->{}<!--\n" \
						   "\t\t--></Exception>\n"

			exceptionText = DebugShared.FormatException(self.Exception)  # type: str
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

class _Logger(DebugShared.Logger):
	WriteFailureNotificationTitle = Language.String(This.Mod.Namespace + ".System.Debug.Write_Failure_Notification.Title")
	WriteFailureNotificationText = Language.String(This.Mod.Namespace + ".System.Debug.Write_Failure_Notification.Text")

	def __init__ (self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.CurrentLogNumber = 0

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

		self.CurrentLogNumber += 1

		if _logLevel is not None:
			if level > _logLevel:
				return

		report = Report(self.CurrentLogNumber, datetime.datetime.now().isoformat(), str(message),
						level = level, group = str(group), owner = owner,
						exception = exception, logStack = logStack, stacktrace = str.join("", traceback.format_stack(f = frame)))  # type: Report

		self._reportStorage.append(report)

		if _logInterval == 0:
			self.Flush()

	def _FilterReports (self, reports: typing.List[Report]) -> typing.List[Report]:
		def Filter (report: Report) -> bool:
			if _logLevel is not None:
				if report.Level > _logLevel:
					return False

			return True

		return list(filter(Filter, reports))

	def _LogAllReports (self, reports: typing.List[Report]) -> None:
		if not _writeChronological and not _writeGroups:
			return

		if len(reports) == 0:
			return

		chronologicalTextBytes = bytes()  # type: bytes
		groupsTextBytes = dict()  # type: typing.Dict[str, bytes]

		writeTime = datetime.datetime.now().isoformat()  # type: str

		for report in reports:  # type: Report
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

			if _writeGroups:
				if not os.path.exists(groupsLogDirectory):
					os.makedirs(groupsLogDirectory)

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

				retryingReports = filter(lambda filterReport: filterReport.RetryOnError, reports)  # type: typing.List[Report]
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
	Settings.RegisterUpdate(_UpdateSettings)

	_preload = False
	_logger.Flush()

def _OnStop (cause: LoadingShared.UnloadingCauses) -> None:
	global _exiting

	Settings.UnregisterUpdate(_UpdateSettings)

	_logger.Flush()

	if cause == LoadingShared.UnloadingCauses.Exiting:
		_exiting = True

def _UpdateSettings () -> None:
	global _loggingEnabled, _writeChronological, _writeGroups, _logLevel, _logInterval

	loggingEnabledChange = Settings.Get(Settings.LoggingEnabled.Key)  # type: bool
	writeChronologicalChange = Settings.Get(Settings.WriteChronological.Key)  # type: bool
	writeGroupsChange = Settings.Get(Settings.WriteGroups.Key)  # type: bool
	logLevelChange = Settings.Get(Settings.LogLevel.Key)  # type: str
	logLevelChange = Parse.ParseEnum(logLevelChange, Debug.LogLevels)  # type: Debug.LogLevels
	logIntervalChange = Settings.Get(Settings.LogInterval.Key)  # type: float

	loggingEnabledLast = _loggingEnabled  # type: bool
	writeChronologicalLast = _writeChronological  # type: bool
	writeGroupsLast = _writeGroups  # type: bool
	logLevelLast = _logLevel  # type: enum.EnumBase
	logIntervalLast = _logInterval  # type: float

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