CS3240
======

Repository for CS 3240 project OneDir:
Latest commit changes: 
inotify.py contains a patch to watch for files that are deleted from the linux file system
(linux actually moves the file to trash rather than deleting the contents of the file). Please copy this to your
usr/local/lib/python2.7/dist-packages/watchdog/observers folder. It will already contain a inotify.py file so just
open that in a sudo gedit editor and copy/paste the contents of the this into that one.

To run the program:
1. Check through the client/server daemon and change all directories paths to what you want it to watch (change it back before you push)
2. Run the server daemon
3. Run the client daemon
4. Create/modify/delete stuff in the client or server directory and it should transmit the changes

