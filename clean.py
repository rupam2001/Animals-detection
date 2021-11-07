'''
    to clean the images in root 
'''
pattern = r".png"

import os
import re

files = os.listdir(".")

for file in files:
    found = re.search(pattern, file)
    if found:
        os.remove(file)