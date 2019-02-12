import os

		for root, dirs, files in os.walk(os.getcwd()):
			for name in files:
				if name.endswith("mp4"):
					os.remove(os.path.join(root, name))
					print ("Delete File: " + os.path.join(root, name))
				if name.endswith("txt"):
					os.remove(os.path.join(root, name))
					print ("Delete File: " + os.path.join(root, name))