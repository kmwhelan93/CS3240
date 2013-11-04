__author__ = 'Michael Gilbertson'

import LocalMachine.prefOps as prefOps

class LMInterface:

    def __init__(self):
        self.con = prefOps.prefOps()

    def menu(self):

        print "\nWelcome to your OneDir Preferences."
        print "-------------------------------------------------"
        print "   Press 1 to view your preferences."
        print "   Press 2 to change password."
        print "   Press 3 to change autosync setting."
        print "   Press 4 to change OneDir Directory."
        print "   Press 0 to exit."
        print "-------------------------------------------------"


    def start(self):

        while True:
            self.menu()
            x = int(raw_input('What would you like to do? '))
            if not (x >= 0 or x <= 4):
                print "Invalid Option \n\n"
                continue
            elif x == 0:
                print "Interface Exit"
                break
            elif x == 1:
                self.con.viewuserprefs(Username)
            elif x == 2:
                self.con.changepassword(Username)
            elif x == 3:
                self.con.changeautosync(Username)
            elif x == 4:
                self.con.changedirectory(Username)


if __name__== '__main__':
    LMI = LMInterface()
    LMI.start()