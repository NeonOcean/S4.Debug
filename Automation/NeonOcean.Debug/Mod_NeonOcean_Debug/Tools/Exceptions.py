import traceback

def FormatException (exception: BaseException) -> str:
	return str.join("", traceback.format_exception(type(exception), exception, exception.__traceback__))
