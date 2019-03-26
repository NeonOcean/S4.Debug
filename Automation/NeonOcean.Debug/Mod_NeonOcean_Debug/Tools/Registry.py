import platform
import traceback

def FormatException (exception: BaseException) -> str:
	return str.join("", traceback.format_exception(type(exception), exception, exception.__traceback__))

def ReadRegistry (keyRoot: int, keyDirectory: str, keyEntry: str):
	if platform.system() != "Windows":
		raise Exception("Cannot read registry as it is only available on windows.")

	import winreg

	try:
		openedKeyDirectory = winreg.OpenKey(keyRoot, keyDirectory, access = (winreg.KEY_WOW64_32KEY | winreg.KEY_READ))  # type: winreg.HKEYType
		keyValue = winreg.QueryValueEx(openedKeyDirectory, keyEntry)[0]
		openedKeyDirectory.Close()

		return keyValue
	except:
		try:
			openedKeyDirectory = winreg.OpenKey(keyRoot, keyDirectory, access = (winreg.KEY_WOW64_64KEY | winreg.KEY_READ))  # type: winreg.HKEYType
			keyValue = winreg.QueryValueEx(openedKeyDirectory, keyEntry)[0]
			openedKeyDirectory.Close()

			return keyValue
		except:
			pass

	raise Exception("Cannot find registry key for, Root ID: " + str(keyRoot) + " Directory: " + keyDirectory + " Entry: " + keyEntry)

def ReadRegistryFullKey (fullKey: str):
	if platform.system() != "Windows":
		raise Exception("Cannot read registry as it is only available on windows.")

	if fullKey.count("\\") < 1:
		return

	keyRoot = _GetRegistryKeyRoot(fullKey)  # type: int

	keyDirectory = ""
	if fullKey.count("\\") >= 2:
		keyDirectory = fullKey[fullKey.index("\\"): fullKey.rfind("\\")].lstrip("\\")  # type: str

	keyEntry = fullKey[fullKey.rfind("\\"):].lstrip("\\")  # type: str

	return ReadRegistry(keyRoot, keyDirectory, keyEntry)

def _GetRegistryKeyRoot (path: str) -> int:
	if platform.system() != "Windows":
		raise Exception("Cannot find the registry key's root as the registry is only available on windows.")

	import winreg

	rootString = path[: path.index("\\")].upper()  # type: str

	root = None  # type: int
	if rootString == "HKEY_CLASSES_ROOT":
		root = winreg.HKEY_CLASSES_ROOT
	elif rootString == "HKEY_CURRENT_CONFIG":
		root = winreg.HKEY_CURRENT_CONFIG
	elif rootString == "HKEY_CURRENT_USER":
		root = winreg.HKEY_CURRENT_USER
	elif rootString == "HKEY_LOCAL_MACHINE":
		root = winreg.HKEY_LOCAL_MACHINE
	elif rootString == "HKEY_USERS":
		root = winreg.HKEY_USERS

	if root is None:
		raise Exception(rootString + " is not a valid root.")

	return root
