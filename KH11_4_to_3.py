import struct,sys

def u32be(file):
    return struct.unpack(">I", file.read(4))[0]
def u32le(file):
    return struct.unpack("<I", file.read(4))[0]
def u16be(file):
    return struct.unpack(">H", file.read(2))[0]
def u16le(file):
    return struct.unpack("<H", file.read(2))[0]

def w32(file,val):
    file.write(struct.pack("<I", val))
def w16(file,val):
    file.write(struct.pack("<H", val))

def s64(fin,fout):
    fout.write(struct.pack(">Q", struct.unpack("<Q", fin.read(8))[0]))
def s32(fin,fout):
    fout.write(struct.pack(">I", struct.unpack("<I", fin.read(4))[0]))
def s16(fin,fout):
    fout.write(struct.pack(">H", struct.unpack("<H", fin.read(2))[0]))

if(len(sys.argv)<3):
    sys.exit("Not enough args\nKH11_Endianizer.py <Input.kh11> <Output.kh11>")

inf = open(sys.argv[1],'rb')
ouf = open(sys.argv[2],'wb')
inf.seek(0)

if(u32le(inf) == 825313355):
    u32 = u32le
    u16 = u16le
else:
    u32 = u32be
    u16 = u16be

inf.seek(0x0C)#Entry count
entryCount = u16(inf)

inf.seek(0x10)#Attack + Grab address
attackList = u32(inf)
grabDMG = u32(inf)
inf.seek(0x60)#to get the first cmd address for grabdmg count
oldCmdBase = u32(inf)

entrySize = entryCount*0x40
attackCount = int((grabDMG-attackList)/0x58)
attackSize = attackCount*0x58
grabCount = int((oldCmdBase-grabDMG)/2)


newAttackOff = entrySize + 0x28
newThrowOff = newAttackOff + attackSize
newCmdBase = newThrowOff+(grabCount*2)


inf.seek(0)
#Magic
s32(inf,ouf)
#Date n time (the year is u16)
ouf.write(inf.read(2))
s16(inf,ouf)
ouf.write(inf.read(4))
#Entry Count
s16(inf,ouf)
#Doesnt change huh
ouf.write(inf.read(2))

#s32(inf,ouf)#attack list
w32(ouf,newAttackOff)
#s32(inf,ouf)#throw dmgs
w32(ouf,newThrowOff)
inf.seek(8,1)

for x in range(8):#The 4 Movepools (Index,Count)
    s16(inf,ouf)

for x in range(entryCount):
    s16(inf,ouf)#Motion 1
    s16(inf,ouf)#Motion 2

    s32(inf,ouf)#8 unk

    s32(inf,ouf)#0xC motion Muti
    s32(inf,ouf)#0x10 speed Muti

    s16(inf,ouf)#0x12
    s16(inf,ouf)#0x14
    ouf.write(inf.read(4)) #0x18 always 0xC00 BE
    s32(inf,ouf)#0x1C unk
    s32(inf,ouf)#0x20 FLOAT

    s32(inf,ouf)
    s32(inf,ouf)
    s32(inf,ouf)
    s32(inf,ouf)#all unks

    s32(inf,ouf)#0x30 unk multi
    s16(inf,ouf)#framecount
    s16(inf,ouf)#0x34

    #s32(inf,ouf)#CMD addr 0x38
    newAddr = ((u32(inf)-oldCmdBase)+newCmdBase)
    w32(ouf,newAddr)

    s32(inf,ouf)#attack1 0x3C
    inf.seek(8,1)
    #s32(inf,ouf)#attack2 0x40
    #s32(inf,ouf)#unk 0x44

for x in range(attackCount):#I guess the reversed them????
    start = inf.tell()
    s64(inf,ouf)
    for y in range(34):
        s16(inf,ouf)
    ret = inf.tell()
    inf.seek(10,1)
    s16(inf,ouf)
    s16(inf,ouf)
    ouf.write(inf.read(4))
    s16(inf,ouf)
    w16(ouf,0)
inf.seek(grabDMG)
for x in range(grabCount):
    s16(inf,ouf)
ouf.write(inf.read())
ouf.close()
inf.close()