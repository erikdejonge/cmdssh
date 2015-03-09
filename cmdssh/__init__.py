# coding=utf-8
"""
pip
-
Active8 (09-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""

import os
import sys
import paramiko
import subprocess
import getpass
from os.path import join, expanduser
from consoleprinter import console_exception, console


def remote_cmd(server, cmd, username=None):
    """
    @type server: str, unicode
    @type cmd: str, unicode
    @type username: CryptoUser
    @return: None
    """
    if username is None:
        username = getpass.getuser()

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username)
    si, so, se = ssh.exec_command(cmd)
    so = so.read()
    se = se.read()

    if len(se) > 0:
        so = "\033[31m " + str(se) + "\033[0m"

    return so


def remote_cmd_map(servercmd):
    """
    @type servercmd: tuple
    @return: str
    """
    server, cmd = servercmd
    res = remote_cmd(server, cmd)
    return server, res


def put_scp(server, fp1, fp2, username=None):
    """
    @type server: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type username: CryptoUser, None
    @return: None
    """
    return scp(server, "put", fp1, fp2, username)


def get_scp(server, fp1, fp2, username=None):
    """
    @type server: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type username: CryptoUser, None
    @return: None
    """
    return scp(server, "get", fp1, fp2, username)


def scp(server, username, cmdtype, fp1, fp2, rsa_private_key=None):
    """
    @type server: str, unicode
    @type username: CryptoUser
    @type cmdtype: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type rsa_private_key: str, unicode, None
    @return: None
    """

    # put back known_hosts file
    run_cmd("ssh -t " + username + "@" + server + " date")
    transport = None
    try:
        hostname = server
        port = 22
        password = ''

        #rsa_private_key = join(os.getcwdu(), "keys/secure/vagrantsecure")
        if rsa_private_key is None:
            rsa_private_key = join(expanduser("~"), ".ssh/id_rsa")

        if rsa_private_key is None:
            raise AssertionError("rsa_private_key: is None")

        if not os.path.exists(rsa_private_key):
            raise AssertionError("rsa_private_key: does not exist")

        transport = paramiko.Transport((hostname, port))
        transport.start_client()
        ki = paramiko.RSAKey.from_private_key_file(rsa_private_key)
        agent = paramiko.Agent()
        agent_keys = agent.get_keys() + (ki,)

        if len(agent_keys) == 0:
            raise AssertionError("scp: no keys", server)

        authenticated = False

        for key in agent_keys:
            try:
                transport.auth_publickey(username, key)
                authenticated = True
                break
            except paramiko.SSHException:
                pass

        if not authenticated:
            raise AssertionError("scp: not authenticated", server)

        try:
            host_keys = paramiko.util.load_host_keys(expanduser('~/.ssh/known_hosts'))
        except IOError:
            try:
                host_keys = paramiko.util.load_host_keys(expanduser('~/ssh/known_hosts'))
            except IOError:
                print('*** ')
                print("\033[31msftp: unable to open host keys file\033[0m")
                host_keys = {}

        if hostname in host_keys:
            hostkeytype = list(host_keys[hostname].keys())[0]
            hostkey = host_keys[hostname][hostkeytype]

            if not transport.is_authenticated():
                transport.connect(username=username, password=password, hostkey=hostkey)
            else:
                transport.open_session()

            sftp = paramiko.SFTPClient.from_transport(transport)

            if cmdtype == "put":
                sftp.put(fp1, fp2)
            else:
                sftp.get(fp1, fp2)

            return True
    finally:
        if transport is not None:
            transport.close()


def run_cmd(cmd, pr=False, shell=False, streamoutput=True, returnoutput=False):
    """
    @type cmd: str, unicode
    @type pr: bool
    @type shell: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @return: None
    """
    if pr:
        console("run_cmd:", cmd, color="blue")
    console("run_cmd:", cmd, color="blue")

    if shell is True:
        return subprocess.call(cmd, shell=True)
    else:
        cmdl = [x for x in cmd.split(" ") if len(x.strip()) > 0]
        p = subprocess.Popen(cmdl, cwd=os.getcwd(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        if streamoutput and not returnoutput:
            while p.poll() is None:
                output = p.stdout.readline()

                if len(output.strip()) > 0:
                    sys.stdout.write("\033[30m" + output.decode("utf-8") + "\033[0m")
                    sys.stdout.flush()

        out, err = p.communicate()
        if p.returncode != 0:
            console(out, color="red")
            console(err, color="red")
        else:
            if not returnoutput:
                if len(out) > 0:
                    console(out, color="grey")

    if not returnoutput:
        return p.returncode
    else:
        return out, err
