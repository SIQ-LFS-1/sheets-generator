# Python Script to perform Git-Pull...

import os


def pull():  # Function Definition...
    os.system("git stash")
    os.system("git pull")


# Function Call...
pull()
