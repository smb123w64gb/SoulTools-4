import sys,spd,os

filein = open(sys.argv[1],'rb')

pack = spd.SPD()
pack.read(filein)
filein.close()

outDir = str(sys.argv[1]+"_Extract/")
os.makedirs(outDir, exist_ok=True)
for idx,x in enumerate(pack.data):
    
    if(len(x)):
        fileout = open(outDir + str("%04i.bin"%idx),'wb')
        fileout.write(x)
        fileout.close()