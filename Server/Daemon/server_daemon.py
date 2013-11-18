# -*- coding: utf-8 -*-
#
# Name: Pyton Twisted binary file transfer demo (server)
# Description: Simple demo which shows how you can transfer binary files using
# the Twisted framework.
#
# Keep in mind that this is only a demo and there are many possible scenarios
# where program can break.
#
# Author: Tomaž Muraus (http://www.tomaz-muraus.info)
# License: GPL

# Requirements:
# - Python >= 2.5
# - Twisted (http://twistedmatrix.com/)

'''TODO: FIX CTRL + Z moving a folder out of another folder -- right now deletes existing folder
EX: folder structure first, first/second, first/second/third, ctrl+z --> first, second, second/third'''

import os
import shutil
import optparse
from common import get_timestamps

import json
import Server.DbOps
from twisted.internet import reactor, protocol
from twisted.protocols import basic

from common import COMMANDS, display_message, validate_file_md5_hash, get_file_md5_hash, read_bytes_from_file, clean_and_split_input


class FileTransferProtocol(basic.LineReceiver):
    delimiter = '\n'

    def connectionMade(self):
        self.factory.clients.append(self)
        self.file_handler = None
        self.file_data = ()
        self.sendLine("init")

        display_message(
            'Connection from: %s (%d clients total)' % (self.transport.getPeer().host, len(self.factory.clients)))

    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.file_handler = None
        self.file_data = ()

        display_message(
            'Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients)))

    def lineReceived(self, line):
        data = json.loads(line)
        command = data["command"]
        retVal = {"done": True}
        print line
        if not command in COMMANDS:
            self.sendLine(json.dumps(retVal))
            return
        if command == 'move':
            print "Receiving move from " + data['src'] + " to " + data['dest']
            if os.path.exists(os.path.join(self.factory.files_path, data["username"], data['src'])):
                os.renames(os.path.join(self.factory.files_path, data["username"], data['src']), os.path.join(self.factory.files_path, data['username'], data['dest']))
            self.sendLine(json.dumps(retVal))

        elif command == "delete":
            print "Receiving delete of " + data["what"] + " " + data['file']
            path = os.path.join(self.factory.files_path, data['username'], data["file"])
            if (os.path.exists(path)):
                if (data["what"] == "file"):
                    os.unlink(path)
                elif data["what"] == "directory":
                    shutil.rmtree(path)
            self.sendLine(json.dumps(retVal))
        elif command == 'create':
            print "Receiving create for " + data['file']
            if data['what'] == 'directory':
                path = os.path.join(self.factory.files_path, data["username"], data['file'])
                if not os.path.exists(path):
                    os.mkdir(path)
            else:
                os.mknod(os.path.join(self.factory.files_path, data["username"], data['file']))
            self.sendLine(json.dumps(retVal))
        elif command == 'get':
            #TODO GET DOESNT WORK FOR DIRECTORIES
            timestamps = get_timestamps(os.path.join(self.factory.files_path, data['username']))
            retVal = dict(retVal.items() + {'files': {}, 'directories': [], "remove": []}.items())
            for file, stamp in timestamps.iteritems():
                if (not file in data['timestamps'] or stamp > data['timestamps'][file]):
                    path = os.path.join(self.factory.files_path, data['username'], file)
                    if os.path.isdir(path):
                        retVal['directories'].append(file)
                    elif os.path.isfile(path):
                        f = open(path, 'r')
                        retVal['files'][file] = {"content": f.read()}
                        f.close()
            for file, stamp in data['timestamps'].iteritems():
                if not file in timestamps:
                    retVal['remove'].append(file)
            #print retVal
            self.sendLine(json.dumps(retVal))
        elif command == 'put':
            try:
                filename = data["local"]
            except IndexError:
                self.transport.write('Missing filename or file MD5 hash\n')
                self.transport.write('ENDMSG\n')
                return

            file_path = os.path.join(self.factory.files_path, data['username'], filename)
            # Switch to the raw mode (for receiving binary data)
            print 'Receiving file: %s' % (filename)
            f = open(file_path, 'w')
            f.write(data['content'])
            f.close()
            self.sendLine(json.dumps(retVal))

        elif command == 'help':
            self.sendLine(json.dumps(retVal))
        elif command == 'quit':
            self.transport.loseConnection()
        else:
            self.sendLine(json.dumps(retVal))

    def _get_file_list(self):
        """ Returns a list of the files in the specified directory as a dictionary:

        dict['file name'] = (file path, file size, file md5 hash)
        """

        file_list = {}
        for filename in os.listdir(self.factory.files_path):
            file_path = os.path.join(self.factory.files_path, filename)

            if os.path.isdir(file_path):
                continue

            file_size = os.path.getsize(file_path)
            md5_hash = get_file_md5_hash(file_path)

            file_list[filename] = (file_path, file_size, md5_hash)

        return file_list

    def _cleanAndSplitInput(self, input):
        input = input.strip()
        input = input.split(' ')

        return input


class FileTransferServerFactory(protocol.ServerFactory):
    protocol = FileTransferProtocol

    def __init__(self, files_path):
        self.files_path = files_path

        self.clients = []
        self.files = None


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', action='store', type='int', dest='port', default=1234,
                      help='server listening port')
    parser.add_option('--path', action='store', type='string', dest='path',
                      help='directory where the incoming files are saved')
    (options, args) = parser.parse_args()

    if (options.path == None):
        options.path = "/home/student/Documents/CSA/server/" #os.path.join("C:\Users\Venkat\Documents", "test folder")

    display_message('Listening on port %d, serving files from directory: %s' % (options.port, options.path))

    reactor.listenTCP(options.port, FileTransferServerFactory(options.path))
    reactor.run()

### SERVER DATABASE OPERATIONS... INSERTED BY JUSTIN ###
db = Server.DbOps.DbOps()
def auth(username, password):
    return db.authUser(username, password)

def register(username, password):
    return db.createUser(username, password)
