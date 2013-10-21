
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

import sys

con = sqlite3.connect ('prefs.db')

with con:

    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS Prefs")
    cur.execute ("CREATE TABLE Prefs (Id INTEGER PRIMARY KEY, Username TEXT ,\
                  Password TEXT, AutoSync INTEGER)")
    cur.execute("INSERT INTO Prefs VALUES (NULL,'User1', 'password1', 1)")
    cur.execute("INSERT INTO Prefs VALUES (NULL,'User2', 'password2', 1)")
    cur.execute("INSERT INTO Prefs VALUES (NULL,'User3', 'password3', 1)")

    cur.execute("SELECT * FROM Prefs")
    rows = cur.fetchall()
    for row in rows:
        print row






