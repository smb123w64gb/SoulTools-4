import sys,spd

filein = open(sys.argv[1],'rb')

pack = spd.SPD()
pack.read(filein)
filein.close()

OutDir = sys.argv[2]
for idx,x in enumerate(pack.data):
    fileout = open(OutDir + str("%02i"%idx),'wb')
    fileout.write(x)
    fileout.close()