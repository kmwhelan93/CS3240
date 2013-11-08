
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prefOps import localPrefs
import sys


class LMInterface:

    def __init__(self):
        self.ops = localPrefs()
        self.Username = self.ops.getUsername()


    def menu(self):

        print "-------------------------------------------------"
        print "   Press 1 to view your preferences."
        print "   Press 2 to change password."
        print "   Press 3 to change autosync setting."
        print "   Press 4 to change OneDir Directory."
        print "   Press 0 to exit."
        print "-------------------------------------------------"


    def start(self):
        print "\nWelcome " + self.Username + " to your OneDir Preferences."
        while True:
            self.menu()
            x = int(raw_input('What would you like to do? '))
            if not (x >= 0 or x <= 4):
                print "\nInvalid Selection. Please select another option.\n"
                continue
            elif x == 0:
                print "\nYou are now exiting your OneDir Preferences. Goodbye."
                break
            elif x == 1:
                self.ops.viewuserprefs(self.Username)
            elif x == 2:
                self.ops.changepassword(self.Username)
            elif x == 3:
                self.ops.changeautosync(self.Username)
            elif x == 4:
                self.ops.changedirectory(self.Username)


if __name__== '__main__':
    LMI = LMInterface()
    LMI.start()