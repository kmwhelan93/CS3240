from threading import Thread
from socket import socket
from Queue import Queue
#from command_thread import command_thread
import thread
import time
import logging
import sys
import json
from common import get_timestamps

from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, stdio, defer

from twisted.internet import task

from get_modification import SyncEventHandler
from watchdog.observers import Observer
from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input

import os
import shutil
import optparse
from LocalMachine.preferences_Operations import preferenceOperations

class Echo(LineReceiver):
    delimiter = '\n'

    def __init__(self, q, ignore, files_path, username, password, factory, server_ip='127.0.0.1', server_port=1234):
        self.username = username
        self.password = password
        self.q = q
        self.server_ip = server_ip
        self.server_port = server_port
        self.files_path = files_path
        self.connected = False
        self.ignore = ignore
        self.file_to_update = None
        self.factory = factory

        self.file_handler = None
        self.file_data = ()

    def connectionMade(self):
        #self.factory2 = EchoClientFactory(self.q, self.files_path, self.ignore, self.server_ip, self.username, self.password)
        #self.connection = reactor.connectTCP(self.server_ip, self.server_port, self.factory2)
        #self.factory.deferred.addCallback(self._display_response)

        self.connected = False
        self.task_id = task.LoopingCall(self.callback)
        self.task_id.start(.5)
        self.setLineMode()
        task.LoopingCall(self.get_files).start(10)

    def get_files(self):
        username = self.username
        password = self.factory.get_password()
        timestamps = get_timestamps(self.factory.get_directory())
        object = {"command": "get", "username": username, "password": password, "timestamps": timestamps}
        if (self.connected == True and self.factory.command_out == False and len(q) == 0):
            self.q.append(object)

    def callback(self):
        #print 'callback'
        print 'COMMAND OUT ', self.factory.command_out
        if (self.connected == True and self.factory.command_out == False and len(q) > 0):
            #print 'sending command'
            self.files_path = self.factory.get_directory()
            first = q.pop(0)
            if (first['command'] == 'get' and len(q) > 0):
                first = q.pop(0)
            print q
            self._sendCommand(first)



    def rawDataReceived(self, data):
        if 'FILEDOESNOTEXISTFAIL2389' in data:
            self.factory.command_out = False
            self.setLineMode()
            self.file_handler = None
            return
        file_path = self.file_to_update
        self.factory.file_syncing = file_path
        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
        if data.endswith('\r\n'):
            # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.setLineMode()

            self.file_handler.close()
            self.file_handler = None
            self.factory.command_out = False
            self.factory.file_syncing = None
        else:
            self.file_handler.write(data)
    def lineReceived(self, data):
        self.files_path = self.factory.get_directory()
        print 'data received ' + data
        print data
        print self.factory.get_directory()
        if (data == "init"):
            self.connected = True
        else:
            files = json.loads(data.strip())
            if 'command' in files and files['command'] == 'put':
                if not os.path.exists(files['local_file_path']):
                    self.factory.command_out = False
                    self.factory.connection.transport.write('\r\n')
                    return
                self.setRawMode()
                for bytes in read_bytes_from_file(files['local_file_path']):
                    self.factory.connection.transport.write(bytes)

                self.factory.connection.transport.write('\r\n')

                # When the transfer is finished, we go back to the line mode
                self.setLineMode()
                return
            elif 'command' in files and files['command'] == 'done uploading':
                self.factory.command_out = False
            elif files['success'] == False:
                print 'Authentication failed with username: ' + self.username + ' and password: ' + self.password
                self.factory.command_out = False
            elif "directories" in files.keys():
            # get directories first
                files['directories'].sort()
                directories = []
                for file in files['remove']:
                    path = os.path.join(self.files_path, file)
                    if os.path.isfile(path):
                        os.unlink(path)
                    else:
                        directories.append(path)
                directories.sort(reverse=True)
                for dir in directories:
                    if os.path.isdir(dir):
                        shutil.rmtree(dir)

                for directory in files['directories']:
                    path = os.path.join(self.files_path, directory)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    self.ignore.append(self.clean_file_string(directory))
                # because files need the directories to exist
                # TODO THIS NEEDS TO CHANGE
                for file in files['files']:
                    path = os.path.join(self.files_path, file)
                    q.insert(0, {'command': 'get_file', 'rel_path': file})
                self.factory.command_out = False
            elif files['success'] == True:
                self.factory.command_out = False

    def _sendCommand(self, object):
        self.factory.command_out = True
        object["username"] = self.username
        object["password"] = self.factory.get_password()
        self.password = self.factory.get_password()
        self.files_path = self.factory.get_directory()
        sendObj = {"username": self.username, "password": self.password}
        command = object["command"]
        print 'command to be sent: ' + json.dumps(object)
        print 'ignore is' + json.dumps(self.ignore)
        if command in ['move', 'create', 'get', 'delete']:
            if (command=='create' or command=="delete") and self.clean_file_string(object['file']) in self.ignore:
                self.ignore.remove(self.clean_file_string(object['file']))
                print 'ignored ' + object['file']
                self.factory.command_out = False
                return
            self.sendLine(json.dumps(object))
        elif command == 'get_file':
            self.file_to_update = os.path.join(self.files_path, self.clean_file_string(object['rel_path']))
            self.ignore.append(self.clean_file_string(object['rel_path']))
            self.setRawMode()
            self.factory.file_syncing = self.file_to_update
            self.sendLine(json.dumps(object))
        elif command == 'put':
            if self.clean_file_string(object['file'].replace(self.files_path, "")) in self.ignore:
                self.ignore.remove(self.clean_file_string(object['file'].replace(self.files_path, "")))
                print 'ignored ' + object['file']
                self.factory.command_out = False
                return
            try:
                file_path = object['file']
                filename = object['file'].replace(self.files_path, "")
            except IndexError:
                self._display_message('Missing local file path or remote file name')
                self.factory.command_out = False
                return

            if not os.path.isfile(file_path):
                self._display_message('This file does not exist')
                self.factory.command_out = False
                return

            file_size = os.path.getsize(file_path) / 1024
            print self.factory.command_out
            print 'Uploading file: %s (%d KB)' % (filename, file_size)
            object = {"command": "put", "relative_path": filename, 'local_file_path': file_path}
            sendObj = dict(object.items() + sendObj.items())
            self.sendLine(json.dumps(sendObj))

    def _display_message(self, message):
        print message

    def clean_file_string(self, string):
        if (len(string) > 0):
            if string[0] == '/':
                return string[1:]
        return string



