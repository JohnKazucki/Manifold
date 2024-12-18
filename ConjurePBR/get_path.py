import os


# --- Adapted from Machin3tools
# This code assumes your folder name is the name of your addon
# It also assumes that this function is placed inside a .py file in the base folder

# get the folder path for the .py file containing this function
def get_path():
    return os.path.dirname(os.path.realpath(__file__))


# get the name of the "base" folder
def get_name():
    return os.path.basename(get_path())

def get_addon_location():
    return os.path.dirname(os.path.abspath(__file__))
