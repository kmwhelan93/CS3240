
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
        self.parent.config(padx = 10,  pady =10)
        self.parent.withdraw()
        self.loginWindow()
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

        self.usernameE= Entry(self.top , width = 40, bg="white")
        self.usernameE.grid(row=1,column=1,columnspan=2)
        self.passwordE = Entry(self.top, width = 40, show="*", bg="white")
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

        self.directoryE= Entry(self.top , width = 40, bg="white")
        self.directoryE.grid(row=5,column=1,columnspan=2)

        SignUpBtn = Button(self.top, text="Sign Up" , width = 40,
                command=lambda:self.signup(self.usernameE.get(),self.passwordE.get(),self.directoryE.get()))
        SignUpBtn.grid(row=6, column = 0, columnspan =3)


        self.center(self.top)


    def initUI(self):
        self.parent.title("OneDir Local User Preferences Interface")

        self.username_var = StringVar()
        self.password_var = StringVar()
        self.directory_var = StringVar()
        self.autosync_var = IntVar()

        self.usernameLabel = Label(self.parent, text="Username:", padx=5, pady = 5)
        self.usernameLabel.grid(row=0)
        self.passwordLabel = Label(self.parent, text="Password:", padx=5, pady = 5)
        self.passwordLabel.grid(row=1)
        self.directoryLabel = Label(self.parent, text = "OneDir Directory:", padx=5, pady = 5)
        self.directoryLabel.grid(row=2)
        self.autosyncLabel = Label(self.parent, text = "Autosync:", padx=5, pady = 5)
        self.autosyncLabel.grid(row=3)

        self.username_var.set(self.userrow[0])
        self.password_var.set(self.userrow[1])
        self.directory_var.set(self.userrow[3])
        self.autosync_var.set(self.userrow[2])

        username_entry= Entry(self.parent,textvariable=self.username_var, width = 40, state = DISABLED)
        username_entry.grid(row=0,column=1,columnspan=2)
        password_entry= Entry(self.parent, textvariable=self.password_var, show = "*", width = 40, state = DISABLED)
        password_entry.grid(row=1,column=1,columnspan=2)
        directory_entry= Entry(self.parent, textvariable=self.directory_var, width = 40, state = DISABLED)
        directory_entry.grid(row=2,column=1,columnspan=2)

        autosyncCheck = Checkbutton(self.parent, text="Select to enable Autosync",
                                    variable=self.autosync_var, padx=5, pady = 5,
                                    command = lambda:self.govnah.ops.changeautosync(self.userrow[0]))
        autosyncCheck.grid(row=3,column=1,columnspan=2)

        self.chgPasswordBtn = Button(self.parent, text="Change Password", command = self.passwordWindow)
        self.chgPasswordBtn.grid(row=4, column=0)

        self.chgDirectoryBtn = Button(self.parent, text="Change Directory", command = self.directoryWindow)
        self.chgDirectoryBtn.grid(row=4, column=1)

        self.exitBtn = Button(self.parent, text="Exit", width = 10, command = lambda:self.closeWindow())
        self.exitBtn.grid(row=4, column=2)
        self.center(self.parent)



    def login(self, username, password):
        if ( self.govnah.ops.userExistsLocally(username) == False):
            self.top.loginstatus_var.set("No record of this username on this machine. You must set up your directory first.")
            self.top.login_entry.config(fg="blue")
            self.top.signupstatus_var.set("Enter a valid directory path to go along with desired username and  password. ")
            self.top.signup_entry.config(fg="blue")
            return

        if self.govnah.ops.authUser(username,password):
            self.top.loginstatus_var.set("Username and password  match.")
            self.top.login_entry.config(fg="green")
            self.userrow = self.govnah.ops.getUserRow(username)
            self.closeLogWindow()
            self.parent.deiconify()
            self.initUI()
            return

        self.top.loginstatus_var.set("Username and password don't match.")
        self.top.login_entry.config(fg="red")
        return

    def signup(self, username, password, directory):
        if ( self.govnah.ops.userExistsLocally(username) == True):
            self.top.loginstatus_var.set("That username has already been taken. Try another.")
            self.top.login_entry.config(fg="red")
            self.top.signupstatus_var.set("Enter a valid directory path to go along with desired username and password. ")
            self.top.signup_entry.config(fg="red")
            return
        if ( (self.govnah.ops.userExistsGlobally(username)== False) &
                 ( self.govnah.ops.validDirPath(directory) == True) & (len(password) > 0)):
            self.govnah.ops.createUser(username, password, directory)
            self.top.signupstatus_var.set("You have successfully set up you OneDir directory on this machine.")
            self.top.signup_entry.config(fg="green")
            self.userrow = self.govnah.ops.getUserRow(username)
            self.closeLogWindow()
            self.parent.deiconify()
            self.initUI()
            return




    def directoryWindow(self):
        self.chgDirectoryBtn.config( state = DISABLED)
        self.lock = True
        self.dwin = Toplevel()
        self.dwin.config(padx = 10, pady = 10)
        self.dwin.protocol('WM_DELETE_WINDOW',self.closeDirWindow)
        self.dwin.title = "Change OneDir Directory"

        self.dwin.dirstatus_var = StringVar()
        self.dwin.dirstatus_var.set("Enter your desired directory path below: ")

        self.dwin.directory_entry= Label(self.dwin, padx=5, pady = 5,
                                     wraplength = 300, textvariable=self.dwin.dirstatus_var)
        self.dwin.directory_entry.grid(row=0,column=0,columnspan=3)

        curDirectory = Label(self.dwin, text= "Current OneDir Directory:", padx=5, pady = 5)
        curDirectory.grid(row = 1, columnspan=1,)
        curDir_entry= Entry(self.dwin, textvariable=self.directory_var, width = 30, state = DISABLED)
        curDir_entry.grid(row=1,column=1,columnspan=2)

        newDirectory = Label(self.dwin, text= "New OneDir Directory:")
        newDirectory.grid(row = 2, columnspan=1,)
        newDir_entry= Entry(self.dwin,  width = 30)
        newDir_entry.grid(row=2,column=1,columnspan=2)

        cancelBtn = Button(self.dwin, text="Cancel", command=self.closeDirWindow)
        cancelBtn.grid(row=3, column=0)
        dirBtn = Button(self.dwin, text="Change", command=lambda:self.chgDirectory(newDir_entry.get()))
        dirBtn.grid(row=3, column=2)
        self.center(self.dwin)

    def passwordWindow(self):
        self.chgPasswordBtn.config( state = DISABLED)
        self.lock = True
        self.pwin = Toplevel()
        self.pwin.config(padx = 10, pady = 10)
        self.pwin.protocol('WM_DELETE_WINDOW', self.closePwdWindow)
        self.pwin.title = "Change Your Password"

        self.pwin.pwdstatus_var = StringVar()
        self.pwin.pwdstatus_var.set("Enter your old password followed by your new password.")

        self.pwin.password_entry= Label(self.pwin, padx=5, pady = 5,
                                     wraplength = 300, textvariable=self.pwin.pwdstatus_var)
        self.pwin.password_entry.grid(row=0,column=0,columnspan=3)

        oldPwd = Label(self.pwin, text= "Old Password:", padx=5, pady = 5)
        oldPwd.grid(row = 2, columnspan=1,)
        oldPwd_entry= Entry(self.pwin, show = "*" ,width = 30)
        oldPwd_entry.grid(row=2,column=1,columnspan=2)

        newPwd1 = Label(self.pwin, text= "New Password:", padx=5, pady = 5)
        newPwd1.grid(row = 3, columnspan=1,)
        newPwd1_entry= Entry(self.pwin, show = "*" , width = 30)
        newPwd1_entry.grid(row=3,column=1,columnspan=2)

        newPwd2 = Label(self.pwin, text= "Retype Password:", padx=5, pady = 5)
        newPwd2.grid(row = 4, columnspan=1,)
        newPwd2_entry= Entry(self.pwin,show = "*" , width = 30)
        newPwd2_entry.grid(row=4,column=1,columnspan=2)

        cancelBtn = Button(self.pwin, text="Cancel", command=self.closePwdWindow)
        cancelBtn.grid(row=5, column=0)

        pwdBtn = Button(self.pwin, text="Change", command=lambda:self.chgPassword(oldPwd_entry.get(),
                                                                        newPwd1_entry.get(), newPwd2_entry.get()))
        pwdBtn.grid(row=5, column=2)
        self.center(self.pwin)

    def chgDirectory(self, directory):
        if ( self.govnah.ops.changedirectory(self.userrow[0],directory) == False):
            self.top.dirstatus_var.set("This directory does not exist. Please enter another one.")
            self.top.directory_entry.config(fg="red")
            return
        self.directory_var.set(directory)
        self.top.dirstatus_var.set("Your OneDir Directory was changed successfully.")
        self.top.directory_entry.config(fg="green")
        self.closeDirWindow()
        return

    def chgPassword(self, op, np1, np2):
        if (self.govnah.ops.authUser(self.userrow[0], op) == False):
            self.pwin.pwdstatus_var.set("This password doesn't match your username. Try again.")
            self.pwin.password_entry.config(fg="red")
            return

        if ( (len(np1)+len(np2)>= 1) & (np1 != np2)):
            self.pwin.pwdstatus_var.set("Your new password fields do not match one another.")
            self.pwin.password_entry.config(fg="red")
            return

        if ( (len(np1)+len(np2)>= 1) & (np1 == np2)):
            self.govnah.ops.updatePassword(self.userrow[0], np1)
            self.pwin.pwdstatus_var.set("Your password has been changed successfully.")
            self.pwin.password_entry.config(fg="green")
            self.closePwdWindow()
            return

    def closeWindow(self):
        self.lock = False
        self.parent.destroy()
        return

    def closeLogWindow(self):
        self.top.destroy()
        return

    def closePwdWindow(self):
        self.lock = False
        self.chgPasswordBtn.config(state = NORMAL)
        self.pwin.destroy()
        return

    def closeDirWindow(self):
        self.lock = False
        self.chgDirectoryBtn.config(state = NORMAL)
        self.dwin.destroy()
        return


    def center(self, win):
        win.withdraw()
        win.update_idletasks()  # Update "requested size" from geometry manager

        x = (win.winfo_screenwidth() - self.parent.winfo_reqwidth()) / 2
        y = (win.winfo_screenheight() - self.parent.winfo_reqheight()) / 2
        win.geometry("+%d+%d" % (x, y))

        # This seems to draw the window frame immediately, so only call deiconify()
        # after setting correct window position
        win.deiconify()


class LMInterface:

    def __init__(self):
        self.ops = localPrefs()
        self.Username = self.ops.getUsername()
        root = Tk()
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
