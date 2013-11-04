import os
import datetime

def modification_date(base_path, filename):
    t = os.path.getmtime(os.path.join(base_path, filename))
    return t
    #return datetime.datetime.fromtimestamp(t)

def modification_dir(base_path):
	for file in os.listdir(base_path):
		print file, modification_date(base_path, file)

modification_dir("/home/venkat/Documents")
