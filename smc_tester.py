#!/usr/bin/env python3
#SaveMyCode! tester module (alpha3)
#Released under GNU General Public License
#Copyright 2015, Aswin Babu K

#import some important stuff
import linecache
import random
import os

#change pwd to /opt/smc_alpha3
os.chdir ('/opt/smc_alpha3')

#read the input folder path
in_dir = linecache.getline ('in_dir.inf', 1).rstrip()

#generate a file name and path
file_name = str (random.random())
file_path = os.path.join (in_dir, file_name)

#create the dummy file
dummy_file = open (file_path, 'w')

#fill up the file
dummy_file.write ('dummy file!');

#close the file
dummy_file.close()
