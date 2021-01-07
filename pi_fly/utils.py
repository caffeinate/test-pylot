'''
Created on 7 Jan 2021

@author: si
'''
import os

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))


def load_from_file(filepath):
    """
    Return contents of a file. Used as a simple loader for the password instead of using env vars.

    Args:
        filepath (str) filename with path *relative* to `pi_fly` project directory.

    Returns:
        (str)
    """
    abs_file_path = os.path.join(PROJECT_PATH, filepath)
    with open(abs_file_path, 'r') as f:
        f_content = f.read()
    return f_content
