__author__ = 'justin'

from Tkinter import *
from ttk import Frame, Style
from Server import DbOps
from idlelib.WidgetRedirector import WidgetRedirector
import tkMessageBox
from PIL import Image, ImageTk
import tkFont
import os
import subprocess
import threading
import Queue


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
        self.lock = False

    def initUI(self):
        self.parent.title("OneDir Server Admin Interface")
        #self.pack(fill=BOTH, expand=1)
        commands = Label(self.parent, text="Commands")
        commands.grid(row=0, columnspan=3)
        output = Label(self.parent, text="Output")
        output.grid(row=0, column=3)

        scrollbar = Scrollbar(self.parent)
        scrollbar.grid(row=1, column=4, rowspan=100, sticky=N+S)

        self.log = ReadOnlyText(self.parent, bg="white", undo=False, yscrollcommand=scrollbar.set, width=120)
        self.log.grid(row=1, column=3, rowspan=100)

        scrollbar.config(command=self.log.yview)

        userStuff = Label(self.parent, text="List Users: ")
        userStuff.grid(row=1, column=0)

        printUserName = Button(self.parent, text="By Name", command=self.govnah.printUsersByName)
        printUserName.grid(row=1, column=1)

        printUserTime = Button(self.parent, text="By Time", command=self.govnah.printUsersByTime)
        printUserTime.grid(row=1, column=2)

        trans = Label(self.parent, text="List Transactions: ")
        trans.grid(row=2, column=0)

        printTransType = Button(self.parent, text="By Type", command=self.govnah.printTransByType)
        printTransType.grid(row=2, column=1)

        printTransTime = Button(self.parent, text="By Time", command=self.govnah.printTransByTime)
        printTransTime.grid(row=2, column=2)

        printTransSize = Button(self.parent, text="By Size", command=self.govnah.printTransBySize)
        printTransSize.grid(row=3, column=1)

        printTransUser = Button(self.parent, text="By User", command=self.govnah.printTransByUser)
        printTransUser.grid(row=3, column=2)

        trans = Label(self.parent, text="Username: ")
        trans.grid(row=4, column=0)

        vcmd = (self.parent.register(self.valid), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        uentry = Entry(self.parent, width=20, bg="white", validate="key", validatecommand=vcmd)
        uentry.grid(row=4, column=1, columnspan=2)

        trans = Label(self.parent, text="Actions: ")
        trans.grid(row=6, column=0)

        changepw = Button(self.parent, text="Change\nPassword", command=self.getNewPw)
        changepw.grid(row=6, column=1)

        delete = Button(self.parent, text="Delete", command=self.delUser)
        delete.grid(row=6, column=2)

        start = Button(self.parent, text="Start Server Daemon", command=self.govnah.startServer)
        start.grid(row=9, column=0, columnspan=3)

        self.uinfo = Label(self.parent, text="")
        self.uinfo.grid(row=5, column=1, columnspan=2)

        pathLabel = Label(self.parent, text="OneDir Path:")
        pathLabel.grid(row=7, column=0)

        self.path = self.govnah.path
        self.pathEntry = Entry(self.parent, width=20, bg="white")
        self.pathEntry.insert(END, self.path)
        self.pathEntry.grid(row = 7, column=1, columnspan=2)

        performChange = Button(self.parent, text="Change OneDir\nDirectory", command=self.chngPath)
        performChange.grid(row=8, column=1, columnspan=2)

        self.img = ImageTk.PhotoImage(file='img/logo50.png')
        logoLabel = Label(self.parent, image=self.img)
        logoLabel.grid(row=10, column=0)

        slogan = Label(self.parent, text="This Directory\nis a OneDir!", font=("Helvetica", 10, "bold italic"))
        slogan.grid(row = 10, column=1, columnspan=2)

        self.log.insert(END, "Howdy Admin, Welcome to the Server Interface \n\n")

    def chngPath(self):
        self.path = self.pathEntry.get()
        self.govnah.changeDir(self.path)

    def valid(self, d, i, P, s, S, v, V, W):
        if not self.lock:
            self.uname = P
            if self.govnah.userExists(P):
                self.goodMessage("Valid User")
            else:
                self.badMessage("User not Found")
        return not self.lock

    def goodMessage(self, msg):
        self.uinfo.config(text=msg, fg="forest green")

    def badMessage(self, msg):
        self.uinfo.config(text=msg, fg="red")

    def alert(self):
        top = Toplevel()
        top.title("Are you sure?")

        msg = Message(top, text="Are you sure?")
        msg.pack()

        button = Button(top, text="Dismiss", command=top.destroy)
        button.pack()

        self.center(top)

    def areYouSureDelete(self):
        return tkMessageBox.askyesno("Confirmation", "Are you sure you want delete " + self.uname)

    def delUser(self):
        if self.govnah.userExists(self.uname):
            self.lock = True
            if self.areYouSureDelete():
                self.govnah.delUser(str(self.uname))
                self.appendText("User: " + self.uname + " successfully deleted.")
                self.appendText("")
            self.lock = False


    def appendText(self, text):
        self.log.insert(END, str(text) + "\n")
        self.log.see(END)

    def getNewPw(self):
        if self.govnah.userExists(self.uname):
            self.unameforpwch = self.uname
            self.lock = True
            self.top = Toplevel()
            self.top.protocol('WM_DELETE_WINDOW', self.closePwWindow)
            self.top.title = "Change Password"
            l = Label(self.top, text="Enter a new Password for user: " + self.unameforpwch)
            l.grid(row=0, columnspan=2)
            self.entry = Entry(self.top, width=20, bg="white")
            self.entry.grid(row=1, columnspan=2)
            n = Button(self.top, text="Cancel", command=self.closePwWindow)
            n.grid(row=2, column=0)
            y = Button(self.top, text="Proceed", command=self.confirmPwChange)
            y.grid(row=2, column=1)
            self.center(self.top)

    def closePwWindow(self):
        self.lock = False
        self.top.destroy()
        self.appendText("Password for " + self.unameforpwch + " not changed")
        self.appendText("")

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


class DaemonView(Frame):


    def __init__(self, parent, govnah):
        self.parent = parent
        self.govnah = govnah
        self.initUI()
        #self.out = self.govnah.daemon.stdout
        #self.err = self.govnah.daemon.stderr

    def initUI(self):

        scrollbar = Scrollbar(self.parent)
        scrollbar.grid(row=0, column=1, sticky=N+S)

        self.log = ReadOnlyText(self.parent, bg="white", undo=False, yscrollcommand=scrollbar.set, width=80)
        self.log.tag_config("errorstring", foreground="#CC0000")
        self.log.grid(row=0, column=0)

        button = Button(self.parent, text="Stop this Daemon", command=self.stop)
        button.grid(row=1, columnspan=2)

        scrollbar.config(command=self.log.yview)

    def stop(self):
        self.govnah.stopServer()

    def update(self):
        try:
            msg = self.govnah.dioq.get_nowait()
            if msg:
                self.log.insert(END, msg + "\n")
        except Queue.Empty:
            pass

        try:
            msg = self.govnah.dioeq.get_nowait()
            if msg:
                self.log.insert(END, msg + "\n", ('errorstring',))
        except Queue.Empty:
            pass

        self.parent.after(50, self.update)


class SInterface():

    def __init__(self):
        self.prefs = DbOps.ServerPrefs()
        self.path = self.prefs.getOption("path")
        self.db = DbOps.DbOps(self.path)
        self.daemon = None
        self.dview = None
        self.dioq = Queue.Queue()
        self.dioeq = Queue.Queue()
        self.root = Tk()
        self.root.geometry("1150x400+100+100")
        img = ImageTk.PhotoImage(file='img/logo50.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        self.view = View(self.root, self)
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.mainloop()

    def close(self):
        self.stopServer()
        self.root.destroy()

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

    def printTransByUser(self):
        self.view.appendText("The list of transactions, sorted by username. (Unique ID, username, type, path, size, timestamp)")
        self.printSanitizeDBstrDub(self.db.getTransByUser())

    def printTransBySize(self):
        self.view.appendText("The list of transactions, sorted by size. (Unique ID, username, type, path, size, timestamp)")
        self.printSanitizeDBstrDub(self.db.getTransBySize())

    def printTransByTime(self):
        self.view.appendText("The list of transactions, sorted by timestamp. (Unique ID, username, type, path, size, timestamp)")
        self.printSanitizeDBstrDub(self.db.getTransByTime())

    def printTransByType(self):
        self.view.appendText("The list of transactions, sorted by type. (Unique ID, username, type, path, size, timestamp)")
        self.printSanitizeDBstrDub(self.db.getTransByType())

    def printSanitizeDBstr(self, results):
        for entry in results:
            t = ""
            for item in entry:
                t = t + str(item) + "\t"
            self.view.appendText(t)
        self.view.appendText("")

    def printSanitizeDBstrDub(self, results):
        for entry in results:
            t = ""
            for item in entry:
                t = t + str(item) + "\t\t"
            self.view.appendText(t)
        self.view.appendText("")

    def userExists(self, userName):
        return self.db.userExists(userName)

    def delUser(self, userName):
        if self.db.userExists(userName):
            self.db.deleteUser(userName)

    def chUserPass(self, usr, pw):
        if self.db.userExists(usr):
            self.db.updatePassword(usr, pw)

    def setOption(self, option, value):
        if self.prefs.optionExists(option):
            self.prefs.setOption(option, value)

    def changeDir(self, path):
        self.prefs.checkPath(path)
        self.prefs.setOption("path", path)
        self.path = path
        self.db = DbOps.DbOps(self.path)

    def startServer(self):
        if self.daemon is None:
            self.droot = Toplevel()
            self.droot.geometry("585x380+100+100")
            self.droot.title("OneDir at " + self.path)
            self.droot.protocol('WM_DELETE_WINDOW', self.stopServer)
            self.view.appendText("Start Daemon on path: " + self.path)
            self.daemon = subprocess.Popen(["python", "Server/Daemon/server_daemon.py", "--path", self.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.dview = DaemonView(self.droot, self)
            self.diot = Piper(self)
            self.diot.start()
            self.dview.update()
        else:
            self.view.appendText("Daemon Already started on " + self.path + ". Please stop it first.")

    def stopServer(self):
        if self.daemon is not None:
            self.diot.stopThread()
            self.daemon.terminate()
            self.daemon.kill()
            self.daemon = None
            self.droot.destroy()
        else:
            self.view.appendText("No Daemon Currently Running")

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


class Piper (threading.Thread):
    def __init__(self, govnah):
        threading.Thread.__init__(self)
        self.govnah = govnah
        self.stop = False

    def stopThread(self):
        self.stop = True

    def run(self):
        while not self.stop:
            while True:
                try:
                    line = self.govnah.daemon.stdout.readline()
                except AttributeError:
                    break

                if not line:
                    break
                else:
                    self.govnah.dioq.put(line, True)

            while True:
                try:
                    line = self.govnah.daemon.stderr.readline()
                except AttributeError:
                    break

                if not line:
                    break
                else:
                    self.govnah.dioeq.put(line, True)