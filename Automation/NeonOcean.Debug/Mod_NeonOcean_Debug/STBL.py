import sys
import os
import typing
from xml.etree import ElementTree

from Mod_NeonOcean_Debug import Mod

def GetEntries () -> typing.List[typing.Tuple[str, int]]:
	entries = list()  # type: typing.List[typing.Tuple[str, int]]

	for package in Mod.GetCurrentMod().Packages:  # type: Mod.Package
		if not os.path.exists(package.STBLPath):
			continue

		if os.path.exists(package.STBLPath):
			for stblXMLFileName in os.listdir(package.STBLPath):  # type: str
				stblXMLFilePath = os.path.join(package.STBLPath, stblXMLFileName)  # type: str

				if os.path.isfile(stblXMLFilePath) and os.path.splitext(stblXMLFileName)[1].casefold() == ".xml":
					try:
						stblXMLFile = ElementTree.parse(stblXMLFilePath)  # type: ElementTree.ElementTree
						entriesElements = stblXMLFile.findall("Entries/STBLXMLEntry")  # type: typing.Optional[typing.List[ElementTree.Element]]

						if entriesElements is None:
							continue

						for entryElement in entriesElements:  # type: ElementTree.Element
							entryIdentifierElement = entryElement.find("Identifier")  # type: ElementTree.Element
							entryKeyElement = entryElement.find("Key")  # type: ElementTree.Element

							if entryIdentifierElement is None or entryKeyElement is None:
								continue

							entryIdentifier = entryIdentifierElement.text  # type: str
							entryKeyText = entryKeyElement.text  # type: str
							entryKey = int(entryKeyText)  # type: int

							entries.append((entryIdentifier, entryKey))
					except Exception as e:
						print("Failed to read potential stbl xml file at '" + stblXMLFilePath + "'\n" + str(e), file = sys.stderr)
						continue

	return entries