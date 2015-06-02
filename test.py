#!/usr/bin/env python3
#root directory monitoring tool prototype
#Copyright 2015, Aswin Babu K

#import some serious stuff
import notify2
from gi.repository import Gtk

#what to do when add button is clicked
def add_button_click (notification, action):
    notification.close()
    return 1

#what to do when ignore button is clicked
def ignore_button_click (notification, action):
    return 0

#close the notification
def close_notification (notification):
    Gtk.main_quit()

#draw a simple notification
def draw_notification():
    notify2.init ('SaveMyCode!', mainloop='glib')
    server_capability = notify2.get_server_caps()
    notification = notify2.Notification ('Starting work on a new project?')
    
    if 'actions' in server_capability:
        notification.add_action ('add', 'Add', add_button_click)
        notification.add_action ('ignore', 'Ignore', ignore_button_click)
    notification.connect ('closed', close_notification)
    
    notification.show()
    Gtk.main()

#stricly for debugging purposes
draw_notification()