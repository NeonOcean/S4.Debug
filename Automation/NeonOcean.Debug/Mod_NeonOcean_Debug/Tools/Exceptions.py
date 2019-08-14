import traceback
import types
import typing

def FormatException (exception: BaseException) -> str:
	return str.join("", traceback.format_exception(type(exception), exception, exception.__traceback__))

class IncorrectTypeException(Exception):
	def __init__ (self, value, valueName: str, correctTypes: typing.Tuple[typing.Union[type, str, None], ...], *additional):
		"""
		This exception will display error messages such as: 'Expected type 'builtins.str' not 'builtins.int' for 'parameter 1'."

		:param value: The incorrectly typed value. When converting the exception to a string it will display the full name of the value's type.
		:param valueName: Use this to provide information on what is incorrect.
		:type valueName: str
		:param correctTypes: A iterable object containing any possibly correct types. The entries can be either a type or a string object.
							 If an entry is a type, when converting the exception to a string it will display the full name of the type.
		:type correctTypes: typing.Tuple[typing.Union[type, str], typing.Any]
		"""

		if not isinstance(valueName, str):
			raise IncorrectTypeException(valueName, "valueName", (str,))

		if not isinstance(correctTypes, tuple):
			raise IncorrectTypeException(correctTypes, "correctTypes", (tuple,))

		if len(correctTypes) == 0:
			raise Exception("This exception must receive at least one correct type")

		for correctTypeIndex in range(len(correctTypes)):  # type: int
			if not isinstance(correctTypes[correctTypeIndex], type) and not (not isinstance(correctTypes[correctTypeIndex], type) and isinstance(correctTypes[correctTypeIndex], str)):
				raise IncorrectTypeException(correctTypes[correctTypeIndex], "correctTypes[%d]" % correctTypeIndex, (type, str))

		self._value = value  # type: type
		self._valueName = valueName  # type: str
		self._correctTypes = correctTypes  # type: typing.Tuple[typing.Union[type, str], typing.Any]
		self._additional = additional  # type: typing.Tuple[typing.Any, ...]

		super().__init__((value, valueName, correctTypes, *additional))

	def __str__ (self):
		return GetIncorrectTypeExceptionText(self._value, self._valueName, self._correctTypes, *self._additional)

def GetIncorrectTypeExceptionText (value, valueName: str, correctTypes: typing.Tuple[typing.Union[type, str, None], ...], *additional):
	if not isinstance(valueName, str):
		raise IncorrectTypeException(valueName, "valueName", (str,))

	if not isinstance(correctTypes, tuple):
		raise IncorrectTypeException(correctTypes, "correctTypes", (tuple,))

	if len(correctTypes) == 0:
		raise Exception("This exception must receive at least one correct type")

	for correctTypeIndex in range(len(correctTypes)):  # type: int
		if isinstance(correctTypes[correctTypeIndex], type):
			continue

		if isinstance(correctTypes[correctTypeIndex], str):
			continue

		if correctTypes[correctTypeIndex] is None:
			continue

		raise IncorrectTypeException(correctTypes[correctTypeIndex], "correctTypes[%d]" % correctTypeIndex, (type, str, None))

	valueType = type(value)

	correctString = "'{}'" + (", '{}'" * (len(correctTypes) - 2) if len(correctTypes) > 2 else "") + (" or '{}'" if len(correctTypes) > 1 else "")

	formatList = list()

	for correctTypeIndex in range(0, len(correctTypes)):
		if isinstance(correctTypes[correctTypeIndex], type) or correctTypes[correctTypeIndex] is None:
			formatList.append(_GetFullName(correctTypes[correctTypeIndex]))
		elif isinstance(correctTypes[correctTypeIndex], str):
			formatList.append(correctTypes[correctTypeIndex])
		else:
			formatList.append("")

	formatList.append(_GetFullName(valueType))
	formatList.append(valueName)

	exceptionString = ("Expected type " + correctString + " not '{}' for '{}'").format(*formatList)

	for additionalObject in additional:  # type: typing.Any
		exceptionString += "\n" + str(additionalObject)

	return exceptionString

def _GetFullName (obj) -> str:
	"""
	:param obj: Takes builtin function, function, method, type, or object.
	:return: The full name of a built-in function, function, method, type or object's type, including the module.
	"""

	if isinstance(obj, types.BuiltinFunctionType):
		return _GetBuiltinFunctionFullName(obj)
	if isinstance(obj, types.FunctionType):
		return _GetFunctionFullName(obj)
	if isinstance(obj, types.MethodType):
		return _GetMethodFullName(obj)
	if isinstance(obj, type):
		return _GetTypeFullName(obj)
	else:
		return _GetTypeFullName(type(obj))

def _GetBuiltinFunctionFullName (obj: types.BuiltinFunctionType) -> str:
	if obj.__module__ is not None:
		return obj.__module__ + "." + obj.__name__
	else:
		return obj.__name__

def _GetFunctionFullName (obj: types.FunctionType) -> str:
	if obj.__module__ is not None:
		return obj.__module__ + "." + obj.__qualname__
	else:
		return obj.__qualname__

def _GetMethodFullName (obj: types.MethodType) -> str:
	if obj.__module__ is not None:
		return obj.__module__ + "." + obj.__func__.__qualname__
	else:
		return obj.__func__.__qualname__

def _GetTypeFullName (obj: type) -> str:
	if obj.__module__ is not None:
		return obj.__module__ + "." + obj.__qualname__
	else:
		return obj.__qualname__
