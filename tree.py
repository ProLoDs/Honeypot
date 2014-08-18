#! /usr/bin/env python
import getopt
import gzip
import pickle
import pwd
import time
import urllib
from colors import bcolors,print_good,print_debug,print_fail,print_warning
import grp


class commandParser():
    def __init__(self,mysys):
        self.mysys=mysys
        self.root=mysys.parent
    def parsePath(self,path):
        split=path.split("/")
        if path.startswith("/"):
            split[0]="/"
        if path[-1] == "/":
            split.pop()
        return split 
    
    def getpwd(self,place_holder):
        #print_debug("Start pwd")
        path=[]
        tmp=""
        tmpsys=self.mysys
        while tmp != tmpsys.pwd():
            path.append(tmpsys.pwd())
            tmp=tmpsys.pwd()
            tmpsys=tmpsys.parent
            #print_debug(tmp)
        #print_debug("Print path:")
        #print_debug()
        #print_debug("Return_pwd: "+"/".join(reversed(path)).replace("//","/"))
        return "\r\n"+"/".join(reversed(path)).replace("//","/")
    def tmp_travel(self,filesystem,path_raw):
        tmp_sys=filesystem
        path = self.parsePath(path_raw)
        if path[0] == "/":
            #print_debug("///////")
            for a in range(20):
                tmp_sys=tmp_sys.parent
            if len(path)==1:
                return tmp_sys
            path.pop(0)
        for p in path:
            #print_debug(path)
            tmp_sys = tmp_sys.cd(p)
        #print_debug(self.mysys.pwd())
        return tmp_sys
    def uname(self,parts):
        opts, args = getopt.getopt(parts[1:], "asnrvmpio", ["all","kernel-name","nodename","kernel-release","kernel-release",
                                                      "kernel-version","machine","processor","hardware-platform","operating-system"])
        uname_param={}
        with open("util/uname.info","r") as unameinfo:
            for line in unameinfo:
                uname_param[line.split(";")[0]]=line.split(";")[1].replace("\n","")
        if not opts:
            return "\r\nLinux"
        out="\r\n"
        for option , argument in opts:
            if option.replace("-","") in uname_param.keys():
                out+=uname_param[option.replace("-","")]
        return out
    def cat (self,parts):
        opts, args = getopt.getopt(parts[1:], "AbeEnstTuv", [])
        if not args:
            return ""
        if len(args[0])>1:
            tmp_sys=self.tmp_travel(self.mysys, args[0])
            if not tmp_sys.fileAttributes.fileRights.startswith("d"):
                return "\r\n"+ tmp_sys.fileAttributes.content.replace("\n","\r\n")
            else:
                return "\r\ncat: "+args[0] + "Is a directory"
        else:
            try:
                tmp_sys =  self.root.cd(args[0])
                if not tmp_sys.fileAttributes.fileRights.startswith("d"):
                    return "\r\n"+ tmp_sys.fileAttributes.content.replace("\n","\r\n")
                else:
                    return "\r\ncat: "+args[0] + "Is a directory"
            except:
                return "\r\ncat: "+args[0]+" :No such File or Direcotry!"
        
        return "\r\ncat: "+args[0] + ": Is a directory"
        
    def cd(self,parts):
        opts, args = getopt.getopt(parts[1:], ":LP", [])
        try:
            if not args:
                #print_debug("cd without argument")
                self.mysys=self.root.cd("root")
                return " "
            path = self.parsePath(args[0])
            if path[0] == "/":
                #print_debug("///////")
                self.mysys=self.root
                if len(path)==1:
                    return " "
                path.pop(0)
            for p in path:
                #print_debug(path)
                self.mysys = self.mysys.cd(p)
            #print_debug(self.mysys.pwd())
            return " "
        except:
            return "\r\ncd: "+args[0]+": File or Directory not found!"
   
    def ls(self,parts):
        opts, args = getopt.getopt(parts[1:], "aAbBcCdDfFgGhHiIklLmnNopqQrRsStTuUvwxX1Z:", 
            ['all','almost-all','author',
            'escape','block-size=','ignore-backups',
            'color','directory','dired',
            'classify','file-type','format=',
            'full-time','no-group','human-readable',
            'si','dereference-command-line-symlink-to-dir','hide=',
            'idicator-style=','inode','ignore=',
            'dereference','numeric-uid-gid','literal',
            'indicator-style=','hide-control-chars','show-control-chars',
            'quote-name','quoting-style=','reverse',
            'recursive','size','sort=',
            'time=','time-style=','tabsize=',
            'width=','lcontect','context',
            'scontext','help','version'])
        out=""
        #print_debug(opts)
        l_option=False
        a_option=False
        if not args:
            #print_debug("not args")
            files = sorted(self.mysys.leafs.keys())
        else:
            #print_debug("args")
            files = sorted(self.tmp_travel(self.mysys, args[0]).leafs.keys())
        for option , argument in opts:
            #print_debug(option)
            if option=="-l":
                l_option=True
            if option == "-a":
                a_option = True
        if not a_option:
            files.remove("..")
            files.remove(".")
        if l_option:
            #print_debug("l option")
            #print [self.mysys.leafs[x].fileAttributes.ll() for x in files if x != None]
            return "\r\n"+"".join([self.mysys.leafs[x].fileAttributes.ll()+x+"\r\n" for x in files if x != None])
        else:
            return self.ls_print(files)
    def ls_print(self,files):
        

        for count in range(len(files)):
            if len(files[count])<8:
                files[count]+= "\t\t\t\t"
            elif len(files[count])<16:
                files[count]+= "\t\t\t" 
            elif len(files[count])<24:
                files[count]+= "\t\t" 
            elif len(files[count])>=24:
                files[count]+= "\t" 
        for a in range(len(files)):
            if (a+1)%3==0:
                #print_debug("new Line")
                files[a]=files[a].replace("\t","")+"\r\n"
        #print_debug(repr("".join(files)))    
        return "\r\n"+"".join(files)
     
    def wget(self,parts):
        opts, args = getopt.getopt(parts[1:], "aAbBcCdDfFgGhHiIklLmnNopqQrRsStTuUvwxX1Z:", 
            ['all','almost-all','author',
            'escape','block-size=','ignore-backups',
            'color','directory','dired',
            'classify','file-type','format=',
            'full-time','no-group','human-readable',
            'si','dereference-command-line-symlink-to-dir','hide=',
            'idicator-style=','inode','ignore=',
            'dereference','numeric-uid-gid','literal',
            'indicator-style=','hide-control-chars','show-control-chars',
            'quote-name','quoting-style=','reverse',
            'recursive','size','sort=',
            'time=','time-style=','tabsize=',
            'width=','lcontect','context',
            'scontext','help','version'])
        for arg in args:
            if not arg.startswith("http://"):
                arg = "http://"+arg
            filehandle = urllib.urlopen(arg)
            #print filehandle.read()
            with open("bin/"+filehandle.geturl().replace("/","."),"w") as out:
                out.write(str(filehandle.read()))
        return " "
        
    def parseCommand(self,raw):
        try:
            parts=raw.split()
            if len(parts) == 0:
                return ' '
            #print repr(parts) , parts[0]
            command_map={
                         "cd":self.cd,
                         "ls":self.ls,
                         "pwd":self.getpwd,
                         "wget":self.wget,
                         "uname":self.uname,
                         "cat":self.cat
                         }
            if parts[0] in command_map:
                return command_map[parts[0]](parts)
            else:
                return '\r\nUnkown Command'
        except Exception as e:
            print_fail(str(e))
            return '\r\nUnkown Command'
    
