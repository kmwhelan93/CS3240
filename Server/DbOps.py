__author__ = 'Justin Ingram'

import sqlite3, hashlib
from datetime import datetime

class DbOps:

    def __init__(self):
        # Connect to the database. Name should be preceeded with a . so its a hidden file
        self.db = sqlite3.connect('../.oneDir.db')
        # Get a cursor object for operations
        self.cur = self.db.cursor()
        # Get a SHA3 256 bit hasher for storing passwords
        self.hash256 = hashlib.sha256()
        self.setup()

    def setup(self):
        # A method to make sure that all our tables in the database are initialized and ready to go
        self.cur.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY ASC, username TEXT, password TEXT, ts TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY ASC, username TEXT, type TEXT, path TEXT, ts TEXT)")
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

    def recordTrans(self, userName, type, path):
        self.cur.execute("INSERT INTO transactions VALUES(?,?,?,?,?)",[None, userName, self.hash256.hexdigest(), path, datetime.now()])

    def finish(self):
        self.db.close()

    def start(self):
        self.createUser("zebra", "hello")


if __name__== '__main__':
     odsd = DbOps()
     odsd.start()
     print odsd.getUsersByTime()
     print odsd.getUsersByUName()

     odsd.finish()