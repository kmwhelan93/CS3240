from threading import Thread
from socket import socket
from Queue import Queue
#from command_thread import command_thread
import thread
import time
import logging

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

from client_Interface import clientInterface


class Echo(LineReceiver):
    delimiter = '\n'

    def __init__(self, q, server_ip='127.0.0.1', server_port=1234):
        self.q = q
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected = False

        self.file_handler = None
        self.file_data = ()
        self.command_out = False

    def connectionMade(self):

        self.connected = False
        self.task_id = task.LoopingCall(self.callback)
        self.task_id.start(.5)
        #self.setLineMode()

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
        self.command_out = False

    def _sendCommand(self, object):
        self.command_out = True
        self.sendLine(json.dumps(object))

    def _display_message(self, message):
        print message



class EchoClientFactory(ClientFactory):
    def __init__(self, q, server_ip):
        self.q = q
        self.server_ip = server_ip

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.echo = Echo(self.q, self.server_ip)
        return self.echo

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason


#KEVIN: 172.25.108.150
#VENKAT: 172.27.108.88

def client_interface(q, ciq):
    ci = clientInterface(q, ciq)

parser = optparse.OptionParser()
parser.add_option('--server_ip', action='store', type='string', dest='server_ip',
                      help='ip address of server')
(options, args) = parser.parse_args()
if (options.server_ip == None):
    options.server_ip = 'localhost'

q = Queue()
ciq = Queue()
thread.start_new_thread(client_interface, (q, ciq))


factory = EchoClientFactory(q, server_ip = options.server_ip,)
reactor.connectTCP(options.server_ip, 1234, factory)
reactor.run()








