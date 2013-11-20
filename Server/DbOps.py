__author__ = 'Justin Ingram'

import sqlite3, hashlib
from datetime import datetime
import os

class DbOps:

    def __init__(self, path):
        # Connect to the database. Name should be preceeded with a . so its a hidden file
        if not path:
            self.path = str(os.getenv("HOME")) + "/OneDir"
        else:
            self.path = path

        print self.path + '/.oneDir.db'
        self.db = sqlite3.connect(self.path + '/.oneDir.db')
        # Get a cursor object for operations
        self.cur = self.db.cursor()
        # Get a SHA3 256 bit hasher for storing passwords
        self.hash256 = hashlib.sha256()
        self.setup()
        self.start()

    def setup(self):
        # A method to make sure that all our tables in the database are initialized and ready to go
        self.cur.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY ASC, username TEXT, password TEXT, ts TEXT, UNIQUE(username) ON CONFLICT IGNORE)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY ASC, username TEXT, type TEXT, path TEXT, size INTEGER, ts TEXT)")

        # before exiting method
        self.db.commit()

    def userExists(self, userName):
        self.cur.execute('SELECT * FROM user WHERE username=?',[userName])
        result = self.cur.fetchall()
        if(len(result) > 0):
            return True
        else:
            return False

    def createUser(self, userName, password):
        if not self.userExists(userName):
            self.hash256.update(password)
            self.cur.execute("INSERT INTO user VALUES(?,?,?,?)",[None, userName, self.hash256.hexdigest(), datetime.now()])
            self.db.commit()
            return True
        else:
            return False

    def deleteUser(self, userName):
        self.cur.execute("DELETE FROM user WHERE username=?",[userName])
        self.db.commit()

    def updatePassword(self, userName, password):
        if self.userExists(userName):
            self.hash256.update(password)
            self.cur.execute("UPDATE user SET password=? WHERE username=?", [self.hash256.hexdigest(),userName])
            self.db.commit()
            return True
        else:
            return False

    def authUser(self, userName, password):
        self.cur.execute('SELECT * FROM user WHERE username=?',[userName])
        userData = self.cur.fetchone()
        self.hash256.update(password)
        if len(userData) > 0:
            if userData(2) is self.hash256.hexdigest():
                return True

        return False

    def getUsersByTime(self):
        self.cur.execute("SELECT * FROM user ORDER BY DATETIME(ts) DESC")
        return self.cur.fetchall()

    def getUsersByUName(self):
        self.cur.execute("SELECT * FROM user ORDER BY username ASC")
        return self.cur.fetchall()

    def getTransByUser(self):
        self.cur.execute("SELECT * FROM transactions ORDER BY username ASC")
        return self.cur.fetchall()

    def getTransBySize(self):
        self.cur.execute("SELECT * FROM transactions ORDER BY size ASC, username ASC")
        return self.cur.fetchall()

    def getTransByTime(self):
        self.cur.execute("SELECT * FROM transactions ORDER BY DATETIME(ts) DESC")
        return self.cur.fetchall()

    def getTransByType(self):
        self.cur.execute("SELECT * FROM transactions ORDER BY type ASC, username ASC")
        return self.cur.fetchall()

    def recordTrans(self, userName, type, size, path):
        self.cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?,?)",[None, userName, type, path, size, datetime.now()])

    def finish(self):
        self.db.close()

    def start(self):
        self.createUser("zebra", "hello")
        self.createUser("justin", "hello")
        self.recordTrans("justin", "put", 1024, "/home/justin")
        self.recordTrans("zebra", "put", 856, "/home/zebra")


class ServerPrefs:


    def __init__(self):
        self.db = sqlite3.connect('.serverPrefs.db')
        # Get a cursor object for operations
        self.cur = self.db.cursor()
        self.setup()

    def setup(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS serveropts(option TEXT, optval TEXT, UNIQUE(option) ON CONFLICT REPLACE)")
        self.checkInitPath()

    def checkInitPath(self):
        if not self.optionExists("path"):
            self.path = str(os.getenv("HOME")) + "/OneDir"
            self.setOption("path", self.path)
            if not os.path.exists(self.path):
                os.mkdir(self.path)
        else:
            self.path = self.getOption("path")

    def checkPath(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = path

    def setOption(self, option, value):
        self.cur.execute("INSERT OR REPLACE INTO serveropts (option, optval) values (?,?)", [option, value])
        self.db.commit()

    def optionExists(self, option):
        self.cur.execute("SELECT * FROM serveropts WHERE option=?",[option])
        result = self.cur.fetchall()
        if(len(result) > 0):
            return True
        else:
            return False

    def getOption(self, option):
        if self.optionExists(option):
            self.cur.execute("SELECT * FROM serveropts WHERE option=?", [option])
            result = self.cur.fetchone()
            return result[1]

if __name__== '__main__':
     odsd = DbOps()
     odsd.start()
     print odsd.getUsersByTime()
     print odsd.getUsersByUName()

     odsd.finish()