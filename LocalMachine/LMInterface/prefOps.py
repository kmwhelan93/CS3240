

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3
import os
import sys
import getpass
import hashlib

class localPrefs:

    def __init__(self):
        self.con = None
        self.con = sqlite3.connect('prefs.db', isolation_level=None)
        self.cur = self.con.cursor()
        self.hash256 = hashlib.sha256()
        self.setup()


    def setup(self):

        self.cur.execute("CREATE TABLE IF NOT EXISTS Prefs ( Username TEXT ,\
                  Password TEXT, AutoSync INTEGER, Directory TEXT)")

        self.cur.execute ("SELECT * FROM Prefs")
        result = self.cur.fetchall()
        if ( len(result)==0 ):
           self.createUser("User1","password1","/home/student/PycharmProjects")

        self.con.commit()

    def userExistsLocally(self, username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": username} )
        result = self.cur.fetchall()
        if(len(result) ==1):
            return True
        else:
            return False

    def userExistsGlobally(self, username):
        #code to be added.
        return False

    def getUserRow(self, username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": username} )
        row = self.cur.fetchone()
        return row

    def updatePassword(self, username, password):
        if self.userExistsLocally(username):
            digest = hashlib.sha256(password).hexdigest()
            self.cur.execute("UPDATE Prefs SET password=? WHERE username=?", [digest,username])
            self.con.commit()
            return True
        else:
            return False

    def createUser(self, username, password, directory):
        if not self.userExistsLocally(username):
            digest = hashlib.sha256(password).hexdigest()
            self.cur.execute("INSERT INTO Prefs VALUES(?,?,?,?)",
                [ username, digest,  1 , directory])
            self.con.commit()
            return True
        else:
            return False

    def authUser(self, username, password):
        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": username} )
        userData = self.cur.fetchone()
        digest = hashlib.sha256(password).hexdigest()
        #self.hash256.update(password)
        if userData[1] == digest:
            print "The username and password match."
            return True
        print userData[0]
        print userData[1]
        print self.hash256.hexdigest()
        print "The username and password don't match."
        return False

    def getUsername(self):
        self.cur.execute ("SELECT * FROM Prefs")
        row = self.cur.fetchone()
        Username = row[0]
        return Username



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

        print "\nUsername: " + curUser[0]
        print "Password: " + curUser[1]
        print "AutoSync(0=>off; 1=>on): " + str(curUser[2])
        print "OneDir Directory: " + curUser[3]
        print ""
        return



    def changepassword(self, Username):

        self.cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": Username} )
        curUser = self.cur.fetchone()

        oldpwd = getpass.getpass( prompt='\nEnter your old password:')
        attempts = 5

        while ( oldpwd != curUser[1]):

            print "This password doesn't match your account. Please try again."
            attempts = attempts -1
            if ( attempts == 0):
                print "You have used all of you attempts. Please try again later. "
                return
            print "You have " + str(attempts) + " attempts left."
            oldpwd = getpass.getpass( prompt = 'Enter you old password:')

        if (oldpwd == curUser[1]) :

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

        if ( curUser[2] == 0 ):
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

    def validDirPath(self, directory):
        if (os.path.isdir(directory) == False):
                return False
        return True

    def changedirectory(self,Username, directory):

        if (self.validDirPath(directory)==False):
                return False
        Directory = directory
        self.cur.execute("UPDATE Prefs SET Directory = ? WHERE Username = ?", (Directory, Username))
        self.con.commit()
        return True








