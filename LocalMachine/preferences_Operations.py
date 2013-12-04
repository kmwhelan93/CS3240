#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Michael Gilbertson'

import sqlite3
import os
import sys
import getpass
import hashlib
import subprocess
import signal

class preferenceOperations:

    def __init__(self):

        self.con = None
        self.con = sqlite3.connect('localPreferences.db', isolation_level=None)
        self.cur = self.con.cursor()
        self.setUpTable()

    def setUpTable(self):

        self.cur.execute("CREATE TABLE IF NOT EXISTS Preferences ( Username TEXT ,\
                  Password TEXT, AutoSync INTEGER, Directory TEXT)")
        self.cur.execute("SELECT * FROM Preferences")
        result = self.cur.fetchall()

        if len(result) == 0:
            self.createUser("User1", "password1", "/home/justin/wiki")
            self.con.commit()
        else:
            self.con.commit()



    def createUser(self, username, password, directory):
        if not self.userExistsLocally(username):
            digest = password
            self.cur.execute("INSERT INTO Preferences VALUES(?,?,?,?)",
                [username, digest,  1, directory])
            self.con.commit()
            return True
        else:
            return False

    def authenticateUser(self, username, password):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        userData = self.cur.fetchone()
        digest = password

        if userData[1] == digest:
            print "The username and password match."
            return True
        else:
            print userData[0]
            print userData[1]
            print "The username and password don't match."
            return False

    def userExistsLocally(self, username):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        result = self.cur.fetchall()

        if len(result) == 1:
            return True
        else:
            return False

    def userExistsGlobally(self, username):
        #code to be added.
        return True

    def getUserRow(self, username):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        row = self.cur.fetchone()
        return row

    def getHashedPassword(self, username):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        row = self.cur.fetchone()
        return row[1]

    def getAutoSyncSetting(self, username):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        row = self.cur.fetchone()
        return row[2]

    def getDirectoryPath(self, username):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        row = self.cur.fetchone()
        return row[3]


    def updatePassword(self, username, password):

        if self.userExistsLocally(username):
            digest = password
            self.cur.execute("UPDATE Preferences SET password=? WHERE username=?", [digest,username])
            self.con.commit()
            print "Password has been updated."
            return True
        else:
            print "Password was not updated."
            return False

    def updateDirectory(self, username, directory):

        if not self.validDirectoryPath(directory):
            print "Directory path was not updated."
            return False
        else:
            self.cur.execute("UPDATE Preferences SET Directory = ? WHERE Username = ?", (directory, username))
            self.con.commit()
            print "Directory path has been updated."
            return True

    def updateAutoSyncSetting(self, username, password):

        self.cur.execute("SELECT * FROM Preferences WHERE Username =:Username", {"Username": username})
        curUser = self.cur.fetchone()

        if curUser[2] == 0:
            AutoSync = 1
            self.cur.execute("UPDATE Preferences SET AutoSync = ? WHERE Username =?", (AutoSync, username))
            self.con.commit()
            subprocess.Popen(["python", "../LMDaemon/client_daemon.py", "--path", curUser[3], "--user", username, "--password", password])
            print "AutoSync setting has been turned on."
            return
        else:
            AutoSync = 0
            self.cur.execute("UPDATE Preferences SET AutoSync= ? WHERE Username = ?", (AutoSync, username))
            self.con.commit()
            ps = subprocess.Popen("ps -ef | grep client_daemon.py | grep -v grep", shell=True, stdout=subprocess.PIPE)
            output = ps.stdout.read()
            ps.stdout.close()
            ps.wait()
            if len(output) > 3:
                procstring = output.split()
                pid = procstring[1]
                print int(pid)
                print os.kill(int(pid), signal.SIGKILL)
            print "AutoSync setting has been turned off."
            return

    def validDirectoryPath(self, directory):

        if not os.path.isdir(directory):
            print "Directory path is invalid."
            return False
        else:
            print "Directory path is valid."
            return True

    def checkStartDaemon(self, username, password):
        if self.getAutoSyncSetting(username):
            subprocess.Popen(["python", "../LMDaemon/client_daemon.py", "--path", self.getDirectoryPath(username), "--user", username, "--password", password])
        else:
            ps = subprocess.Popen("ps -ef | grep client_daemon.py | grep -v grep", shell=True, stdout=subprocess.PIPE)
            output = ps.stdout.read()
            ps.stdout.close()
            ps.wait()
            if len(output) > 3:
                procstring = output.split()
                pid = procstring[1]
                print int(pid)
                print os.kill(int(pid), signal.SIGKILL)
            print "AutoSync setting has been turned off."