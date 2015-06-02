#!/usr/bin/env python3
#SaveMyCode! service module (alpha3)
#Released under GNU General Public License
#Copyright 2014-2015, Aswin Babu K

#import some serious stuff
import sys
import os

#append the smc directory to path
sys.path.append ('/home/aswin/Project/smc_alpha3')

#import the stuff that i created
from smc_backup import *
from smc_dropbox import *

#set the user directory
user_dir = '/home/' + os.getlogin()

#tell the world that the program is alive
write_to_log ('SaveMyCode! service module (alpha3) started')

#check if all necessary files exists
write_to_log ('checking file integrity...')
if file_integrity_check() == 1:
	write_to_log ('error: integrity check failed, exiting!')
	sys.exit()

#read configuration settings
write_to_log ('reading settings...')

if read_configuration_file(1) == '1':
	write_to_log ('SaveMyCode! is disabled, skipping backup\n')
	sys.exit()

root_directory = (linecache.getline (user_dir + '/.smc/root_history.inf', 1)).rstrip()
archive_format = read_configuration_file(2)
check_interval = read_configuration_file(3)
smc_priority = read_configuration_file(4)
dropbox_enable = read_configuration_file(5)

#set priority of the program
write_to_log ('Setting priority of program to ' + smc_priority)
os.nice (int (smc_priority))

#check root directory for changes
if root_directory != 'None':
    if os.path.isfile (user_dir + '/.smc/sub_directory_list.inf'):
        write_to_log ('Checking root directory for new sub directories')
        
        old_sub_directory_set = set (read_directory_list (user_dir + '/.smc/sub_directory_list.inf'))
        new_sub_directory_set = list_root_directory (root_directory)
        set_difference = new_sub_directory_set.difference (old_sub_directory_set)

        if set_difference:
            write_to_log ('New sub directory found, notifying user...')
            draw_notification (set_difference)
    
    else:
        write_to_log ('Sub directory list does not exist, creating new file')
        
        sub_directory_set = list_root_directory (root_directory)
        sub_directory_list_file = open (user_dir + '/.smc/sub_directory_list.inf', 'w')
        
        for sub_directory in sub_directory_set:
            sub_directory_list_file.write (sub_directory + '\n')
        
        sub_directory_list_file.close()
            
#read input and output directory list
write_to_log ('reading directory lists...')
input_directory_list = read_directory_list (user_dir + '/.smc/in_dir.inf')
output_directory_list = read_directory_list (user_dir + '/.smc/out_dir.inf')

#check if the directory lists are empty
if not input_directory_list or not output_directory_list:
	write_to_log ('error: directory list is empty, exiting!')
	sys.exit()

#check for invalid entries in input directory list
write_to_log ('checking input directory structure')
input_directory_dictionary = check_directory_structure (input_directory_list, None)

if input_directory_dictionary['invalid']:
	write_to_log ('error: ' + str(input_directory_dictionary['invalid']) + ' are invalid!')

#get the input directory names to check if they exist, and create them if not
input_directory_name_list = get_directory_names (input_directory_dictionary['valid'])

#check for invalid entries in output directory list
write_to_log ('checking output directory structure')
output_directory_dictionary = check_directory_structure (output_directory_list, input_directory_name_list)

if output_directory_dictionary['invalid']:
	write_to_log ('error: ' + str(output_directory_dictionary['invalid']) + ' are invalid!')
	write_to_log ('creating output directories...')

	create_output_directories (output_directory_dictionary['invalid'])

if output_directory_dictionary['sub']:
	write_to_log ('error: ' + str(output_directory_dictionary['sub']) + ' are invalid!')
	write_to_log ('creating output sub-directories...')

	create_sub_directories (output_directory_dictionary['valid'], output_directory_dictionary['sub'])

if input_directory_dictionary['valid']:
	write_to_log ('checking for changes in input directories')
	backup_directory_list = check_for_changes (input_directory_dictionary['valid'])

	if backup_directory_list:
		write_to_log ('backing up directories...')
		archive_info = backup (output_directory_list, backup_directory_list, archive_format)

		#this is where the dropbox module should be invoked

	else:
		write_to_log ('no changes found, skipping backup')

else:
	write_to_log ('error: no vaid input directories found, skipping backup')

write_to_log ('exiting\n')
