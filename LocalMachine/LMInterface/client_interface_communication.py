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


'''
SEND COMMANDS WITH THE FOLLOWING FORMATS:
{'command':'register', 'username':'<username>', 'password':'<password>'}
    returns: {'success':<boolean>} indicating successful creation -- if false, user already exists

{'command': 'authenticate', 'username':'<username>', 'password':'<password>'}
    returns {'success':<boolean>, 'reason':<reason>} -- <reason> is one of ['user does not exist', 'incorrect password']

{'command': 'change password', 'username':'<username>', 'old_password':'<password>', 'new_password':'<new_password>'}
    returns {'success':<boolean>, 'reason':<reason>} -- <reason> is one of ['user does not exist', 'incorrect password']
'''
class Echo(LineReceiver):
    delimiter = '\n'

    def __init__(self, server_ip='127.0.0.1', server_port=1234):
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected = False

    def connectionMade(self):

        self.connected = False
        self.setLineMode()

    def dataReceived(self, data):
        print 'data received ' + data
        if (data == "init\n"):
            self.connected = True


    def _sendCommand(self, object):
        self.sendLine(json.dumps(object))




class EchoClientFactory(ClientFactory):
    def __init__(self,  server_ip):
        self.server_ip = server_ip
        self.ci = None

    def set_ci(self, ci):
        self.ci = ci

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        self.echo = Echo(self.server_ip)
        return self.echo

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason


#KEVIN: 172.25.108.150
#VENKAT: 172.27.108.88

def client_interface(factory):
    ci = clientInterface(factory)

parser = optparse.OptionParser()
parser.add_option('--server_ip', action='store', type='string', dest='server_ip',
                      help='ip address of server')
(options, args) = parser.parse_args()
if (options.server_ip == None):
    options.server_ip = 'localhost'


factory = EchoClientFactory(server_ip = options.server_ip,)
thread.start_new_thread(client_interface, (factory,))



reactor.connectTCP(options.server_ip, 1234, factory)
reactor.run()