class filenode(object):
    def __init__(self):
        self.parent=None
        self.leafs={} #'..':self.parent, '.' : self
        self.fileAttributes=None
        self.name=None
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

    def pwd (self):
        return self.name
    def cd (self,leaf):
        if leaf not in self.leafs:
            raise Exception(bcolors.FAIL + "Path not found!" + bcolors.ENDC)
        return self.leafs[leaf]


class loadSaveFilesystem():
    def save(self,object, filename, bin = 1):
        """Saves a compressed object to disk
        """
        fileout = gzip.GzipFile(filename, 'wb')
        fileout.write(pickle.dumps(object, bin))
        fileout.close()


    def load(self,filename):
        """Loads a compressed object from disk
        """
        out = gzip.GzipFile(filename, 'rb')
        buffer = ""
        while 1:
            data = out.read()
            if data == "":
                break
            buffer += data
        object = pickle.loads(buffer)
        out.close()
        return object
class fileAttributes():
    def __init__(self,raw_object,filename,content):
        self.filename = filename
        self.fileRights=self.parse_rights(oct(raw_object.st_mode))
        self.nlink = raw_object.st_nlink
        self.user = pwd.getpwuid(raw_object.st_uid)[0]
        self.group = grp.getgrgid(raw_object.st_gid)[0]
        self.size =  str(raw_object.st_size)
        self.time = time.strftime("%d. %b %H:%M",  time.gmtime(raw_object.st_mtime))
        self.content= content
    def parse_rights(self,raw):
        charrights=''
        charrights += self.number_to_filetype(raw[1])
        for a in range(3,6):
            charrights += self.number_to_char(raw[a])
        charrights+= '.'
        return charrights
    
    def number_to_char(self,number):
        options= { 0: '---',
                1: '--x',
                2:'-w-',
                3:'-wx',
                4:'r--',
                5:'r-x',
                6:'rw-',
                7:'rwx'
        }
        return options[int(number)]

    def number_to_filetype(self,number):
        options = { 0: '-',
                1:'-',
                2:'c',
                3:'-',
                4:'d',
                5:'-',
                6:'-',
                7:'-'
        }
        return options[int(number)]

    def ll(self):
        return self.fileRights + ' ' + str(self.nlink) + '\t' + self.user + '\t' + self.group + '\t' + str(self.size) + '\t' + self.time + '\t' 

    