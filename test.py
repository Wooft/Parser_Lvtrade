import os
import pathlib

lists = os.walk(os.path.join(pathlib.Path.cwd(), 'details'))

for list in lists:
    print(list)