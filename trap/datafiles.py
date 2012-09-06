
import os
from os import path

def files_in_folder(folder, extension=".fits"):
    """
    :param folder: what folder to use
    :param extension: only use files with this extention
    :return: returns a list of full paths to the files in the folder
    """
    return sorted([path.join(folder, x) for x in os.listdir(folder) if x.endswith(extension)])



