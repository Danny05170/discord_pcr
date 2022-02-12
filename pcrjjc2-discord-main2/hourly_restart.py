# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 03:25:55 2022

@author: danny
"""
import subprocess
from subprocess import PIPE

comp_process = subprocess.run("ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs -r kill -9",stdout=PIPE, stderr=PIPE)
print(comp_process.stdout)