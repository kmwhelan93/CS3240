import hashlib
from datetime import datetime
import os

COMMANDS = {
    'list': ('list', 'Displays a list of all the available files'),
    'get': ('get <remote filename>', 'Downloads a file with a given filename'),
    'put': ('put <local file path> <remote file name>', 'Uploads a file with a given filename'),
    'help': ('help', 'Displays a list of all the available commands'),
    'quit': ('quit', 'Disconnects from the server'),
    'move': ('move', 'Moves a file on server'),
    'create': ('create', 'Creates a file on server'),
    'delete': ('delete', 'Deletes a file on server'),
}


def timestamp():
    """ Returns current time stamp. """
    return '[%s]' % (datetime.strftime(datetime.now(), '%H:%M:%S'))


def display_message(message):
    """ Displays a message with a prepended time stamp. """

    print '%s %s' % (timestamp(), message)


def validate_file_md5_hash(file, original_hash):
    """ Returns true if file MD5 hash matches with the provided one, false otherwise. """

    if get_file_md5_hash(file) == original_hash:
        return True

    return False


def get_file_md5_hash(file):
    """ Returns file MD5 hash"""

    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)

    return md5_hash.hexdigest()


def read_bytes_from_file(file, chunk_size=8100):
    """ Read bytes from a file in chunks. """

    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)

            if chunk:
                yield chunk
            else:
                break


def clean_and_split_input(input):
    """ Removes carriage return and line feed characters and splits input on a single whitespace. """

    input = input.strip()
    input = input.split(' ')

    return input

# This is called by the both the server and the client
# The server calls it with base_path = server_path + username
# While the client calls it just with base_path
# Needs to get all of the files/directories in current directory. That means it
# must go more than a level deep (recursively)

def get_timestamps_helper(timestamps, base_path):
    for file in os.listdir(base_path):
        path = os.path.join(base_path, file)
        if(os.path.isfile(path)):
            modTime = os.path.getmtime(path)
            timestamps[path] = modTime
        elif(os.path.isdir(path)):
            modTime = os.path.getmtime(path)
            timestamps[path] = modTime
            get_timestamps_helper(timestamps, path)
    return timestamps

def get_timestamps(base_path):
    timestamps = get_timestamps_helper({}, base_path)
    for path in timestamps.keys():
        rel_path = os.path.relpath(path, base_path)
        timestamps[rel_path] = timestamps[path]
        timestamps.pop(path, timestamps[path])
    return timestamps
