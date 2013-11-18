
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prefOps import localPrefs
import sys
from Tkinter import *
from ttk import Frame, Style
from idlelib.WidgetRedirector import WidgetRedirector
import tkMessageBox

from Tkinter import *

class Gui(Frame):

    def __init__(self, parent, govnah):
        self.govnah = govnah
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.withdraw()
        self.loginWindow()
        self.initUI()
        self.lock = False

    def loginWindow(self):

        self.lock = True
        self.top = Toplevel ( self, padx = 10, pady = 10 )

        self.top.protocol('WM_DELETE_WINDOW', self.closeWindow)
        self.top.title("Login to OneDir Preferences")

        self.top.loginstatus_var = StringVar()
        self.top.loginstatus_var.set("Enter you username and password below to login.")

        self.top.login_entry= Label(self.top, padx=5, pady = 5,
                                    wraplength = 300, textvariable=self.top.loginstatus_var)
        self.top.login_entry.grid(row=0,column=0,columnspan=3)

        usernameL = Label(self.top, text="Username:", padx=5, pady = 5)
        usernameL.grid(row=1, columnspan=1)
        passwordL = Label(self.top, text="Password:", padx=5, pady = 5)
        passwordL.grid(row=2, columnspan=1)

        self.usernameE= Entry(self.top , width = 40)
        self.usernameE.grid(row=1,column=1,columnspan=2)
        self.passwordE = Entry(self.top, width = 40, show="*")
        self.passwordE.grid(row=2,column=1,columnspan=2)

        LoginBtn = Button(self.top, text="Login", width = 40,
                          command=lambda:self.login(self.usernameE.get(),self.passwordE.get()))
        LoginBtn.grid(row=3 ,column = 0, columnspan = 3)


        self.top.signupstatus_var = StringVar()
        self.top.signupstatus_var.set("To set up account, please enter desired OneDir path,"
                                      " along with your desired username and password. ")

        self.top.signup_entry= Label(self.top, padx=5, pady = 5,
                                     wraplength = 300, textvariable=self.top.signupstatus_var)
        self.top.signup_entry.grid(row=4,column=0,columnspan=3)

        directoryL = Label(self.top, text="Directory:", padx=5, pady = 5)
        directoryL.grid(row=5, column = 0, columnspan=1)

        self.directoryE= Entry(self.top , width = 40)
        self.directoryE.grid(row=5,column=1,columnspan=2)

        SignUpBtn = Button(self.top, text="Sign Up" , width = 40,
                command=lambda:self.signup(self.usernameE.get(),self.passwordE.get(),self.directoryEget()))
        SignUpBtn.grid(row=6, column = 0, columnspan =3)


        self.center(self.top)


    def initUI(self):
        self.parent.title("OneDir Local User Preferences Interface")

        username_var = StringVar()
        password_var = StringVar()
        directory_var = StringVar()
        autosync_var = IntVar()

        self.usernameLabel = Label(self.parent, text="Username:").grid(row=0)
        self.passwordLabel = Label(self.parent, text="Password:").grid(row=1)
        self.directoryLabel = Label(self.parent, text = "OneDir Directory:").grid(row=2)
        self.autosyncLabel = Label(self.parent, text = "Autosync:").grid(row=3)

        username_var.set(self.govnah.ops.getuserprefs()[0])
        password_var.set(self.govnah.ops.getuserprefs()[1])
        directory_var.set(self.govnah.ops.getuserprefs()[2])
        autosync_var.set(self.govnah.ops.getuserprefs()[3])

        username_entry= Label(self.parent,textvariable=username_var).grid(row=0,column=1,columnspan=2)
        password_entry= Label(self.parent, textvariable=password_var).grid(row=1,column=1,columnspan=2)
        directory_entry= Label(self.parent, textvariable=directory_var).grid(row=2,column=1,columnspan=2)

        autosyncCheck = Checkbutton(self.parent, text="Select to enable Autosync", variable=autosync_var)
        autosyncCheck.grid(row=3,column=1,columnspan=2)

        chgPasswordBtn = Button(self.parent, text="Change Password", command = self.getNewPw)
        chgPasswordBtn.grid(row=4, column=0)

        chgDirectoryBtn = Button(self.parent, text="Change Directory")
        chgDirectoryBtn.grid(row=4, column=1)

        signOutBtn = Button(self.parent, text="Sign Out")
        signOutBtn.grid(row=4, column=2)

    def login(self, username, password):
        if ( self.govnah.ops.userExists(username) == False):
            self.top.loginstatus_var.set("No record of this username on this machine. You must set up your directory first.")
            self.top.login_entry.config(fg="blue")
            self.top.signupstatus_var.set("Enter a valid directory path to go along with desired username and  password. ")
            self.top.signup_entry.config(fg="blue")
            return

        if self.govnah.ops.authUser(username,password):
            self.top.loginstatus_var.set("Username and password  match.")
            self.top.login_entry.config(fg="green")
            self.closeWindow()
            self.parent.deiconify()
            return

        self.top.loginstatus_var.set("Username and password don't match.")
        self.top.login_entry.config(fg="red")
        return

    def signup(self, username, password, directory):
        if ( self.govnah.ops.userExists(username) == True):
            self.top.loginstatus_var.set("That username has already been taken. Try another.")
            self.top.login_entry.config(fg="red")
            self.top.signupstatus_var.set("Enter a valid directory path to go along with desired username and password. ")
            self.top.signup_entry.config(fg="red")
            return

        return



    def getNewPw(self):
        if self.govnah.ops.authenticateUser:
            self.unameforpwch = self.govnah.Username
            self.lock = True
            self.top = Toplevel()
            self.top.protocol('WM_DELETE_WINDOW', self.closeWindow)
            self.top.title = "Change Password"
            l = Label(self.top, text="Enter a new Password for user: " + self.unameforpwch)
            l.grid(row=0, columnspan=2)
            self.entry = Entry(self.top, width=20, bg="white")
            self.entry.grid(row=1, columnspan=2)
            n = Button(self.top, text="Cancel", command=self.closeWindow)
            n.grid(row=2, column=0)
            y = Button(self.top, text="Proceed", command=self.confirmPwChange)
            y.grid(row=2, column=1)
            self.center(self.top)

    def closeWindow(self):
        self.lock = False
        self.top.destroy()


    def confirmPwChange(self):
        pw = self.entry.get()
        if len(pw) > 0:
            self.govnah.chUserPass(self.unameforpwch, pw)
            self.top.destroy()
            self.appendText("Password for " + self.unameforpwch + " successfully changed to " + pw)
            self.appendText("")
            self.lock = False

    def center(self, win):
        win.withdraw()
        win.update_idletasks()  # Update "requested size" from geometry manager

        x = (win.winfo_screenwidth() - self.parent.winfo_reqwidth()) / 2
        y = (win.winfo_screenheight() - self.parent.winfo_reqheight()) / 2
        win.geometry("+%d+%d" % (x, y))

        # This seems to draw the window frame immediately, so only call deiconify()
        # after setting correct window position
        win.deiconify()




    def say_hi(self):

        print "hi there, everyone!"


class LMInterface:

    def __init__(self):
        self.ops = localPrefs()
        self.Username = self.ops.getUsername()
        root = Tk()
        root.geometry("600x300+100+100")
        self.gui = Gui(root, self )
        root.mainloop()




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