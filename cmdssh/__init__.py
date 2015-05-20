#!/usr/bin/env python3
# coding=utf-8
"""
pip
-

active8 (09-03-15)
author: erik@a8.nl
license: gnu-gpl2
"""

import os
import sys
import tty
import stat
import time
import fcntl
import select
import socket
import struct
import getpass
import hashlib
import termios
import paramiko
import requests
import subprocess

from scp import SCPClient
from paramiko import SSHClient
from paramiko.py3compat import u
from consoleprinter import bar, info, console, warning, console_error, console_exception, colorize_for_print, remove_escapecodes


class CallCommandException(SystemExit):
    """
    CallCommandException
    """
    pass


def call_command(command, cmdfolder=os.getcwd(), verbose=False, streamoutput=True, returnoutput=False, prefix=None, ret_and_code=False):
    """
    @type command: str, unicode
    @type cmdfolder: str, unicode
    @type verbose: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @type prefix: str, None
    @type ret_and_code: bool
    @return: None
    """
    try:
        if ret_and_code is True:
            streamoutput = False
            returnoutput = True

        if verbose:
            console(cmdfolder, command, color="yellow")

        for prevfile in os.listdir(cmdfolder):
            if prevfile.startswith("callcommand_"):
                os.remove(os.path.join(cmdfolder, prevfile))

        commandfile = "callcommand_" + hashlib.md5(str(command).encode()).hexdigest() + ".sh"
        commandfilepath = os.path.join(cmdfolder, commandfile)
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
                            prefix = prefix.split()[0]

                        console(output.rstrip(), color="green", prefix=prefix)

                        if returnoutput is True:
                            retval += output

            so, se = proc.communicate()
            if ret_and_code is False and (proc.returncode != 0 or verbose):
                so = so.decode().strip()
                se = se.decode().strip()
                output = str(so + se).strip()

                if proc.returncode == 1:
                    console_error(command, CallCommandException("Exit on: " + command), errorplaintxt=output, line_num_only=9)
                else:
                    console("returncode: " + str(proc.returncode), command, color="red")

            if ret_and_code is True or returnoutput is True and streamoutput is False:
                retval = so
                retval += se

                if hasattr(retval, "decode"):
                    retval = retval.decode()

            if ret_and_code is True:
                returnoutput = False

            if returnoutput is True:
                return retval.strip()
            elif ret_and_code is True:
                return proc.returncode, retval.rstrip()
            else:
                return proc.returncode
        finally:
            if os.path.exists(commandfilepath):
                #if proc.returncode == 0:
                os.remove(commandfilepath)

    except ValueError as e:
        console_exception(e)
    except subprocess.CalledProcessError as e:
        console_exception(e)


def cmd_exec(cmd, cmdtoprint=None, display=True, myfilter=None):
    """
    @type cmd: str
    @type cmdtoprint: None, str
    @type display: bool
    @type myfilter: function
    @return: None
    """
    code, rv = call_command(cmd, os.getcwd(), ret_and_code=True)

    if display is True:
        if cmdtoprint is not None:
            cmd = cmdtoprint

        if code == 0:
            if cmdtoprint is not None and not len(cmdtoprint) == 0:
                print(cmdtoprint)

            rvs = rv.split("\n")

            for rv in rvs:
                print(colorize_for_print(rv))
        else:
            if myfilter is not None:
                rv = myfilter(rv)

            warning("code", str(code))
            warning("cmd", cmd)
            warning("rv", rv)

    return code, rv


def cmd_run(cmd, pr=False, streamoutput=True, returnoutput=True, cwd=None, prefix=None):
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


