#!/usr/bin/env python

from twisted.cred import portal, checkers
from twisted.conch import error, avatar
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.internet import reactor, protocol, defer
from twisted.python import log
from twisted.python.logfile import DailyLogFile
from zope.interface import implements

import subprocess
import thread
import sys
import tree
import time
import CustomMemoryPasswordDB
import os
from colors import print_debug,print_good
log.startLogging(DailyLogFile.fromFullPath("logs/honeypot.log"))
passwords=[]
usernames=[]

def nmap_scan(target,log):
    print target
    process = subprocess.Popen(["nmap","-Pn", "-A" ,target],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    with open(log,"w") as nmapout:
        nmapout.write(stdout)
        
def LoadPassDB():
    with open("util/passwords","r") as pws:
        for line in pws:
            passwords.append(line[:-1])
    with open("util/usernames","r") as users:
        for line in users:
            usernames.append(line[:-1])
    print_good( "Loaded "+str(len(usernames))+" Users")
    print_good( "Loaded "+str(len(passwords))+ " Passwords")
class ExampleAvatar(avatar.ConchUser):

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session':session.SSHSession})

class ExampleRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        print avatarId,mind
        return interfaces[0], ExampleAvatar(avatarId), lambda: None

class FakeSSH(protocol.Protocol):
    """this is our example protocol that we will run over SSH
    """
    def __init__(self):
        self.message=''
        self.curdir=mysys.pwd()
        self.parser = tree.commandParser(mysys)
        self.charCounter = 0
        self.attacker=""
        self.curlog=""
        
    def log(self,data):
        with open(self.curlog,"a") as logfile:
            logfile.write(data)
        
    def connectionMade(self):
        self.transport.write("[root@host] "+self.curdir+" # ")
        
        self.attacker=str(self.transport.getPeer().address.host)
        self.curlog="logs/"+self.attacker+"/"+time.strftime("%Y-%m-%d %H:%M:%S")
        if not os.path.exists("logs/"+self.attacker):
            os.makedirs("logs/"+self.attacker)
        thread.start_new_thread( nmap_scan, (self.attacker, "logs/"+self.attacker+"/nmap.result" ) )
    def dataReceived(self, data):
        data =  self.prepareData(data)
        self.message+=data
        if data == '\r':
            self.charCounter = 0
            self.message = self.prepareMessage(self.message)
            print_debug(repr(self.message))
            if(self.message.replace("\r", "") == "exit"):
                self.transport.write("\r\n")
                self.transport.loseConnection()
            output= self.parser.parseCommand(self.message)
            self.log(time.strftime("%Y-%m-%d %H:%M:%S :")+self.message)
            self.log(output+"\n")
            self.transport.write(output)
            self.curdir=self.parser.getpwd("")
            #print repr(self.curdir)
            self.transport.write("\r\n[root@host] "+self.curdir.replace("\r\n","")+" # ")
            self.message=''
            data = ''
        elif data == '\x03': #^C
            self.transport.loseConnection()
            return
        self.transport.write(data)
        
    def prepareData(self,data):
        data = data.replace("\x1b[D","").replace("\x1b[A","").replace("\x1b[B","").replace("\x1b[C","") # Loeshen von Pfeiltasten
        if data != '\x7f':
            self.charCounter+=1
        else:    
            if self.charCounter < 0:
                self.charCounter = 0 
            if self.charCounter > 0 :
                data = data.replace("\x7f","\b \b")
                self.charCounter-=1
            else:
                data = data.replace("\x7f"," \b \b")
        return data
        
    def prepareMessage(self,s):
        s=self.backspace(s)
        return s
        
    def backspace(self,s):
        while(s.find('\x08 \x08')!= -1):
            pos = s.find('\x08 \x08')
            s=list(s)
            del s[pos -1 : pos + 3]
            s = ''.join(s)
        return s

with open("util/id_rsa.pub","r") as pubkey:
    publicKey=pubkey.read()
with open("util/id_rsa","r") as privkey:
    privateKey=privkey.read()
    

class ExampleSession:
    
    def __init__(self, avatar):
        
        """
        We don't use it, but the adapter is passed the avatar as its first
        argument.
        """
    def windowChanged(self,size):
        self.windowSize = size
        #print 'Windowsize changed',size
        pass
    def getPty(self, term, windowSize, attrs):
        pass
    
    def execCommand(self, proto, cmd):
        raise Exception("no executing commands")

    def openShell(self, trans):
        ep = FakeSSH()
        ep.makeConnection(trans)
        trans.makeConnection(session.wrapProtocol(ep))

    def eofReceived(self):
        pass

    def closed(self):
        pass

from twisted.python import components
components.registerAdapter(ExampleSession, ExampleAvatar, session.ISession)

class ExampleFactory(factory.SSHFactory):
    publicKeys = {
        'ssh-rsa': keys.Key.fromString(data=publicKey)
    }
    privateKeys = {
        'ssh-rsa': keys.Key.fromString(data=privateKey)
    }
    services = {
        'ssh-userauth': userauth.SSHUserAuthServer,
        'ssh-connection': connection.SSHConnection
    }
    

portal = portal.Portal(ExampleRealm())
passwdDB = CustomMemoryPasswordDB.CustomMemoryPwDB()
LoadPassDB()
for user in usernames:
    for pw in passwords:
        #print user , pw
        passwdDB.addUser(user, "")
        passwdDB.addPW(pw)
print_good("Loaded "+str(len(usernames)*len(passwords))+" User/Password combinations")
portal.registerChecker(passwdDB)
ExampleFactory.portal = portal

print_good( "Loading Filesystem")
start = time.time()
mysys = tree.loadSaveFilesystem().load("util/filesystem_v3")
end = time.time() - start 
print_good( "Filesystem loaded in " + str(end) + " Seconds")
if __name__ == '__main__':
    reactor.listenTCP(8080, ExampleFactory())
    reactor.run()
    
