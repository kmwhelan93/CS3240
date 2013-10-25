#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import getpass
import os
import sys

def viewallpreferences( ):
    cur.execute("SELECT * FROM Prefs")
    rows = cur.fetchall()
    for r in rows:
        print r
    return

con = None
con = sqlite3.connect('prefs.db', isolation_level=None)
cur = con.cursor()


def viewyourprefs():
    cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": uUsername} )
    userrow = cur.fetchone()
    print "\nUsername: " + userrow[1]
    print "Password: " + userrow[2]
    print "AutoSync(0=>off; 1=>on): " + str(userrow[3])
    print "OneDir Directory: " + userrow[4]
    print ""
    return

def changepassword():
    #cur.execute("SELECT * FROM Prefs WHERE Id =:Id" , {"Id": uId })
    #row = cur.fetchone()
    opwd = getpass.getpass( prompt='Enter your old password:')
    attempts = 5
    while ( opwd != userrow[2]):
        print "This password doesn't match your account. Please try again."
        attempts = attempts -1
        if ( attempts == 0):
            print "You have used all of you attempts. Please try again later. "
            return
        print "You have " + str(attempts) + " attempts left."
        opwd = getpass.getpass( prompt = 'Enter you old password:')

    if (opwd == userrow[2]) :
        npwd1 = getpass.getpass( prompt = 'Type your new password:')
        npwd2 = getpass.getpass( prompt = 'Retype your new password:')
        while ( npwd1 != npwd2 ):
            print "Your passwords do not match. Try again"
            npwd1 = getpass.getpass( prompt = 'Type your new password:')
            npwd2 = getpass.getpass( prompt = 'Retype your new password:')
        uPassword = str(npwd1)
        cur.execute("UPDATE Prefs SET Password=:Password WHERE Username=:Username",{"Password":uPassword, "Username":uUsername})
        con.commit()
        print "Your password has been changed."
        return



def changeautosync():
    #cur.execute("SELECT * FROM Prefs WHERE Id =:Id" , {"Id": uId })
    #row = cur.fetchone()
    if ( userrow[3] == 0 ):
        uAutoSync = 1
        cur.execute("UPDATE Prefs SET AutoSync = ? WHERE Username =?", (uAutoSync, uUsername))
        con.commit()
        print "\nAutoSync setting has been turned on.\n"
        return
    uAutoSync = 0
    cur.execute("UPDATE Prefs SET AutoSync= ? WHERE Username = ?", (uAutoSync, uUsername))
    con.commit()
    print ("AutoSync setting has been turned off.\n")
    return

def changedirectory():
    print ("Your current OneDir directory is : " + userrow[4])
    answer = raw_input("Would you like to change this directory? (Y/N): ")
    if ( answer == 'Y' or answer == 'y') :
        newdir = raw_input('Alright. Enter new OneDir directory path:')
        if (os.path.isdir(newdir) == False):
            print "Sorry. This directory path doesn't seem to exist."
            return

        uDirectory = newdir
        cur.execute("UPDATE Prefs SET Directory = ? WHERE Username = ?", (uDirectory, uUsername))
        print "Alright. Your OneDir Directory has been changed."
        con.commit()
        return
    print "Ok. Your OneDir Directory has not been changed."
    return



options = {
            1 : viewyourprefs,
            2 : changepassword,
            3 : changeautosync,
            4 : changedirectory
            }

with con:

    uUsername = str(raw_input( 'What is your Username?'))
    cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": uUsername} )
    row = cur.fetchone()
    while ( row == None ):
        print "Username doesn't match any in our database. Please try again. \n"
        uUsername = str(raw_input( 'What is your Username?'))
        cur.execute("SELECT * FROM Prefs WHERE Username =:Username", {"Username": uUsername} )
        row = cur.fetchone()
    userrow = row

    print "\nWelcome " + uUsername + " to your OneDir Preferences."
    print "-------------------------------------------------"
    print "   Press 1 to view your preferences."
    print "   Press 2 to change password."
    print "   Press 3 to change autosync setting."
    print "   Press 4 to change OneDir Directory."
    print "   Press 0 to exit."
    print "-------------------------------------------------"

    x = int(raw_input('What would you like to do?'))

    while ( x != 0):
        options[x]()
        print "---------------------------------------------"
        print "   Press 1 to view your preferences."
        print "   Press 2 to change password."
        print "   Press 3 to change autosync setting."
        print "   Press 4 to change OneDir Directory."
        print "   Press 0 to exit."
        print "---------------------------------------------"
        x = int(raw_input('What else would you like to do?'))
    print "Goodbye."
    sys.exit()





