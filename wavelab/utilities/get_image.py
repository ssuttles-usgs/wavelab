"""
Module to get the directory location of an image
depending on if the code is being run as a frozen executable
"""

import sys
import os


def get_image(image_name):

    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = os.path.join(sys._MEIPASS,'images')
    else:
        file_dir = os.path.dirname(__file__)
        application_path = os.path.join(file_dir, "../images")
        print(application_path)

    return os.path.join(application_path, image_name)
