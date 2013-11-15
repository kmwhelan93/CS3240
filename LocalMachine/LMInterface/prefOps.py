

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3
import os
import sys
import getpass

class localPrefs:

    def __init__(self):
        self.con = None
        self.con = sqlite3.connect('prefs.db', isolation_level=None)
        self.cur = self.con.cursor()
        self.setup()


    def setup(self):

        self.cur.execute("CREATE TABLE IF NOT EXISTS Prefs (Id INTEGER PRIMARY KEY, Username TEXT ,\
                  Password TEXT, AutoSync INTEGER, Directory TEXT)")

        self.cur.execute ("SELECT * FROM Prefs")
        result = self.cur.fetchall()
        if ( len(result)==0 ):
            self.cur.execute("INSERT INTO Prefs VALUES (NULL,'User1', 'password1', 1 ,'/home/student/PycharmProjects')")

        self.con.commit()

    def getUsername(self):
        self.cur.execute ("SELECT * FROM Prefs")
        row = self.cur.fetchone()
        Username = row[1]
        return Username

    def authenticateUser(self):
        return True


    def getuserprefs(self):
        self.cur.execute ("SELECT * FROM Prefs")
        curUser = self.cur.fetchone()
        return curUser



    def viewallpreferences(self ):
        self.cur.execute("SELECT * FROM Prefs")
        rows = self.cur.fetchall()
        for r in rows:
            print r
        return

    def viewuserprefs(self , Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = self.cur.fetchone()

        print "\nUsername: " + curUser[1]
        print "Password: " + curUser[2]
        print "AutoSync(0=>off; 1=>on): " + str(curUser[3])
        print "OneDir Directory: " + curUser[4]
        print ""
        return

    def changepassword(self, Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = self.cur.fetchone()

        oldpwd = getpass.getpass( prompt='\nEnter your old password:')
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

            npwd1 = getpass.getpass( prompt = '\nAlright. Type your new password:')
            npwd2 = getpass.getpass( prompt = 'Retype your new password:')
            while ( npwd1 != npwd2 ):
                print "Your passwords do not match. Try again\n"
                newpwd1 = getpass.getpass( prompt = 'Type your new password:')
                newpwd2 = getpass.getpass( prompt = 'Retype your new password:')
            newpwd = str(npwd1)
            self.cur.execute("UPDATE Prefs SET Password=:Password WHERE Username=:Username",{"Password": newpwd, "Username":Username})
            self.con.commit()
            print "\nYour password has been changed.\n"
        return

    def changeautosync(self, Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = self.cur.fetchone()

        if ( curUser[3] == 0 ):
            AutoSync = 1
            self.cur.execute("UPDATE Prefs SET AutoSync = ? WHERE Username =?", (AutoSync, Username))
            self.con.commit()
            print "\nAutoSync setting has been turned on.\n"
            return
        AutoSync = 0
        self.cur.execute("UPDATE Prefs SET AutoSync= ? WHERE Username = ?", (AutoSync, Username))
        self.con.commit()
        print ("\nAutoSync setting has been turned off.\n")
        return

    def changedirectory(self,Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username})
        curUser = self.cur.fetchone()

        print ("\nYour current OneDir directory is : " + curUser[4])
        answer = raw_input("Would you like to change this directory? (Y/N): ")
        if ( answer == 'Y' or answer == 'y') :
            newdir = raw_input('Alright. Enter new OneDir directory path:')
            if (os.path.isdir(newdir) == False):
                print "Sorry. This directory path doesn't seem to exist.\n"
                return

            Directory = newdir
            self.cur.execute("UPDATE Prefs SET Directory = ? WHERE Username = ?", (Directory, Username))
            print "Alright. Your OneDir Directory has been changed."
            self.con.commit()
            return
        print "Ok. Your OneDir Directory has not been changed.\n"
        return







