#!/usr/bin/env python3
#SaveMyCode! backup module (alpha3)
#Released under GNU General Public License
#Copyright 2014-2015, Aswin Babu K

#import some serious stuff
import time
import linecache
import os
import shutil
from crontab import CronTab
import notify2
from gi.repository import Gtk

'''
#what to do when add button is clicked
def add_button_click (notification, action, set_difference):
    notification.close()
    return 1

#what to do when ignore button is clicked
def ignore_button_click (notification, action, set_difference):
    return 0
'''

#close the notification
def close_notification (notification):
    Gtk.main_quit()

#draw a simple notification
def draw_notification (set_difference):
    notify2.init ('SaveMyCode!', mainloop='glib')
    server_capability = notify2.get_server_caps()
    notification = notify2.Notification ('Starting work on a new project?',
                                         'Should I add the new folder in root directory to the list of ' +
                                         'input directories?')
    
    if 'actions' in server_capability:
        notification.add_action ('add', 'Add', add_sub_directory, set_difference)
        notification.add_action ('ignore', 'Ignore', ignore_sub_directory, set_difference)
    notification.connect ('closed', close_notification)
    
    notification.show()
    Gtk.main()

#add the sub directory to the input directory list
def add_sub_directory (notification, action, set_difference):
    user_dir = '/home/' + os.getlogin()
    input_directory_list_file = open (user_dir + '/.smc/in_dir.inf', 'a')
    sub_directory_list_file = open (user_dir + '/.smc/sub_directory_list.inf', 'a')

    for sub_directory in set_difference:
        input_directory_list_file.write (sub_directory + '\n')
        sub_directory_list_file.write (sub_directory + '\n')
    
    notification.close()
    
#ignore the sub directory, and add it to sub directory list
def ignore_sub_directory (notification, action, set_difference):
    user_dir = '/home/' + os.getlogin()
    sub_directory_list_file = open (user_dir + '/.smc/sub_directory_list.inf', 'a')

    for sub_directory in set_difference:
        sub_directory_list_file.write (sub_directory + '\n')

    sub_directory_list_file.close()

#list all directories under root directory
def list_root_directory (root_directory_path):
    sub_directory_set = set()
    for sub_directory in os.listdir (root_directory_path):
        path_to_sub_directory = os.path.join (root_directory_path, sub_directory)

        if os.path.isdir (path_to_sub_directory):
            sub_directory_set.add (path_to_sub_directory)

    return set (sub_directory_set)

#set up cron according to settings
def set_up_cron (check_interval, path_to_exec):
        user_cron = CronTab (user=True)
        smc_job = None

        for line in user_cron:
                if line.command == path_to_exec:
                        smc_job = line

        if not smc_job:
                smc_job = user_cron.new (command=path_to_exec)

        smc_job.minute.every (check_interval)
        user_cron.write_to_user (user=True)


#backup the directories
def backup(output_directory_list, backup_directory_list, archive_format):
        original_working_directory = os.getcwd()
        archive_info = []

        for output_directory_path in output_directory_list:
                for backup_directory_path in backup_directory_list:

                        backup_directory_name = os.path.basename (backup_directory_path)
                        archive_path = os.path.join (output_directory_path, backup_directory_name)
                        os.chdir (archive_path)

                        backup_archive_name = '[' + backup_directory_name + ']'
                        backup_archive_name += time.strftime ('[%d%b%y][%H%M%S]')

                        shutil.make_archive (backup_archive_name, archive_format, backup_directory_path)

                        archive_info.append ({'archive_name': backup_archive_name,
                                                                'directory_name': backup_directory_name, 'path': archive_path})

        os.chdir (original_working_directory)
        return archive_info

#check for changes
def check_for_changes (input_directory_list):
        backup_directory_list = []
        original_working_directory = os.getcwd()

        for path in input_directory_list:
                os.chdir (path)
                current_checksum = 0
                old_checksum = 0

                for location, directories, files in os.walk (path):
                        for each_file in files:
                                current_checksum += os.path.getsize (os.path.join (location, each_file))

                if os.path.isfile ('checksum.inf'):
                        checksum_file = open ('checksum.inf', 'r')
                        line_from_file = checksum_file.readline()
                        checksum_file.close()

                        old_checksum = int (line_from_file.rstrip('\n'))

                if current_checksum != old_checksum:
                        checksum_file = open ('checksum.inf', 'w')
                        checksum_file.write (str(current_checksum))
                        checksum_file.close()
                        backup_directory_list.append (path)

        os.chdir (original_working_directory)
        return backup_directory_list

#creates directory structure
def create_output_directories (invalid_directory_list):
        for path in invalid_directory_list:
                os.mkdir (path)

#create the sub directories in output directories
def create_sub_directories (output_directory_list, sub_directory_name_list):
        for output_path in output_directory_list:
                for sub_directory_name in sub_directory_name_list:

                        os.mkdir (os.path.join (output_path, sub_directory_name))

#returns directory names from their path
def get_directory_names (directory_list):
        directory_name_list = []

        for directory_path in directory_list:
                directory_name = os.path.basename (directory_path)
                directory_name_list.append (directory_name)

        return directory_name_list

#checks if the directories passed on to it exists
def check_directory_structure (directory_list, input_directory_name_list):
        invalid_directory_list = []
        valid_directory_list = []
        sub_directory_list = []

        for path in directory_list:
                if os.path.exists (path):
                        valid_directory_list.append (path)

                        if input_directory_name_list != None:
                                for directory_name in input_directory_name_list:

                                        if os.path.exists (os.path.join (path, directory_name)):
                                                continue
                                        else:
                                                sub_directory_list.append (directory_name)
                else:
                        invalid_directory_list.append (path)

        return {'invalid': invalid_directory_list, 'valid': valid_directory_list, 'sub':sub_directory_list}

#read the list of directories from hard drive
def read_directory_list (file):
    directory_list = []
    directory_file = open (file)

    for line_from_file in directory_file:
        directory_list.append (line_from_file.rstrip())

    directory_file.close()
    return directory_list

#check if the necessary files for running the programs exist
def file_integrity_check():
        user_dir = '/home/' + os.getlogin()
        if os.path.exists (user_dir + '/.smc/config.inf'):
                if os.path.exists (user_dir + '/.smc/in_dir.inf'):
                        if os.path.exists (user_dir + '/.smc/out_dir.inf'):
                                return 0
        return 1

#reads the configuration file [write the better algorithm]
def read_configuration_file (line):
        user_dir = '/home/' + os.getlogin()
        line_from_file = linecache.getline (user_dir + '/.smc/config.inf', line)
        start_of_string = line_from_file.find ('=') + 1
        configuration_value = line_from_file [start_of_string:]
        return configuration_value.rstrip()

#writes data to the log file
def write_to_log (matter):
        user_dir = '/home/' + os.getlogin()
        log_file = open (user_dir + '/.smc/log.txt', 'a')

        log_file.write (time.strftime('[%d-%b-%Y %H:%M:%S] '))
        log_file.write (matter + '\n')

        log_file.close()
