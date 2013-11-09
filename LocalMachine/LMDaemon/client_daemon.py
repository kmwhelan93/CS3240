from threading import Thread
from socket import socket
from Queue import Queue
#from command_thread import command_thread
import thread
import time
import logging

from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol, stdio, defer

from get_modification import SyncEventHandler
from watchdog.observers import Observer
from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input

import os
import optparse


class Echo(LineReceiver):
    delimiter = '\n'

    def __init__(self, q, files_path='/home/student/Documents/CSA/local/', server_ip='127.0.0.1', server_port=1234):
        self.q = q
        self.server_ip = server_ip
        self.server_port = server_port
        self.files_path = files_path
        self.connected = False

    def connectionMade(self):
        self.factory = FileTransferClientFactory(self.files_path)
        self.connection = reactor.connectTCP(self.server_ip, self.server_port, self.factory)
        self.factory.deferred.addCallback(self._display_response)
        from twisted.internet import task

        self.connected = False
        self.task_id = task.LoopingCall(self.callback)
        self.task_id.start(1.0)

    def callback(self):
        print 'callback'
        if (self.connected == True and self.q.qsize() > 0):
            next_command = self.q.get()
            self._sendCommand(next_command)
            #self._sendCommand(next_command)


    def dataReceived(self, data):
        stdout.write(data)
        if data == 'init\n':
            self.connected = True
            print 'here'

    def _sendCommand(self, object):
        username = "kevin"
        password = "kevin"
        command = object["command"]
        print " command is " + command + " and path is " + object['file']
        if command == 'list' or command == 'help' or command == 'quit':
            self.connection.transport.write('%s\n' % (command))
        elif command == 'get':
            try:
                # this will change
                # all of these need to be relative
                filename = object['files']
            except IndexError:
                self._display_message('Missing filename')
                return
            self.connection.transport.write('%s %s\n' % (command, filename))
        elif command == 'put':
            try:
                # Full path of file on local machine
                file_path = object['file']
                # Relative path  (relative to OneDir Directory) for server to interpret
                filename = object['file'].replace(self.files_path, "")
                print "file path" + file_path + " filename " + filename
            except IndexError:
                self._display_message('Missing local file path or remote file name')
                return

            if not os.path.isfile(file_path):
                self._display_message('This file does not exist')
                return

            file_size = os.path.getsize(file_path) / 1024

            print 'Uploading file: %s (%d KB)' % (filename, file_size)

            self.connection.transport.write('PUT %s %s\n' % (filename, get_file_md5_hash(file_path)))
            self.setRawMode()

            for bytes in read_bytes_from_file(file_path):
                self.connection.transport.write(bytes)

            self.connection.transport.write('\r\n')

            # When the transfer is finished, we go back to the line mode
            self.setLineMode()
        else:
            self.connection.transport.write('%s %s\n' % (command, object['file']))

        self.factory.deferred.addCallback(self._display_response)

    def _display_response(self, lines=None):
        """ Displays a server response. """
        if lines:
            for line in lines:
                print '%s' % (line)
        self.factory.deferred = defer.Deferred()

    def _prompt(self):
        """ Prompts user for input. """
        self.transport.write('> ')

    def _display_message(self, message):
        """ Helper function which prints a message and prompts user for input. """
        print message


class FileTransferProtocol(LineReceiver):
    delimiter = '\n'

    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.file_data = ()

        print 'Connected to the server'

    def connectionLost(self, reason):
        self.file_handler = None
        self.file_data = ()

        print 'Connection to the server has been lost'
        reactor.stop()

    def lineReceived(self, line):
        if line == 'ENDMSG':
            self.factory.deferred.callback(self.buffer)
            self.buffer = []
        elif line.startswith('HASH'):
            # Received a file name and hash, server is sending us a file
            data = clean_and_split_input(line)

            filename = data[1]
            file_hash = data[2]

            self.file_data = (filename, file_hash)
            self.setRawMode()
        else:
            self.buffer.append(line)

    def rawDataReceived(self, data):
        filename = self.file_data[0]
        file_path = os.path.join(self.factory.files_path, filename)

        print 'Receiving file chunk (%d KB)' % (len(data))

        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')

        if data.endswith('\r\n'):
            # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.setLineMode()

            self.file_handler.close()
            self.file_handler = None

            if validate_file_md5_hash(file_path, self.file_data[1]):
                print 'File %s has been successfully transfered and saved' % (filename)
            else:
                os.unlink(file_path)
                print 'File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename)
        else:
            self.file_handler.write(data)


class FileTransferClientFactory(ClientFactory):
    protocol = FileTransferProtocol

    def __init__(self, files_path):
        self.files_path = files_path
        self.deferred = defer.Deferred()


class EchoClientFactory(ClientFactory):
    def __init__(self, q):
        self.q = q

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.echo = Echo(self.q)
        return self.echo

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason


def run_thread(q):
    watchDog('/home/student/Documents/CSA/local', q)

def watchDog(base_path, q):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    event_handler = SyncEventHandler(q, base_path)
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
#q.put('list')
#q.put('list')
#q.put('list')
#q.put('get helloWorld.txt')
#q.put('put /home/student/Documents/CSA/server/sendToServer.txt sendToServer.txt')
thread.start_new_thread(run_thread, (q, ))
#t = command_thread(q)


factory = EchoClientFactory(q)
reactor.connectTCP("localhost", 1234, factory)
reactor.run()