class EchoClientFactory(ClientFactory):
    def __init__(self, q, files_path, ignore, server_ip, username, password):
        self.pref = preferenceOperations()
        self.q = q
        self.files_path = files_path
        self.ignore = ignore
        self.server_ip = server_ip
        self.username = username
        self.password = password
        self.command_out = False
        self.connection = None
        self.file_syncing = None
        print self.get_password()
        print self.get_directory()

    def get_password(self):
        row = self.pref.getUserRow(self.username)
        self.password = row[1]
        return row[1]

    def get_directory(self):
        row = self.pref.getUserRow(self.username)
        return row[3]

    def set_connection(self, connection):
        self.connection = connection

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.echo = Echo(q=self.q, ignore=self.ignore, username=self.username, password=self.password, files_path=self.files_path, server_ip=self.server_ip, factory=self)
        return self.echo

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

parser = optparse.OptionParser()
parser.add_option('--path', action='store', type='string', dest='path',
                      help='local directory for syncing')
parser.add_option('--ip', action='store', type='string', dest='ip',
                      help='Server IP')
parser.add_option('--user', action='store', type='string', dest='user',
                      help='Username')
parser.add_option('--password', action='store', type='string', dest='password',
                      help='Password')
(options, args) = parser.parse_args()

server_ip = ""
username = ""
password = ""
if (options.user is None):
    print "No username specified"
    sys.exit(1)
if (options.password is None):
    print "No password specified"
    sys.exit(1)
if (options.path is None):
    print "No path specified"
    sys.exit(1)
if (options.ip is None):
    print "No server IP specified assuming localhost"
    server_ip = "localhost"
else:
    server_ip = options.ip
username = options.user
password = options.password
files_path = options.path

def watchDog(base_path, q, ignore, f):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = SyncEventHandler(q, base_path, ignore, f)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


q = []
ignore = []

f = factory = EchoClientFactory(q=q, files_path=files_path, ignore=ignore, server_ip=server_ip, username=username, password=password)

thread.start_new_thread(watchDog, (files_path, q, ignore, f))
print 'username: ' + username + " password: " + password + " files_path " + files_path

#reactor.connectTCP("localhost", 1234, factory)
connection = reactor.connectTCP(server_ip, 1234, factory)
factory.connection = connection
reactor.run()
