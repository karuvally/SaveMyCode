#!/usr/bin/env python3
#SaveMyCode! GUI module (alpha3)
#Released under GNU General Public License
#Copyright 2015, Aswin Babu K

#import some serious stuff
import sys
import os

#import some stuff written by me
from smc_gui import *
from smc_backup import read_configuration_file, set_up_cron

class main_window (QtGui.QDialog):
	def __init__ (self, parent=None):
		self.user_dir = '/home/' + os.getlogin()
		QtGui.QWidget.__init__ (self, parent)

		self.ui = Ui_Dialog()
		self.ui.setupUi (self)
		
		self.read_file (self.user_dir + '/.smc/in_dir.inf', self.ui.listWidget_in)
		self.read_file (self.user_dir + '/.smc/out_dir.inf', self.ui.listWidget_out)
		self.read_file (self.user_dir + '/.smc/root_history.inf', self.ui.comboBox_root)

		self.set_up_settings()
		self.initialize_settings()
		
		QtCore.QObject.connect (self.ui.pushButton_add_in, QtCore.SIGNAL ('clicked()'), lambda: self.add_path (self.ui.listWidget_in))
		QtCore.QObject.connect (self.ui.pushButton_remove_in, QtCore.SIGNAL ('clicked()'), lambda: self.remove_path (self.ui.listWidget_in))
		
		QtCore.QObject.connect (self.ui.pushButton_add_out, QtCore.SIGNAL ('clicked()'), lambda: self.add_path (self.ui.listWidget_out))
		QtCore.QObject.connect (self.ui.pushButton_remove_out, QtCore.SIGNAL ('clicked()'), lambda: self.remove_path (self.ui.listWidget_out))
		
		QtCore.QObject.connect (self.ui.pushButton_add_root, QtCore.SIGNAL ('clicked()'), lambda: self.add_path (self.ui.comboBox_root))
		QtCore.QObject.connect (self.ui.pushButton_remove_root, QtCore.SIGNAL ('clicked()'), lambda: self.ui.comboBox_root.removeItem(self.ui.comboBox_root.currentIndex()))

		QtCore.QObject.connect (self.ui.pushButton_apply, QtCore.SIGNAL ('clicked()'), self.apply_settings)
		QtCore.QObject.connect (self.ui.pushButton_close, QtCore.SIGNAL ('clicked()'), sys.exit)

	def initialize_settings (self):
		self.ui.comboBox_enable.setCurrentIndex (int (read_configuration_file (1)))
		
		self.ui.comboBox_root.setCurrentIndex (0)
		
		archive_dictionary = {'zip': 0, 'tar': 1, 'bztar': 2, 'gztar': 3}
		archive_format = read_configuration_file (2)
		self.ui.comboBox_archive.setCurrentIndex (archive_dictionary[archive_format])
		
		self.ui.spinBox_interval.setValue (int (read_configuration_file (3)))
		
		self.ui.slider_priority.setValue (int (read_configuration_file (4)))
		
		self.ui.comboBox_dropbox.setCurrentIndex (int (read_configuration_file (5)))
		
		self.ui.lineEdit_token.setText (read_configuration_file (6))
		
	def set_up_settings (self):
		self.ui.comboBox_enable.addItem ('True')
		self.ui.comboBox_enable.addItem ('False')
		
		self.ui.comboBox_archive.addItem ('zip')
		self.ui.comboBox_archive.addItem ('tar')
		self.ui.comboBox_archive.addItem ('bztar')
		self.ui.comboBox_archive.addItem ('gztar')
		
		self.ui.comboBox_dropbox.addItem ('True')
		self.ui.comboBox_dropbox.addItem ('False')
	
	def add_path (self, widget):
		
		new_path = QtGui.QFileDialog.getExistingDirectory (None, 'Select a directory', self.user_dir, QtGui.QFileDialog.ShowDirsOnly)
		
		if str (type (widget)) == "<class 'PyQt4.QtGui.QComboBox'>":
			if new_path:
				for item in range (0, widget.count()):
					if new_path == widget.itemText (item):
						return 1
				widget.addItem (new_path)
				widget.setCurrentIndex (widget.count() - 1)
		
		if str (type (widget)) == "<class 'PyQt4.QtGui.QListWidget'>":
			if new_path:
				for row in range (0, widget.count()):
					if new_path == widget.item (row):
						return 1
				widget.addItem (new_path)

	def remove_path (self, widget):
		widget.takeItem (widget.currentRow())
	
	def apply_settings (self):
		in_dir_file = open (self.user_dir + '/.smc/in_dir.inf', 'w')
		for row in range (0, self.ui.listWidget_in.count()):
			in_dir_file.write (self.ui.listWidget_in.item(row).text() + '\n')
		in_dir_file.close()
		
		out_dir_file = open (self.user_dir + '/.smc/out_dir.inf', 'w')
		for row in range (0, self.ui.listWidget_out.count()):
			out_dir_file.write (self.ui.listWidget_out.item(row).text() + '\n')
		out_dir_file.close()
		
		root_history_file = open (self.user_dir + '/.smc/root_history.inf', 'w')
		if self.ui.comboBox_root.currentText():
			root_history_file.write (self.ui.comboBox_root.currentText() + '\n')
		for row in range (0, self.ui.comboBox_root.count()):
			if self.ui.comboBox_root.currentText() != self.ui.comboBox_root.itemText (row):
				if self.ui.comboBox_root.itemText (row) != 'None':
					root_history_file.write (self.ui.comboBox_root.itemText (row) + '\n')
		if self.ui.comboBox_root.currentText() != 'None':
			root_history_file.write ('None' + '\n')
		root_history_file.close()
		
		configuration_file = open (self.user_dir + '/.smc/config.inf', 'w')

		configuration_file.write ('enable_smc=' + str (self.ui.comboBox_enable.currentIndex()) + '\n')

		configuration_file.write ('archive_format=' + self.ui.comboBox_archive.currentText() + '\n')

		configuration_file.write ('check_interval=' + self.ui.spinBox_interval.cleanText() + '\n')
		current_directory = os.getcwd()
		set_up_cron (int (self.ui.spinBox_interval.cleanText()), current_directory + '/smc_loader.py')
		
		configuration_file.write ('smc_priority=' + str (self.ui.slider_priority.value()) + '\n')
		
		configuration_file.write ('dropbox_enable=' + str (self.ui.comboBox_dropbox.currentIndex()) + '\n')
		
		configuration_file.write ('access_token=' + self.ui.lineEdit_token.text() + '\n')
		
		configuration_file.close()
		
	def read_file (self, file_name, widget):
		file_to_be_read = open (file_name)
		
		for line in file_to_be_read:
			widget.addItem (line.rstrip())
		
		file_to_be_read.close()

if __name__ == '__main__':
	application = QtGui.QApplication (sys.argv)
	
	window = main_window()
	window.show()
	
	sys.exit (application.exec_())
