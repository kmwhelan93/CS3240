__author__ = 'Michael Gilbertson'

from Tkinter import *

class loginWindow:

    def __init__(self, clientInterface):

        self.UI = clientInterface

        self.lwin = Toplevel(self.UI.root,  padx=10, pady=10)
        self.lwin.protocol('WM_DELETE_WINDOW', self.closeWindow)
        self.lwin.title("Login to OneDir Preferences")

        self.loginText = StringVar()
        self.loginText.set("Enter you username and password below to login.")

        self.loginStatus = Label(self.lwin, padx=5, pady=5, wraplength=300, textvariable=self.loginText)
        self.loginStatus.grid(row=0, column=0, columnspan=3)

        self.usernameLabel = Label(self.lwin, text="Username:", padx=5, pady=5)
        self.usernameLabel.grid(row=1, columnspan=1)

        self.passwordLabel = Label(self.lwin, text="Password:", padx=5, pady=5)
        self.passwordLabel.grid(row=2, columnspan=1)

        self.usernameEntry = Entry(self.lwin, width=40)
        self.usernameEntry.grid(row=1, column=1, columnspan=2)
        self.passwordEntry = Entry(self.lwin, width=40, show="*")
        self.passwordEntry.grid(row=2, column=1, columnspan=2)

        self.loginButton = Button(self.lwin, text="Login", width=40,
                          command=lambda:self.login(self.usernameEntry.get(),self.passwordEntry.get()))
        self.loginButton.grid(row=3, column=0, columnspan=3)

        self.setUpText = StringVar()
        self.setUpText.set("To set up account, please enter desired OneDir path,"
                                      " along with your desired username and password. ")

        self.setUpStatus = Label(self.lwin, padx=5, pady=5,
                                     wraplength=300, textvariable=self.setUpText)
        self.setUpStatus.grid(row=4, column=0, columnspan=3)

        self.directoryLabel = Label(self.lwin, text="Directory:", padx=5, pady=5)
        self.directoryLabel.grid(row=5, column=0, columnspan=1)

        self.directoryEntry = Entry(self.lwin, width=40)
        self.directoryEntry.grid(row=5, column=1, columnspan=2)

        self.setUpButton = Button(self.lwin, text="Sign Up", width=40,
                command=lambda:self.signup(self.usernameEntry.get(), self.passwordEntry.get(), self.directoryEntry.get()))
        self.setUpButton.grid(row=6, column=0, columnspan=3)

        self.ipLabel = Label(self.lwin)
        self.ipLabel.grid(row = 7, column=0)

        self.ipEntry = Entry(self.lwin, width=15)
        self.ipEntry.grid(row=7, column=1, columnspan=2)

        self.UI.center(self.lwin)


    def login(self, username, password):

        if ( self.UI.prefOps.userExistsGlobally(username) == False ):
            self.loginText.set("No record of this username on our servers. Choose your OneDir username, password, and directory.")
            self.loginStatus.config(fg="blue")
            self.setUpText.set("Click 'Set Up' to create your OneDir account and set up your OneDir directory on this machine. ")
            self.setUpStatus.config(fg="blue")
            return

        elif ( self.UI.prefOps.userExistsLocally(username) == False):
            self.loginText.set("No record of this username on this machine. Choose your OneDir directory for this machine.")
            self.loginStatus.config(fg="blue")
            self.setUpText.set("Click 'Set Up' to set up your OneDir directory on this machine.")
            self.setUpStatus.config(fg="blue")
            return

        elif ( (self.UI.prefOps.userExistsLocally(username) == True) & (self.UI.prefOps.authenticateUser(username, password) == False)):
            self.loginText.set("The username and password you have entered do not match. Please try again. ")
            self.loginStatus.config(fg="red")
            self.setUpText.set("Click 'Log In' to login to you OneDir Preferences. No need to specify a new directory. ")
            self.setUpStatus.config(fg="red")
            return

        elif self.UI.prefOps.authenticateUser(username, password):
            self.UI.passwordLength = len(password)
            self.UI.initUI(username)
            self.closeWindow()
            return


    def signup(self, username, password, directory):

        if ( (self.UI.prefOps.userExistsGlobally(username) == False) &
                 ( self.UI.prefOps.validDirectoryPath(directory) == True) & (len(password) > 0)):
            self.UI.prefOps.createUser(username, password, directory)
            self.UI.setUpText.set("You have successfully set up you OneDir directory on this machine.")
            self.setUpStatus.config(fg="green")
            self.UI.passwordLength = len(password)
            self.UI.initUI(username)
            self.closeWindow()
            return

        if self.UI.prefOps.userExistsLocally(username):
            self.loginText.set("That username has already been taken. Try another.")
            self.loginStatus.config(fg="red")
            self.setUpText.set("Enter a valid directory path to go along with desired username and password. ")
            self.setUpStatus.config(fg="red")
            return

    def closeWindow(self):
        self.lwin.destroy()
        return