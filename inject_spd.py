import sys,pkg,os

files_names = []
indx = []
files = os.listdir(sys.argv[1])
for y in files:
    indx.append(int(y.split('.')[0]))
    files_names.append(sys.argv[1]+"\\"+y)
filein = open(sys.argv[2],'rb')
pack = pkg.PKG()
pack.read(filein)

for inx,x in enumerate(indx):
    newdata = open(files_names[inx],'rb')
    pack.data[x] = newdata.read()
    print(pack.data[x])
    newdata.close()

fileout = open(sys.argv[3],'wb')
pack.write(fileout)

'''
filein = open(sys.argv[1],'rb')
nudin = open(sys.argv[2],'rb')
fileout = open(sys.argv[3],'wb')


filein.close()

pack.data[3] = nudin.read()
nudin.close()

pack.write(fileout)'''