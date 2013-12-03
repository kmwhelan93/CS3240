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


class Echo(LineReceiver):
    delimiter = '\n'

    def __init__(self, q, ignore, files_path, username, password, server_ip='127.0.0.1', server_port=1234):
        self.username = username
        self.password = password
        self.q = q
        self.server_ip = server_ip
        self.server_port = server_port
        self.files_path = files_path
        self.connected = False
        self.ignore = ignore

        self.file_handler = None
        self.file_data = ()
        self.command_out = False

    def connectionMade(self):

        self.connected = False
        self.task_id = task.LoopingCall(self.callback)
        self.task_id.start(.5)
        #self.setLineMode()
        task.LoopingCall(self.get_files).start(3)

    def get_files(self):
        username = self.username
        password = self.password
        timestamps = get_timestamps(self.files_path)
        object = {"command": "get", "username": username, "password": password, "timestamps": timestamps}
        self.q.put(object)

    def callback(self):
        #print 'callback'
        if (self.connected == True and self.command_out == False and self.q.qsize() > 0):
            #print 'sending command'
            self._sendCommand(self.q.get())

    def dataReceived(self, data):
        print 'data received ' + data
        if (data == "init\n"):
            self.connected = True
        else:
            files = json.loads(data.strip())
            if files['success'] == False:
                print 'Authentication failed with username and password get them here'
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
                    self.ignore.append(path)
                # because files need the directories to exist
                for file, content in files['files'].iteritems():
                    path = os.path.join(self.files_path, file)
                    f = open(path, 'w')
                    f.write(content['content'] +'')
                    f.close()
                    self.ignore.append(path)
        self.command_out = False

    def _sendCommand(self, object):
        self.command_out = True
        object["username"] = self.username
        object["password"] = self.password
        sendObj = {"username": self.username, "password": self.password}
        command = object["command"]
        if command == 'move' or command=='create' or command=='get' or command=="delete":
            if (command=='create' or command=="delete") and object['file'] in self.ignore:
                self.ignore.remove(object['file'])
                self.command_out = False
                return
            self.sendLine(json.dumps(object))
        elif command == 'put':
            if object['file'] in self.ignore:
                self.ignore.remove(object['file'])
                self.command_out = False
                return
            try:
                file_path = object['file']
                filename = object['file'].replace(self.files_path, "")
            except IndexError:
                self._display_message('Missing local file path or remote file name')
                self.command_out = False
                return

            if not os.path.isfile(file_path):
                self._display_message('This file does not exist')
                self.command_out = False
                return

            file_size = os.path.getsize(file_path) / 1024

            print 'Uploading file: %s (%d KB)' % (filename, file_size)
            f = open(file_path, 'r')
            object = {"command": "put", "local": filename, "content": f.read()}
            sendObj = dict(object.items() + sendObj.items())
            self.sendLine(json.dumps(sendObj))
            f.close()
    def _display_message(self, message):
        print message



class EchoClientFactory(ClientFactory):
    def __init__(self, q, files_path, ignore, server_ip, username, password):
        self.q = q
        self.files_path = files_path
        self.ignore = ignore
        self.server_ip = server_ip
        self.username = username
        self.password = password

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.echo = Echo(self.q, self.ignore, self.username, self.password, self.files_path, self.server_ip)
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

def watchDog(base_path, q, ignore):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = SyncEventHandler(q, base_path, ignore)
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


q = Queue()
ignore = []

thread.start_new_thread(watchDog, (files_path, q, ignore))


factory = EchoClientFactory(q, files_path, ignore, server_ip = server_ip, username, password)
#reactor.connectTCP("localhost", 1234, factory)
reactor.connectTCP(server_ip, 1234, factory)
reactor.run()