def download(url, mypath):
    """
    @type url: str
    @type mypath: str
    @return: None
    """
    cnt = 0
    total_length = None
    r = None

    try:
        while cnt < 10:
            info("download", url)
            r = requests.get(url, stream=True, timeout=60)
            total_length = r.headers.get('content-length')

            if total_length is not None:
                total_length = int(total_length)
                break
            else:
                cnt += 1

            if cnt > 1:
                if cnt > 8:
                    console("download", url, "attempt", cnt)

                time.sleep(0.5)

    except BaseException as be:
        console(be, color="red")

    if total_length is None:
        console("Could not download, total_length is None", url, mypath, printstack=True, color="red")

    if total_length > 0 and r is not None:
        with open(mypath, 'wb') as f:
            total_length = int(total_length)

            for chunk in bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()


def get_terminal_size():
    """
    get_terminal_size
    """
    env = os.environ

    def ioctl_gwinsz(fd2):
        """
        @type fd2: int
        @return: None
        """
        # noinspection PyBroadException
        try:
            cr2 = struct.unpack('hh', fcntl.ioctl(fd2, termios.TIOCGWINSZ, '1234'))
        except:
            return

        return cr2

    cr = ioctl_gwinsz(0) or ioctl_gwinsz(1) or ioctl_gwinsz(2)

    if not cr:
        # noinspection PyBroadException
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_gwinsz(fd)
            os.close(fd)
        except:
            pass

    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        # # #  Use get(key[, default]) instead of a try/catch
        # try:
        #    cr = (env['LINES'], env['COLUMNS'])
        # except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])


def interactive_shell(chan):
    """
    @type chan: paramiko.Channel
    @return: None
    """
    posix_shell(chan)


def invoke_shell(server, username, keypath):
    """
    @type server: str
    @type username: str
    @type keypath: list, str
    @return: None
    """
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, key_filename=keypath)
    tw, th = get_terminal_size()
    chann = ssh.invoke_shell(term="xterm-256color", width=tw, height=th)
    interactive_shell(chann)
    exitstatus = chann.recv_exit_status()
    if exitstatus != 0:
        warning("invoke_shell " + username + "@" + server, "return " + str(exitstatus))

    return exitstatus


def posix_shell(chan):
    """
    @type chan: paramiko.Channel
    @return: None
    """
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())

        chan.settimeout(0.0)

        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])

            if chan in r:
                try:
                    x = u(chan.recv(1024))

                    if len(x) == 0:
                        break

                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass

            if sys.stdin in r:
                x = sys.stdin.read(1)

                if len(x) == 0:
                    break

                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


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
        ssh.connect(server, username=username, timeout=timeout, key_filename=keypath)

        # info("remote_cmd", cmd)
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


def remote_cmd_map(servercmd):
    """
    @type servercmd: tuple
    @return: str
    """
    server, cmd, username, keypath = servercmd

    # noinspection PyArgumentEqualDefault
    res = remote_cmd(server, cmd, username, 60, keypath)
    return server, res


def scp_get(server, fp1, fp2, username=None, keypath=None):
    """
    @type server: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type username: CryptoUser, None
    @type keypath: str, None
    @return: None
    """
    return scp_run(server, username, "get", fp1, fp2, keypath)


def scp_put(server, fp1, fp2, username=None, keypath=None):
    """
    @type server: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @type username: CryptoUser, None
    @type keypath: str, None
    @return: None
    """
    return scp_run(server, username, "put", fp1, fp2, keypath)


def scp_run(server, username, cmdtype, fp1, fp2, keypath):
    """
    @type keypath: str, None
    @type server: str, unicode
    @type username: CryptoUser
    @type cmdtype: str, unicode
    @type fp1: str, unicode
    @type fp2: str, unicode
    @return: None
    """
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, key_filename=keypath)

    # SCPCLient takes a paramiko transport as its only argument
    scpc = SCPClient(ssh.get_transport())

    if cmdtype == "put":
        scpc.put(fp1, fp2)
    else:
        scpc.get(fp1, fp2)

    return True


def shell(cmd):
    """
    @type cmd: str
    @return: None
    """
    return subprocess.call(cmd, shell=True)

