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

import os
import optparse

import json

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
        print line
        if not command in COMMANDS:
            self.transport.write('Invalid command\n')
            self.transport.write('ENDMSG\n')
            return
        if command == 'move':
            print "Receiving move from " + data['src'] + " to " + data['dest']
            os.renames(os.path.join(self.factory.files_path, data["username"], data['src']), os.path.join(self.factory.files_path, data['username'], data['dest']))
        elif command == 'create':
            print "Receiving create for " + data['file']
            if data['what'] == 'directory':
                print os.path.join(self.factory.files_path, data["username"], data['file'])
                os.mkdir(os.path.join(self.factory.files_path, data["username"], data['file']))
            else:
                os.mknod(os.path.join(self.factory.files_path, data["username"], data['file']))
        elif command == 'get':
            timestamps = self.get_timestamps(data['username'])
            retVal = {'files': {}, 'directories': [], "remove": []}
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

        elif command == 'help':
            self.transport.write('Available commands:\n\n')

            for key, value in COMMANDS.iteritems():
                self.transport.write('%s - %s\n' % (value[0], value[1]))

            self.transport.write('ENDMSG\n')
        elif command == 'quit':
            self.transport.loseConnection()

    def modification_date(self, username, filename):
        t = os.path.getmtime(os.path.join(self.factory.files_path, username, filename))
        return t
        #return datetime.datetime.fromtimestamp(t)

    def get_timestamps(self, username):
        timestamps = {}
        for file in os.listdir(os.path.join(self.factory.files_path, username)):
            if (not file.endswith("~")):
                modTime = self.modification_date(username, file)
                timestamps[file] = modTime
            #print self.timestamps
        return timestamps

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
        options.path = "/home/student/Documents/CSA/server/"

    display_message('Listening on port %d, serving files from directory: %s' % (options.port, options.path))

    reactor.listenTCP(options.port, FileTransferServerFactory(options.path))
    reactor.run()
