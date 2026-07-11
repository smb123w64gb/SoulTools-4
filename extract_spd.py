import sys,spd,os

filein = open(sys.argv[1],'rb')

pack = spd.SPD()
pack.read(filein)
filein.close()

OutDir = sys.argv[1].split('.')[0]
os.makedirs(OutDir + '\\', exist_ok=True)
for idx,x in enumerate(pack.data):
    
    if(len(x)):
        
        fileout = open(OutDir + '\\'+ str("%04i.bin"%idx),'wb')
        fileout.write(x)
        fileout.close()