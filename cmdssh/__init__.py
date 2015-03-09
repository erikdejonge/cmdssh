# coding=utf-8
"""
pip
-
Active8 (09-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""

import os
import subprocess
import getpass
import stat
import hashlib
from os.path import join

import paramiko
from paramiko import SSHClient
from consoleprinter import console_exception, console, console_warning
from .scp import SCPClient


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
        console_warning(se)

    so = so.decode("utf-8")
    return so


def remote_cmd_map(servercmd):
    """
    @type servercmd: tuple
    @return: str
    """
    server, cmd = servercmd
    res = remote_cmd(server, cmd)
    return server, res


def run_scp(server, username, cmdtype, fp1, fp2):
    """
    @type server: str, unicode
    @type username: CryptoUser
    @type cmdtype: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @return: None
    """
    run_cmd("ssh -t " + username + "@" + server + " date")
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(server)

    # SCPCLient takes a paramiko transport as its only argument
    scpc = SCPClient(ssh.get_transport())

    if cmdtype == "put":
        scpc.put(fp1, fp2)
    else:
        scpc.get(fp1, fp2)

    return True


def put_scp(server, fp1, fp2, username=None):
    """
    @type server: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type username: CryptoUser, None
    @return: None
    """
    return run_scp(server, username, "put", fp1, fp2)


def get_scp(server, fp1, fp2, username=None):
    """
    @type server: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type username: CryptoUser, None
    @return: None
    """
    return run_scp(server, username, "get", fp1, fp2)


def call_command(command, cmdfolder, verbose=False, streamoutput=True, returnoutput=False):
    """
    @type command: str, unicode
    @type cmdfolder: str, unicode
    @type verbose: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @return: None
    """
    try:
        if verbose:
            console(cmdfolder, command, color="yellow")

        commandfile = hashlib.md5(str(command).encode()).hexdigest() + ".sh"
        commandfilepath = join(cmdfolder, commandfile)
        open(commandfilepath, "w").write(command)

        if not os.path.exists(commandfilepath):
            raise ValueError("commandfile could not be made")

        os.chmod(commandfilepath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        proc = subprocess.Popen(commandfilepath, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cmdfolder, shell=True)
        retval = ""

        if streamoutput is True:
            while proc.poll() is None:
                output = proc.stdout.readline()
                output = output.decode("utf-8")
                if returnoutput is True:
                    retval += str(output)

                if len(output.strip()) > 0:
                    console(output, color="green"),
        else:
            so, se = proc.communicate()
            if proc.returncode != 0 or verbose:
                print("command:")
                print(so)
                print(se)

            if returnoutput is True:
                retval = so
                retval += se
                retval = retval.decode()

        if os.path.exists(commandfilepath):
            os.remove(commandfilepath)

        if returnoutput is True:
            return retval.strip()
        else:
            return proc.returncode
    except OSError as e:
        console_exception(e)
    except ValueError as e:
        console_exception(e)
    except subprocess.CalledProcessError as e:
        console_exception(e)


def run_cmd(cmd, pr=False, streamoutput=True, returnoutput=True):
    """
    @type cmd: str, unicode
    @type pr: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @return: None
    """
    if pr:
        console("run_cmd:", cmd, color="blue")

    rv = call_command(cmd, os.getcwd(), pr, streamoutput, returnoutput)
    return str(rv)
