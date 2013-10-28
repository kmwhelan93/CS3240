__author__ = 'justin'
import Server.DbOps as DbOps

class SInterface:


    def __init__(self):
        self.db = DbOps.DbOps()

    def menu(self):
        print "Howdy Admin! Please select an option:"
        print "-----------------------------------------"
        print "1. Print OneDir Users by Username"
        print "2. Print OneDir Users by Registration Time"
        print "3. Print Recent Transactions"
        print "4. Delete a User"
        print "5. Change a user's password"
        print "6. Start Server Daemon"
        print "0. Exit"
        print "-----------------------------------------"

    def start(self):
        while True:
            self.menu()
            x = int(raw_input('What would you like to do? '))
            if not (x >= 1 or x <= 6):
                print "Invalid Option \n\n"
                continue
            elif x == 0:
                print "Interface Exit"
                break
            elif x == 1:
                for u in self.db.getUsersByUName():
                    print u
            elif x == 2:
                for u in self.db.getUsersByTime():
                    print u
            elif x == 3:
                print "Not yet implemented"
            elif x == 4:
                str = raw_input("Which user name?")
                if self.db.userExists(str):
                    self.db.deleteUser(str)
                else:
                    print "That user does not exist."
            elif x == 5:
                str = raw_input("Which user name?")
                if self.db.userExists(str):
                    pw = raw_input("Enter the new password: ")
                    self.db.updatePassword(str, pw)
                else:
                    print "That user does not exist."



if __name__== '__main__':
     SI = SInterface()
     SI.start()