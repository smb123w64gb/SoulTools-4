import struct

def u32be(file):
    return struct.unpack(">I", file.read(4))[0]

def w32be(file,val):
    file.write(struct.pack(">I", val))

class PKG(object):
    def __init__(self):
        self.dataOff = 0x80
        self.data = []
    def read(self,f):
        count = u32be(f)
        baseOffssets = []
        for x in range(count):
            off = u32be(f)
            baseOffssets.append(off)
        f.seek(0,2)
        baseOffssets.append(f.tell())
        for x in range(count):
            size = baseOffssets[x+1]-baseOffssets[x]
            f.seek(baseOffssets[x])
            self.data.append(f.read(size))
    def write(self,f):
        w32be(f,len(self.data))
        truesize = 4+(len(self.data)*4)
        if(truesize%0x80):
            truesize += (0x80 - ((truesize)%0x80))
        curOff = truesize
        self.dataOff = truesize
        for x in self.data:
            w32be(f,curOff)
            curOff += len(x)
            if((curOff)%0x80):
                curOff += (0x80 - (curOff%0x80))
        w32be(f,curOff)
                
        f.seek(self.dataOff)
        for x in self.data:
            if(f.tell()%0x80):
                f.write(b'\0'*(0x80-(f.tell()%0x80)))
            f.write(x)
            