import struct

def u32be(file):
    return struct.unpack(">I", file.read(4))[0]

def w32be(file,val):
    file.write(struct.pack(">I", val))

class SPD(object):
    def __init__(self):
        self.dataOff = 0x80
        self.data = []
    def read(self,f):
        count = u32be(f)
        self.dataOff = u32be(f)
        curOff = self.dataOff
        for x in range(count):
            eof = u32be(f)
            size = eof - curOff
            cur = f.tell()
            f.seek(curOff)
            self.data.append(f.read(size))
            f.seek(cur)
            curOff += size
    def write(self,f):
        w32be(f,len(self.data))
        w32be(f,self.dataOff)
        
        curOff = self.dataOff
        for x in self.data:
            w32be(f,len(x)+curOff)
            curOff+=len(x)
        f.seek(self.dataOff)
        for x in self.data:
            f.write(x)