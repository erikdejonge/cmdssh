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
from consoleprinter import console_exception, console, remove_escapecodes, console_error
from .scp import SCPClient


def remote_cmd(server, cmd, username=None, timeout=60, keypath=None):
    """
    @type server: str
    @type cmd: str
    @type username: string, None
    @type timeout: int
    @type keypath:str,None
    @return: None
    """
    if username is None:
        username = getpass.getuser()

    ssh = paramiko.SSHClient()
    try:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = None

        if keypath is not None:
            if os.path.exists(keypath):
                pkey = paramiko.RSAKey.from_private_key_file(keypath)

        ssh.connect(server, username=username, timeout=timeout, pkey=pkey)
        si, so, se = ssh.exec_command(cmd)
        so = so.read()
        se = se.read()

        if len(se) > 0:
            se = se.decode("utf-8").strip()
            console(se.replace("\n", "\n     | "), color="red", print_stack=True, line_num_only=6)

        so = so.decode("utf-8")
        return so
    finally:
        ssh.close()



def shell(cmd):
    """
    @type cmd: str
    @return: None
    """
    return subprocess.call(cmd, shell=True)


def remote_cmd_map(servercmd):
    """
    @type servercmd: tuple
    @return: str
    """
    server, cmd, username = servercmd
    res = remote_cmd(server, cmd, username)
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
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = None

    # if os.path.exists("keys/insecure/vagrant"):
    #    pkey = paramiko.RSAKey.from_private_key_file("keys/insecure/vagrant")
    ssh.connect(server, username=username, pkey=pkey)

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


def call_command(command, cmdfolder, verbose=False, streamoutput=True, returnoutput=False, prefix=None):
    """
    @type command: str, unicode
    @type cmdfolder: str, unicode
    @type verbose: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @type prefix: str, None
    @return: None
    """
    try:
        if verbose:
            console(cmdfolder, command, color="yellow")

        for prevfile in os.listdir(cmdfolder):
            if prevfile.startswith("callcommand_"):
                os.remove(os.path.join(cmdfolder, prevfile))

        commandfile = "callcommand_" + hashlib.md5(str(command).encode()).hexdigest() + ".sh"
        commandfilepath = join(cmdfolder, commandfile)
        open(commandfilepath, "w").write(command)

        if not os.path.exists(commandfilepath):
            raise ValueError("commandfile could not be made")

        try:
            os.chmod(commandfilepath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            proc = subprocess.Popen(commandfilepath, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cmdfolder, shell=True)
            retval = ""

            if streamoutput is True:
                while proc.poll() is None:
                    output = proc.stdout.readline()

                    if isinstance(output, bytes):
                        output = output.decode()

                    if len(remove_escapecodes(output).strip()) > 0:
                        if returnoutput is True:
                            retval += str(output)

                        if prefix is None:
                            prefix = command

                        if len(prefix) > 50:
                            prefix = prefix.split(" ")[0]

                        console(output.rstrip(), color="green", prefix=prefix)

            so, se = proc.communicate()
            if proc.returncode != 0 or verbose:
                so = so.decode().strip()
                se = se.decode().strip()
                output = str(so + se).strip()
                console_error(command, SystemExit("Exit on: " + command), errorplaintxt=output, line_num_only=9)

            if returnoutput is True:
                retval = so
                retval += se
                retval = retval.decode()

            if returnoutput is True:
                return retval.strip()
            else:
                return proc.returncode
        finally:
            if os.path.exists(commandfilepath):
                os.remove(commandfilepath)

    except ValueError as e:
        console_exception(e)
    except subprocess.CalledProcessError as e:
        console_exception(e)


def run_cmd(cmd, pr=False, streamoutput=True, returnoutput=True, cwd=None, prefix=None):
    """
    @type cmd: str
    @type pr: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @type cwd: str, None
    @type prefix: str, None
    @return: None
    """
    if pr:
        console("run_cmd:", cmd, color="blue")

    if cwd is None:
        cwd = os.getcwd()

    rv = call_command(cmd, cwd, pr, streamoutput, returnoutput, prefix)
    return str(rv)
