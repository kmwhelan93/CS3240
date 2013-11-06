__author__ = 'justin'

from Tkinter import *
from ttk import Frame, Style
from Server import DbOps
from idlelib.WidgetRedirector import WidgetRedirector


class ReadOnlyText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

class View(Frame):
    def __init__(self, parent, govnah):
        self.govnah = govnah
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("OneDir Server Admin Interface")
        #self.pack(fill=BOTH, expand=1)
        commands = Label(self.parent, text="Commands")
        commands.grid(row=0, columnspan=3)
        output = Label(self.parent, text="Output")
        output.grid(row=0, column=3)

        scrollbar = Scrollbar(self.parent, )
        scrollbar.grid(row=1, column=4, rowspan=100, sticky=N+S)

        self.log = ReadOnlyText(self.parent, bg="white", undo=False, yscrollcommand=scrollbar.set, width=120)
        self.log.grid(row=1, column=3, rowspan=100)

        scrollbar.config(command=self.log.yview)

        userStuff = Label(self.parent, text="List Users: ")
        userStuff.grid(row=1, column=0)

        printUserName = Button(self.parent, text="By Name", command=self.govnah.printUsersByName)
        printUserName.grid(row=1, column=1)

        printUserTime = Button(self.parent, text="By Time", command=self.govnah.printUsersByName)
        printUserTime.grid(row=1, column=2)

        trans = Label(self.parent, text="List Transactions: ")
        trans.grid(row=2, column=0)

        printTransType = Button(self.parent, text="By Name")
        printTransType.grid(row=2, column=1)

        printTransTime = Button(self.parent, text="By Time")
        printTransTime.grid(row=2, column=2)

        self.log.insert(END, "Howdy Admin, Welcome to the Server Interface \n\n")

    def appendText(self, text):
        self.log.insert(END, str(text) + "\n")
        self.log.see(END)


class SInterface():

    def __init__(self):
        self.db = DbOps.DbOps()
        root = Tk()
        root.geometry("1150x400+100+100")
        self.view = View(root, self)
        root.mainloop()

    def menu(self):
        print "Howdy Admin! Please select an option:"
        print "-----------------------------------------"
        print "1. Print OneDir Users by Username"
        print "2. Print OneDir Users by Registration Time"
        print "3. Print Recent Transactions"
        print "4. Delete a User"
        print "5. Change a user's password"
        print "6. Start Server Daemon"
        print "0. Exit"
        print "-----------------------------------------\n"

    def printUsersByName(self):
        self.view.appendText("The list of users, sorted by username. (Unique ID, username, password hash, registration timestamp)")
        self.printSanitizeDBstr(self.db.getUsersByUName())

    def printUsersByTime(self):
        self.view.appendText("The list of users, sorted by registration time. (Unique ID, username, password hash, registration timestamp)")
        self.printSanitizeDBstr(self.db.getUsersByTime())

    def printSanitizeDBstr(self, results):
        for entry in results:
            t = ""
            for item in entry:
                t = t + str(item) + "\t"
            self.view.appendText(t)
        self.view.appendText("")



    def start(self):
        while True:
            self.menu()
            x = int(raw_input('What would you like to do? '))
            if not (x >= 1 or x <= 6):
                print "Invalid Option \n\n"
                continue
            elif x == 0:
                print "Interface Exit"
                break
            elif x == 1:
                for u in self.db.getUsersByUName():
                    print u
            elif x == 2:
                for u in self.db.getUsersByTime():
                    print u
            elif x == 3:
                print "Not yet implemented"
            elif x == 4:
                str = raw_input("Which user name?")
                if self.db.userExists(str):
                    self.db.deleteUser(str)
                else:
                    print "That user does not exist."
            elif x == 5:
                str = raw_input("Which user name?")
                if self.db.userExists(str):
                    pw = raw_input("Enter the new password: ")
                    self.db.updatePassword(str, pw)
                else:
                    print "That user does not exist.\n\n"
