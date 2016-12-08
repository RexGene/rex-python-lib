import threading
import socks
import socket
import sys
import random

global defaultCount
defaultCount = 100

class ProxyNode:
    def __init__(self):
        self.sockType = None
        self.ip = ""
        self.port = 0
        self.count = 0

class ProxyManager:
    def __init__(self, filePath):
        self._proxyMap = {}
        self._lock = threading.Lock()

        with open(filePath, "r") as fp:
            for line in fp.readlines():
                data = line.split("\t")

                t = None
                typeStr = data[0]
                if typeStr == 'socks4':
                    t = socks.SOCKS4
                elif typeStr == 'socks5':
                    t = socks.SOCKS5

                if t != None:
                    node = ProxyNode()
                    node.sockType = t
                    node.ip = data[1]
                    node.port = int(data[2])
                    node.count = defaultCount
                    self._proxyMap[data[1]] = node

    def update(self):
        self._lock.acquire()
        ret = ""
        try:
            keys = self._proxyMap.keys()
            if len(keys) > 0:
                index = random.randint(0, len(keys) - 1)
                node = self._proxyMap[keys[index]]
                socks.setdefaultproxy(node.sockType, node.ip, node.port)
                socket.socket = socks.socksocket 
                ret = node.ip

        except Exception, msg:
            print msg
        finally:
            self._lock.release()

        return ret


    def fail(self, ip):
        self._lock.acquire()
        node = None
        if ip in self._proxyMap:
            node = self._proxyMap[ip] 
        try:
            if node and node.count > 0:
                node.count = node.count - 1
            else:
                if ip in self._proxyMap > 0:
                    del self._proxyMap[ip]
                else:
                    sys.stderr.write("[-] proxy not be use\n")
                    sys.exit(1)

        except Exception, msg:
            sys.stderr.write("[-] %s\n" % msg)
        finally:
            self._lock.release()


    def success(self, ip):
        self._lock.acquire()
        node = None
        if ip in self._proxyMap:
            node = self._proxyMap[ip] 
        try:
            if node and node.count < 1000:
                node.count = node.count + 10
        except Exception, msg:
            sys.stderr.write("[-] %s\n" % msg)
        finally:
            self._lock.release()



