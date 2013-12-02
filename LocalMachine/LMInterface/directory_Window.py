__author__ = 'Michael Gilbertson'

from Tkinter import *

class directoryWindow:

    def __init__(self, clientInterface):

        self.UI = clientInterface
        self.UI.changeDirectoryButton.config(state=DISABLED)

        self.dwin = Toplevel(self.UI.root, padx=10, pady=10)
        self.dwin.protocol('WM_DELETE_WINDOW', self.closeDirectoryWindow)
        self.dwin.title = "Change OneDir Directory"

        self.statusText = StringVar()
        self.statusText.set("Enter the new directory path of your OneDir Directory: ")

        self.directoryStatus = Label(self.dwin, padx=5, pady=5,
                                     wraplength=300, textvariable=self.statusText)
        self.directoryStatus.grid(row=0, column=0, columnspan=3)

        self.currentDirectory = Label(self.dwin, text="Current OneDir Directory:", padx=5, pady=5)
        self.currentDirectory.grid(row=1, columnspan=1)

        self.currentDirectoryEntry = Entry(self.dwin, textvariable=self.UI.directoryVar, width=30, state=DISABLED)
        self.currentDirectoryEntry.grid(row=1, column=1, columnspan=2)

        self.newDirectory = Label(self.dwin, text="New OneDir Directory:", padx=5, pady=5)
        self.newDirectory.grid(row=2, columnspan=1)

        self.newDirectoryEntry = Entry(self.dwin,  width=30)
        self.newDirectoryEntry.grid(row=2, column=1, columnspan=2)

        self.cancelButton = Button(self.dwin, text="Cancel", command=self.closeDirectoryWindow)
        self.cancelButton.grid(row=3, column=0)

        self.directoryButton = Button(self.dwin, text="Change", command=lambda:
                self.changeDirectory(self.newDirectoryEntry.get()))
        self.directoryButton.grid(row=3, column=2)
        self.UI.center(self.dwin)

    def changeDirectory(self, directory):
        if not self.UI.prefOps.updateDirectory(self.UI.userRow[0], directory):
            self.statusText.set("This directory path doesn't exist on this machine. Please enter another one.")
            self.directoryStatus.config(fg="red")
            return

        self.UI.directoryVar.set(directory)
        self.closeDirectoryWindow()
        return

    def closeDirectoryWindow(self):
        self.UI.changeDirectoryButton.config(state=NORMAL)
        self.dwin.destroy()
        return