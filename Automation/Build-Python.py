
if __name__ == "__main__":
	import os
	import sys
	from importlib import util
		
	sys.path.append(os.path.join(os.path.dirname(__file__), "NeonOcean.S4.Debug"))
	Main = util.find_spec("Mod_NeonOcean_S4_Debug.Main").loader.load_module()
		
	Main.BuildMod("Python")