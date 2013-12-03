__author__ = 'Michael Gilbertson'

from Tkinter import *
from login_Window import loginWindow
from password_Window import passwordWindow
from directory_Window import directoryWindow
from LocalMachine.preferences_Operations import preferenceOperations
from PIL import Image, ImageTk


class clientInterface:
    def __init__(self, q, ciq):
        self.root = Tk()
        self.prefOps = preferenceOperations()
        self.root.withdraw()
        self.loginWindow = loginWindow(self)
        self.root.mainloop()
        self.userRow = None
        self.passwordLength = 0

        self.q = q
        self.ciq = ciq

    def initUI(self, username, password):
        self.prefOps.checkStartDaemon(username, password)
        self.root.title("OneDir Local User Preferences Interface")
        self.root.config(padx=10, pady=10)
        self.userRow = self.prefOps.getUserRow(username)

        self.usernameVar = StringVar()
        self.passwordVar = StringVar()
        self.directoryVar = StringVar()
        self.autosyncVar = IntVar()

        self.usernameLabel = Label(self.root, text="Username:", padx=5, pady=5)
        self.usernameLabel.grid(row=0)
        self.passwordLabel = Label(self.root, text="Password:", padx=5, pady=5)
        self.passwordLabel.grid(row=1)
        self.directoryLabel = Label(self.root, text="OneDir Directory:", padx=5, pady=5)
        self.directoryLabel.grid(row=2)
        self.autosyncLabel = Label(self.root, text="Autosync:", padx=5, pady=5)
        self.autosyncLabel.grid(row=3)

        self.usernameVar.set(self.userRow[0])
        self.passwordVar.set(self.blankPassword(self.passwordLength))
        self.directoryVar.set(self.userRow[3])
        self.autosyncVar.set(self.userRow[2])

        self.usernameEntry = Entry(self.root, textvariable=self.usernameVar, width=40, state=DISABLED)
        self.usernameEntry.grid(row=0, column=1, columnspan=2)

        self.passwordEntry = Entry(self.root, textvariable=self.passwordVar, show="*", width=40, state=DISABLED)
        self.passwordEntry.grid(row=1, column=1, columnspan=2)

        self.directoryEntry = Entry(self.root, textvariable=self.directoryVar, width=40, state=DISABLED)
        self.directoryEntry.grid(row=2, column=1, columnspan=2)

        self.autosyncCheck = Checkbutton(self.root, text="Select to enable Autosync",
                                         variable=self.autosyncVar, padx=5, pady=5,
                                         command=lambda: self.prefOps.updateAutoSyncSetting(self.userRow[0], password))
        self.autosyncCheck.grid(row=3, column=1, columnspan=2)

        self.changePasswordButton = Button(self.root, text="Change Password", command=lambda: passwordWindow(self))
        self.changePasswordButton.grid(row=4, column=0)

        self.changeDirectoryButton = Button(self.root, text="Change Directory", command=lambda: directoryWindow(self))
        self.changeDirectoryButton.grid(row=4, column=1)

        self.exitButton = Button(self.root, text="Exit", width=10)
        self.exitButton.grid(row=4, column=2)

        self.center(self.root)

    def blankPassword(self, length):
        blank = ""
        for i in range(length):
            blank += "*"

        return blank


    def center(self, win):
        win.withdraw()
        win.update_idletasks()  # Update "requested size" from geometry manager

        x = (win.winfo_screenwidth() - win.winfo_reqwidth()) / 2
        y = (win.winfo_screenheight() - win.winfo_reqheight()) / 2
        win.geometry("+%d+%d" % (x, y))

        # This seems to draw the window frame immediately, so only call deiconify()
        # after setting correct window position
        win.deiconify()
