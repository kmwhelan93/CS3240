__author__ = 'Michael Gilbertson'

import sqlite3

import sys

class prefOps:

    def __int__(self):
        self.con = sqlite3.connect('prefs.db')
        self.cur = self.con.cursor()
        return

    def setup(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS Prefs (Id INTEGER PRIMARY KEY, Username TEXT ,\
                  Password TEXT, AutoSync INTEGER, Directory TEXT)")
        self.con.commit()
        return

    def viewallpreferences(self ):
        self.cur.execute("SELECT * FROM Prefs")
        rows = cur.fetchall()
        for r in rows:
            print r
        return

    def viewuserprefs(self , Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = cur.fetchone()

        print "\nUsername: " + curUser[1]
        print "Password: " + curser[2]
        print "AutoSync(0=>off; 1=>on): " + str(curUser[3])
        print "OneDir Directory: " + curUser[4]
        print ""
        return

    def changepassword(self, Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = cur.fetchone()

        oldpwd = getpass.getpass( prompt='Enter your old password:')
        attempts = 5

        while ( oldpwd != curUser[2]):
            print "This password doesn't match your account. Please try again."
            attempts = attempts -1
            if ( attempts == 0):
                print "You have used all of you attempts. Please try again later. "
                return
            print "You have " + str(attempts) + " attempts left."
            oldpwd = getpass.getpass( prompt = 'Enter you old password:')

        if (oldpwd == curUser[2]) :
            npwd1 = getpass.getpass( prompt = 'Type your new password:')
            npwd2 = getpass.getpass( prompt = 'Retype your new password:')
            while ( npwd1 != npwd2 ):
                print "Your passwords do not match. Try again"
                newpwd1 = getpass.getpass( prompt = 'Type your new password:')
                newpwd2 = getpass.getpass( prompt = 'Retype your new password:')
            newpwd = str(npwd1)
            self.cur.execute("UPDATE Prefs SET Password=:Password WHERE Username=:Username",{"Password": newpwd, "Username":Username})
            self.con.commit()
            print "Your password has been changed."
        return

    def changeautosync(self, Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = cur.fetchone()

        if ( curUser[3] == 0 ):
            AutoSync = 1
            cur.execute("UPDATE Prefs SET AutoSync = ? WHERE Username =?", (AutoSync, Username))
            con.commit()
            print "\nAutoSync setting has been turned on.\n"
            return
        AutoSync = 0
        self.cur.execute("UPDATE Prefs SET AutoSync= ? WHERE Username = ?", (AutoSync, Username))
        self.con.commit()
        print ("AutoSync setting has been turned off.\n")
        return

    def changedirectory(self,Username):

        self.cur.execture("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username})
        curUser = cur.fetchone()

        print ("Your current OneDir directory is : " + curUser[4])
        answer = raw_input("Would you like to change this directory? (Y/N): ")
        if ( answer == 'Y' or answer == 'y') :
            newdir = raw_input('Alright. Enter new OneDir directory path:')
            if (os.path.isdir(newdir) == False):
                print "Sorry. This directory path doesn't seem to exist."
                return

            Directory = newdir
            cur.execute("UPDATE Prefs SET Directory = ? WHERE Username = ?", (Directory, Username))
            print "Alright. Your OneDir Directory has been changed."
            self.con.commit()
            return
        print "Ok. Your OneDir Directory has not been changed."
        return

if __name__== '__main__':
    odsd = DbOps()
    odsd.start()

    odsd.finish()


