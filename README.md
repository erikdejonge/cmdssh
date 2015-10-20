# cmdssh
Execute commands on local machine and on remote machine via ssh, and a wrapper for paramikos scp.


#local command execution

## shell command
Wrapper around subprocess.call with shell=True

``` python
shell(cmd)
```


## run command
Runs a blocking unix command and returns the result

``` python

cmd_run(cmd, pr=False, streamoutput=True, returnoutput=True, cwd=None, prefix=None)

# example
cmd_run('date "+%Y-%m-%d% %H:%M"', pr=False, streamoutput=False, returnoutput=True)

```

###Extended version:

``` python
call_command
```

###Variant
Common usecase scenario, run a command and get the result, possibly print to the console using an optional filter.

``` python
cmd_exec(cmd, cmdtoprint=None, display=True, myfilter=None)
```

- `cmdtoprint`: unix command
- `display`: print to console
- `myfilter`: function used to print 

    ####example filter: 
```python
def onlyerrors(data):
    if "ERROR" in data:
        return data
```

##Parameters:

- `command`: unix command
- `cmdfolder`=os.getcwd() -> working folder command
- `verbose`=False -> prints the command
- `streamoutput`=True -> prints output to stdout (keeps buffering)
- `returnoutput`=False -> return the buffered output
- `prefix`=None -> string to place before streaming output
- `ret_and_code`=False -> return exit code also (code, val)


# SSH: run command on remote machine

Uses ssh and key authentication to logon to a remote ssh server and execute a command there.

``` python
def remote_cmd(server, cmd, username=None, timeout=60, keypath=None):

#example
remote_cmd("localhost", "rm -Rf ~/Desktop/foobar")
```

##Parameters:

- `server`: ip or domain name of server
- `cmd`: unix command to execute
- `username`: username used to login
- `timeout`: try time to connect to server
- `keypath`: path to the public key of username

## tuplebased interface
``` python
remote_cmd_map(servercmd)
```

- `servercmd`: tuple with (  server, cmd, username, keypath )

# SSH: Secure Copy Protocol

``` python
scp_get(server, fp1, fp2, username=None, keypath=None)
scp_put(server, fp1, fp2, username=None, keypath=None)
```

##Parameters:

- `server`: ip or domain name of server
- `fp1`: source filepath
- `fp2`: target filepath
- `username`: username used to login
- `keypath`: path to the public key of username

# SSH: Shell

Invoke a shell on a machine

```python
invoke_shell(server, username, keypath)
```


##Parameters:

- `server`: ip or domain name of server
- `username`: username used to login
- `keypath`: path to the public key of username


# Download file
Wrapper around the requests library. Downloads a file with a progress bar.

```python
download(url, mypath):
```
## parameters

- `url`: url to download
- `mypath`: filepath where to create the downloaded file


