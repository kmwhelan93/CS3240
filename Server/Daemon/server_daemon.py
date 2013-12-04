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
import sys
import shutil
import optparse
from common import get_timestamps


import hashlib
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

        self.file_to_update = ''

        self.c_interface_commands = ['authenticate', 'register']

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
        retVal = {"done": True, 'success': True}

        print line
        # client interface messages come in here
        if command in ['register', 'authenticate', 'change password']:
            if command == 'register':
                success = self.factory.register(data['username'], data['password'])
                self.sendLine(json.dumps({'type': 'register', 'success': success}))
            elif command == 'authenticate':
                print 'AUTHENTICATION RECEIVED'
                success = self.factory.auth(data['username'], data['password'])
                reason = ''
                if not success:
                    user_exists = self.factory.userExists(data['username'])
                    reason = 'incorrect password'
                    if not user_exists:
                        reason = 'user does not exist'
                self.sendLine(json.dumps({'type': 'authenticate', 'success': success, 'reason': reason}))
            elif command == 'change password':
                success = self.factory.auth(data['username'], data['old_password'])
                reason = ''
                if not success:
                    user_exists = self.factory.userExists(data['username'])
                    reason = 'incorrect password'
                    if not user_exists:
                        reason = 'user does not exist'
                if success:
                    print 'here'
                    success = self.factory.updatePassword(data['username'], data['new_password'])
                print {'type': 'change password', 'success': success, 'reason': reason}
                self.sendLine(json.dumps({'type': 'change password', 'success': success, 'reason': reason}))
            return

        # client daemon messages come in here
        if (not self.factory.auth(data['username'], data['password'])) and not command in self.c_interface_commands:
            retVal['success'] = False
            self.sendLine(json.dumps(retVal))
            return
        if not os.path.exists(os.path.join(self.factory.files_path, data['username'])):
                os.mkdir(os.path.join(self.factory.files_path, data['username']))
        if not command in COMMANDS:
            self.sendLine(json.dumps(retVal))
            return
        if command == 'move':
            print "Receiving move from " + data['src'] + " to " + data['dest']
            self.factory.db.recordTrans(data['username'], "move", 0, data['src'] + " to " + data['dest'])
            src_path = os.path.join(self.factory.files_path, data["username"], self.clean_file_string(data['src']))
            dest_path = os.path.join(self.factory.files_path, data["username"], self.clean_file_string(data['dest']))
            if os.path.exists(src_path):
                os.renames(src_path, dest_path)
            self.sendLine(json.dumps(retVal))
        elif command == 'register':
            print 'Receiving register for username ' + data['username']
            success = self.factory.db.createUser(data['username'], data['password'])
            self.sendLine(json.dumps({'success': success}))
            return
        elif command == 'authenticate':
            retVal['success'] = self.factory.auth(data['username'], data['password'])
            self.sendLine(json.dumps(retVal))
            return
        elif command == "delete":
            print "Receiving delete of " + data["what"] + " " + data['file']
            self.factory.db.recordTrans(data['username'], "delete", 0, data["what"] + " " + data['file'])
            path = os.path.join(self.factory.files_path, self.clean_file_string(data['username']), self.clean_file_string(data["file"]))
            if (os.path.exists(path)):
                if (data["what"] == "file"):
                    os.unlink(path)
                elif data["what"] == "directory":
                    shutil.rmtree(path)
            self.sendLine(json.dumps(retVal))
        elif command == 'create':
            print "Receiving create for " + data['file']
            if data['what'] == 'directory':
                path = os.path.join(self.factory.files_path, data["username"], self.clean_file_string(data['file']))
                if not os.path.exists(path):
                    os.mkdir(path)
            else:
                path = os.path.join(self.factory.files_path, data["username"], self.clean_file_string(data['file']))
                if not os.path.exists(path):
                    os.mknod(path)
            self.sendLine(json.dumps(retVal))
        elif command == 'get':
            #TODO GET DOESNT WORK FOR DIRECTORIES
            self.factory.db.recordTrans(data['username'], "get", 0, "/")
            if not os.path.exists(os.path.join(self.factory.files_path, data['username'])):
                os.mkdir(os.path.join(self.factory.files_path, data['username']))
            timestamps = get_timestamps(os.path.join(self.factory.files_path, data['username']))
            retVal = dict(retVal.items() + {'files': [], 'directories': [], "remove": []}.items())
            for file, stamp in timestamps.iteritems():
                if (not file in data['timestamps'] or stamp > data['timestamps'][file]):
                    path = os.path.join(self.factory.files_path, data['username'], self.clean_file_string(file))
                    if os.path.isdir(path):
                        retVal['directories'].append(file)
                    elif os.path.isfile(path):
                        retVal['files'].append(file)
            for file, stamp in data['timestamps'].iteritems():
                if not file in timestamps:
                    retVal['remove'].append(file)
            #print retVal
            self.sendLine(json.dumps(retVal))
        elif command == 'get_file':
            file_path = os.path.join(self.factory.files_path, data['username'], self.clean_file_string(data['rel_path']))
            if os.path.exists(file_path):
                self.setRawMode()
                for bytes in read_bytes_from_file(file_path):
                    self.transport.write(bytes)

                self.transport.write('\r\n')

                # When the transfer is finished, we go back to the line mode
                self.setLineMode()
            else:
                self.sendLine("FILEDOESNOTEXISTFAIL2389")
        elif command == 'put':
            try:
                filename = self.clean_file_string(data["relative_path"])
            except IndexError:
                self.transport.write('Missing filename or file MD5 hash\n')
                self.transport.write('ENDMSG\n')
                return

            file_path = os.path.join(self.factory.files_path, data['username'], filename)
            # Switch to the raw mode (for receiving binary data)
            self.factory.db.recordTrans(data['username'], "put", 0, file_path)
            print 'Receiving file: %s' % (filename)
            retVal['command'] = 'put'
            retVal['local_file_path'] = data['local_file_path']
            self.sendLine(json.dumps(retVal))
            self.file_to_update = file_path
            self.setRawMode()

        elif command == 'help':
            self.sendLine(json.dumps(retVal))
        elif command == 'quit':
            self.transport.loseConnection()
        else:
            self.sendLine(json.dumps(retVal))
    def clean_file_string(self, string):
        if (len(string) > 0):
            if string[0] == '/':
                return string[1:]
        return string

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

    def rawDataReceived(self, data):
        file_path = self.file_to_update

        display_message('Receiving file chunk (%d KB)' % (len(data)))

        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
        if data.endswith('\r\n'):
            print 'end of file'
            # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.setLineMode()

            self.file_handler.close()
            self.file_handler = None
            self.sendLine(json.dumps({'command': 'done uploading', 'success':True}))
        else:
            self.file_handler.write(data)


class FileTransferServerFactory(protocol.ServerFactory):
    protocol = FileTransferProtocol

    def __init__(self, files_path, db):
        self.files_path = files_path
        self.db = db

        self.clients = []
        self.files = None

    def auth(self, username, password):
        return self.db.authUser(username, password)

    def register(self, username, password):
        return self.db.createUser(username, password)

    def userExists(self, userName):
        return self.db.userExists(userName)

    def updatePassword(self, userName, password):
        print "Pass upate called"
        return self.db.updatePassword(userName, password)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', action='store', type='int', dest='port', default=1234,
                      help='server listening port')
    parser.add_option('--path', action='store', type='string', dest='path',
                      help='directory where the incoming files are saved')
    (options, args) = parser.parse_args()

    if (options.path == None):
        #options.path = "/home/student/Documents/CSA/server/" #os.path.join("C:\Users\Venkat\Documents", "test folder")
        print "NO PATH SPECIFIED"
        sys.exit(1)

    display_message('Listening on port %d, serving files from directory: %s' % (options.port, options.path))
    db = Server.DbOps.DbOps(options.path)
    reactor.listenTCP(options.port, FileTransferServerFactory(options.path, db))
    reactor.run()