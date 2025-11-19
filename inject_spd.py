import sys,spd

filein = open(sys.argv[1],'rb')
nudin = open(sys.argv[2],'rb')
fileout = open(sys.argv[3],'wb')

pack = spd.SPD()
pack.read(filein)
filein.close()

pack.data[3] = nudin.read()
nudin.close()

pack.write(fileout)