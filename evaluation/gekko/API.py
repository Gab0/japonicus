#!/bin/python
import os
import requests
import json
from subprocess import Popen, PIPE


def initializeGekko():  # not used yet.
    CMD = ['node', gekkoDIR + '/gekko', '--ui']
    D = Popen(CMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)


def httpPost(URL, data={}, Verbose=True):
    try:
        Request = requests.post(URL, json=data)
        Response = json.loads(Request.text)
    except ConnectionRefusedError:
        print("Error: Gekko comm error! Check your local Gekko instance.")
        exit()
    except Exception as e:
        if Verbose:
            print("Error: config failure")
            print(e)
            print(URL)
            print(data)
        return False

    return Response


def loadHostsFile(HostsFilePath):
    remoteGekkos = []
    if os.path.isfile(HostsFilePath):
        H = open(HostsFilePath).read().split('\n')
        for W in H:
            if W and not '=' in W and not '[' in W:
                remoteGekkos.append("http://%s:3000" % W)
    return remoteGekkos
