#!/usr/bin/env python3
#SaveMyCode! dropbox module (alpha3)
#Released under GNU General Public License
#Copyright 2015, Aswin Babu K

#import some serious stuff
import dropbox
import webbrowser
import os

#how does normal connection happen?
#fix this problem right now!

#read archive information from fail log
def read_fail_log():
	user_dir = '/home/' + os.getlogin();
	fail_log = open (user_dir + '/.smc/fail_log.txt', 'r')
	failed_inf = []

	for line in fail_log:
		archive_name = fail_log.readline()
		directory_name = fail_log.readline()
		path = fail_log.readline()

		failed_inf.append ({'archive_name': archive_name, 'directory_name': directory_name, 'path': path})

	fail_log.close()
	return failed_inf

#authorize the connection
def authorize():
	flow = dropbox.client.DropboxOAuth2FlowNoRedirect('2kfapc10x9248f1', '5xuqi4a04wgcuz9')
	authorize_url = flow.start()
	webbrowser.open (authorize_url)
	return flow

#get the access token from the dropbox server, also an object is passed
def get_token (authorize_code, flow):
	access_token, user_id = flow.finish (authorize_code)
	return access_token

#test if a link is available
def test_connection (access_token):
	client = dropbox.client.DropboxClient (access_token)
	
	if client.account_info():
		return client.account_info()
	return 0

#upload the files
def upload_file (archive_info):
	user_dir = '/home/' + os.getlogin()
	test_path = archive_info[0].path
	archive_path = test_path
	fail_log = open (user_dir + '/.smc/fail_log.txt', 'w')
	index = 0
	return_value = 0

	while archive_path == test_path:
		archive_name = archive_info[index].archive_name
		directory_name = archive_info[index].directory_name

		archive_file = open (os.path.join (archive_path, archive_name), 'rb')
		response = client.put_file ('/' + directory_name + '/' + archive_name, archive_file)

		if response == '503':
			return_value = 1
			fail_log.write (archive_name + '\n' + directory_name + '\n' + archive_path)

		index += 1
		archive_path = archive_info[index].path

	fail_log.close()
	return return_value
