__author__ = 'Michael Gilbertson'

from Tkinter import *

class passwordWindow:

    def __init__(self, clientInterface):

        self.lock = False

        self.UI = clientInterface
        self.UI.changePasswordButton.config(state=DISABLED)

        self.pwin = Toplevel(self.UI.root, padx=10, pady=10)
        self.pwin.protocol('WM_DELETE_WINDOW', self.closePasswordWindow)
        self.pwin.title("Change your OneDir Password")

        self.statusText = StringVar()
        self.statusText.set("Enter your old password followed by your new password.")

        self.passwordStatus = Label(self.pwin, padx=5, pady=5, wraplength=300, textvariable=self.statusText)
        self.passwordStatus.grid(row=0, column=0, columnspan=3)

        self.oldPassword = Label(self.pwin, text="Old Password:", padx=5, pady=5)
        self.oldPassword.grid(row=2, columnspan=1,)
        self.oldPasswordEntry = Entry(self.pwin, show="*", width=30)
        self.oldPasswordEntry.grid(row=2, column=1, columnspan=2)

        self.newPassword1 = Label(self.pwin, text="New Password:", padx=5, pady=5)
        self.newPassword1.grid(row=3, columnspan=1,)
        self.newPassword1Entry = Entry(self.pwin, show="*", width=30)
        self.newPassword1Entry.grid(row=3, column=1, columnspan=2)

        self.newPassword2 = Label(self.pwin, text="Retype Password:", padx=5, pady=5)
        self.newPassword2.grid(row=4, columnspan=1,)
        self.newPassword2Entry = Entry(self.pwin, show="*", width=30)
        self.newPassword2Entry.grid(row=4, column=1, columnspan=2)

        self.cancelButton = Button(self.pwin, text="Cancel", command=self.closePasswordWindow)
        self.cancelButton.grid(row=5, column=0)

        self.passwordButton = Button(self.pwin, text="Change", command=lambda:
            self.changePassword(self.oldPasswordEntry.get(),self.newPassword1Entry.get(), self.newPassword2Entry.get()))
        self.passwordButton.grid(row=5, column=2)
        self.UI.center(self.pwin)

    def validateEdit(self):
        return not self.lock

    def changePassword(self, op, np1, np2):

        if not self.UI.prefOps.authenticateUser(self.UI.userRow[0], op):
            self.statusText.set("This password doesn't match your username. Please enter your current password.")
            self.passwordStatus.config(fg="red")
            return

        elif len(np1) < 5:
            self.statusText.set("Your new password must be at least 5 characters long. Please choose a longer password.")
            self.passwordStatus.config(fg="red")
            return

        elif np1 != np2:
            self.statusText.set("Your new password fields do not match one another. Please make sure they match.")
            self.passwordStatus.config(fg="red")
            return

        elif (len(np1)+len(np2) >= 10) & (np1 == np2):
            self.user = self.UI.userRow[0]
            self.np = np1
            self.lock = True
            #kevin

    def changePasswordResponse(self, response):
        #kevin
        if response:
            self.UI.prefOps.updatePassword(self.user, self.np)
            self.UI.passwordLength = len(self.np)
            self.UI.passwordVar.set(self.UI.blankPassword(self.UI.passwordLength))
            self.closePasswordWindow()
            return
        else:
            self.statusText.set("There was a problem changing your password on the server.")
            self.passwordStatus.config(fg="red")
        self.lock = False

    def closePasswordWindow(self):
        self.UI.changePasswordButton.config(state=NORMAL)
        self.pwin.destroy()
        return
