import subprocess
import os
import pickle
import sys
import paramiko
from scp import SCPClient

def get_scp(host, user):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname = host,
                username = user,
                password = os.environ["PASS"])
    scp = SCPClient(ssh.get_transport())
    return scp

def build_list(dir_path, location):
    scp = get_scp("10.214.14.28", "root")
    scp.get(os.path.join(location, "files.txt"))
    with open("files.txt", 'r') as f:
        filed = set(f.read().split())
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and not f in filed]
    return files

if __name__ == "__main__":
    try:
        dir_path = sys.argv[1]
    except:
        dir_path = "../Tweets/"
    try:
        location = sys.argv[2]
    except:
        location = "./Data/Tweets/"
    scp = get_scp("10.214.14.28", "root")
    files = build_list(dir_path, location)
    try:
        while(len(files) > 0):
            file_name = files.pop()
            print("Sending File: ", file_name, end = " ")
            scp.put(files.pop(), location)
            print("(Completed)")
    except:
        os.unlink("files.txt")
