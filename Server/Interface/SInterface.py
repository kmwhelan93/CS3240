__author__ = 'justin'

from Tkinter import *
from ttk import Frame, Style
from Server import DbOps
from idlelib.WidgetRedirector import WidgetRedirector
import tkMessageBox
from PIL import Image, ImageTk
import tkFont

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

        printTransType = Button(self.parent, text="By Type")
        printTransType.grid(row=2, column=1)

        printTransTime = Button(self.parent, text="By Time")
        printTransTime.grid(row=2, column=2)

        trans = Label(self.parent, text="Username: ")
        trans.grid(row=3, column=0)

        vcmd = (self.parent.register(self.valid), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        uentry = Entry(self.parent, width=20, bg="white", validate="key", validatecommand=vcmd)
        uentry.grid(row=3, column=1, columnspan=2)

        trans = Label(self.parent, text="Actions: ")
        trans.grid(row=5, column=0)

        changepw = Button(self.parent, text="Change\nPassword", command=self.getNewPw)
        changepw.grid(row=5, column=1)

        delete = Button(self.parent, text="Delete", command=self.delUser)
        delete.grid(row=5, column=2)

        start = Button(self.parent, text="Start Server Daemon")
        start.grid(row=6, column=0, columnspan=3)

        self.uinfo = Label(self.parent, text="")
        self.uinfo.grid(row=4, column=1, columnspan=2)


        self.img = ImageTk.PhotoImage(file='../../img/logo50.png')
        logoLabel = Label(self.parent, image=self.img)
        logoLabel.grid(row=7, column=0)

        slogan = Label(self.parent, text="This Directory\nis a OneDir!", font=("Helvetica", 10, "bold italic"))
        slogan.grid(row = 7, column=1, columnspan=2)

        self.log.insert(END, "Howdy Admin, Welcome to the Server Interface \n\n")

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


class SInterface():

    def __init__(self):
        self.db = DbOps.DbOps()
        root = Tk()
        root.geometry("1150x400+100+100")
        img = ImageTk.PhotoImage(file='../../img/logo50.png')
        root.tk.call('wm', 'iconphoto', root._w, img)
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

    def userExists(self, userName):
        return self.db.userExists(userName)

    def delUser(self, userName):
        if self.db.userExists(userName):
            self.db.deleteUser(userName)

    def chUserPass(self, usr, pw):
        if self.db.userExists(usr):
            self.db.updatePassword(usr, pw)

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
