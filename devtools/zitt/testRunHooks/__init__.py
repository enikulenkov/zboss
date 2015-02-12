import os
import glob

# Copied from here
# http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules]
