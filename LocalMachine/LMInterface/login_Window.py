__author__ = 'Michael Gilbertson'

from Tkinter import *
import os

class loginWindow:

    def __init__(self, clientInterface):

        self.lock = False

        self.UI = clientInterface

        self.lwin = Toplevel(self.UI.root,  padx=10, pady=10)
        self.lwin.protocol('WM_DELETE_WINDOW', self.UI.root.destroy)
        self.lwin.title("Login to OneDir Preferences")

        self.loginText = StringVar()
        self.loginText.set("Enter you username and password below to login.")

        self.loginStatus = Label(self.lwin, padx=5, pady=5, wraplength=300, textvariable=self.loginText)
        self.loginStatus.grid(row=0, column=0, columnspan=3)

        self.usernameLabel = Label(self.lwin, text="Username:", padx=5, pady=5)
        self.usernameLabel.grid(row=1, columnspan=1)

        self.passwordLabel = Label(self.lwin, text="Password:", padx=5, pady=5)
        self.passwordLabel.grid(row=2, columnspan=1)

        self.usernameEntry = Entry(self.lwin, width=40, bg="white", validate=ALL, validatecommand=self.validateEdit)
        self.usernameEntry.grid(row=1, column=1, columnspan=2)
        self.passwordEntry = Entry(self.lwin, width=40, show="*", bg="white", validate=ALL, validatecommand=self.validateEdit)
        self.passwordEntry.grid(row=2, column=1, columnspan=2)

        self.loginButton = Button(self.lwin, text="Login", width=40,
                          command=lambda:self.login(self.usernameEntry.get(),self.passwordEntry.get(),self.directoryEntry.get()))
        self.loginButton.grid(row=3, column=0, columnspan=3)

        self.setUpText = StringVar()
        self.setUpText.set("To set up account, please enter desired OneDir path,"
                                      " along with your desired username and password. ")

        self.setUpStatus = Label(self.lwin, padx=5, pady=5,
                                     wraplength=300, textvariable=self.setUpText)
        self.setUpStatus.grid(row=4, column=0, columnspan=3)

        self.directoryLabel = Label(self.lwin, text="Directory:", padx=5, pady=5)
        self.directoryLabel.grid(row=5, column=0, columnspan=1)

        self.v = StringVar()
        self.v.set(os.path.join(os.getenv("HOME"),"onedir"))
        self.directoryEntry = Entry(self.lwin, width=40, bg="white", validate=ALL, textvariable=self.v, validatecommand=self.validateEdit)
        self.directoryEntry.grid(row=5, column=1, columnspan=2)

        self.setUpButton = Button(self.lwin, text="Sign Up", width=40,
                command=lambda:self.signup(self.usernameEntry.get(), self.passwordEntry.get(), self.directoryEntry.get()))
        self.setUpButton.grid(row=6, column=0, columnspan=3)

        self.UI.center(self.lwin)

    def validateEdit(self):
        return not self.lock

    def login(self, username, password, directory):
        self.username = username
        self.password = password
        self.directory = directory
        if not self.UI.prefOps.userExistsLocally(username) and not self.directory:
            self.loginText.set("No record of this username on this machine. Choose your OneDir directory for this machine.")
            self.loginStatus.config(fg="blue")
            self.setUpText.set("Click 'Login' again after specifying directory to set up your OneDir directory on this machine.")
            self.setUpStatus.config(fg="blue")
        else:
            self.lock = True
            #kevin
            object = {'command': 'authenticate', 'username': username, 'password': password}
            self.UI.commq.append(object)
            #Create and Login object here

    def loginResponse(self, response):
        #kevin
        print response
        if response['success'] == True:
            if not self.UI.prefOps.userExistsLocally(self.username):
                self.UI.prefOps.createUser(self.username, self.password, self.directory)
            self.UI.prefOps.updatePassword(self.username, self.password)
            self.UI.passwordLength = len(self.password)
            self.UI.initUI(self.username, self.password)
            self.closeWindow()
        elif response['reason'] == 'user does not exist':
            self.loginText.set("No record of this username on our servers. Choose your OneDir username, password, and directory.")
            self.loginStatus.config(fg="blue")
            self.setUpText.set("Click 'Set Up' to create your OneDir account and set up your OneDir directory on this machine. ")
            self.setUpStatus.config(fg="blue")
        elif response['reason'] == 'incorrect password':
            self.loginText.set("The username and password you have entered do not match. Please try again. ")
            self.loginStatus.config(fg="red")
            self.setUpText.set("Click 'Log In' to login to you OneDir Preferences. No need to specify a new directory. ")
            self.setUpStatus.config(fg="red")

        self.lock = False

    def signup(self, username, password, directory):
        self.username = username
        self.password = password
        self.directory = directory

        if not len(password) > 4:
            self.loginText.set("Choose a longer password")
            self.loginStatus.config(fg="red")

        if not self.UI.prefOps.validDirectoryPath(directory):
            self.setUpText.set("Enter a valid directory path to go along with desired username and password.")
            self.setUpStatus.config(fg="red")

        if len(password) > 4 and self.UI.prefOps.validDirectoryPath(directory):
            self.lock = True
            #kevin
            #CREATE AND SEND OBJECT
            object = {'command': 'register', 'username': username, 'password': password}
            self.UI.commq.append(object)

    def signupResponse(self, response):
        #kevin
        if response['success'] == True:
            self.UI.prefOps.createUser(self.username, self.password, self.directory)
            self.setUpText.set("You have successfully set up you OneDir directory on this machine.")
            self.setUpStatus.config(fg="green")
            self.UI.passwordLength = len(self.password)
            self.UI.initUI(self.username, self.password)
            self.closeWindow()
        else:
            self.loginText.set("That username has already been taken. Try another.")
            self.loginStatus.config(fg="red")

        self.lock = False

    def closeWindow(self):
        self.lwin.destroy()
        return