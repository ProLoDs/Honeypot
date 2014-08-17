#! /usr/bin/env python
import os
import tree

def rec_walk(root,path='/',readFiles=False):
	last_level=1
	old_dirs=[]
	first=True
	for root_fs, dirs, files in os.walk(path,followlinks=False):
		
		level=len(root_fs.split("/"))
		#print level , root_fs,dirs
		#print "--------------------------------"
		#print "last-level:",last_level,"level:",level 
		#print "root_fs:",root_fs
		#print root,root.leafs
		#print old_dirs
		if not first:
			if level == last_level:
		#		print "same level, diffrent folder"
				root=root.leafs[".."]
				root=root.leafs[str(root_fs.split("/")[-1])]
			elif level < last_level:
		#		print "gone down ",last_level-level,"levels"
				for a in range(last_level-level+1):
		#			print "level down!"
					root=root.parent
				root=root.leafs[str(root_fs.split("/")[-1])]
			else:
		#		print "level up to",old_dirs[0]
				root=root.leafs[str(old_dirs[0])]
		first=False
		last_level=level
		old_dirs=dirs
		for dir in reversed(dirs):
			root.leafs[dir]=tree.filenode()
			root.leafs[dir].name=dir 
			root.leafs[dir].parent=root
			root.leafs[dir].leafs[".."]=root
			root.leafs[dir].leafs["."]=root.leafs[dir]
			try:
				root.leafs[dir].fileAttributes=tree.fileAttributes(os.stat(root_fs+"/"+dir),root.leafs[dir].name,None)
			except Exception as e:
				print e
				print root_fs+"/"+dir
		for file in reversed(files):
			root.leafs[file]=tree.filenode()
			root.leafs[file].name=file
			root.leafs[file].parent=root

			try:
				if not readFiles:
					root.leafs[file].fileAttributes=tree.fileAttributes(os.stat(root_fs+"/"+file),root.leafs[file].name,None)
				else:
					with open(root_fs+"/"+file,"r") as fp:
						root.leafs[file].fileAttributes=tree.fileAttributes(os.stat(root_fs+"/"+file),root.leafs[file].name,fp.read())
			except Exception as e:
				print e
				print root_fs+"/"+file
def backToRoot(root):
	for i in range(30):
		root=root.parent
	return root

root=tree.filenode()
root.parent=root
root.name='/'
root.fileAttributes=tree.fileAttributes(os.stat("/"),"/",None)

root.leafs["."]=root
root.leafs[".."]=root

#Create Skeleton
print "Creating Filesystem Skeleton"
rec_walk(root)
#Fill /etc
print "Filling /etc"
root=root.leafs["etc"]
rec_walk(root,"/etc",True)
root=root.parent
print "Filling /root"
root=root.leafs["root"]
rec_walk(root,"/root",True)
root=root.parent
print "Filling /home"
root=root.leafs["home"]
rec_walk(root,"/home",True)
root=root.parent

tree.loadSaveFilesystem().save(root, "filesystem")


#print oct(os.stat('test').st_mode)




