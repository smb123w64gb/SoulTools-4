import struct,sys,os

from reversebox.image.image_decoder import ImageDecoder
from reversebox.image.image_formats import ImageFormats
from reversebox.image.pillow_wrapper import PillowWrapper
from reversebox.image.swizzling.swizzle_psp import swizzle_psp, unswizzle_psp
from reversebox.image.image_padding import psp_image_padding

from PIL import Image

def u8(file):
    return struct.unpack("B", file.read(1))[0]
def u16(file):
    return struct.unpack("<H", file.read(2))[0]
def u32(file):
    return struct.unpack("<I", file.read(4))[0]
def rR(f,o,l):#Read n Return, Takes file,offset,size returns data
    c = f.tell()
    f.seek(o)
    d = f.read(l)
    f.seek(c)
    return d


knownFMT = [0x83,0x84,0x85]#RGBA8,P4,P8

class NTPP(object):
    class Entry(object):
        def __init__(self):
            self.pallet = bytearray()
            self.imgdat = bytearray()
            self.mipcount = 1
            self.pixelformat = 0x84 #P4 & 0x85 P8
            self.width = 0
            self.height = 0
            self.id = 0
        def read(self,f):
            head = f.tell()
            f.seek(4,1)#totalSize
            palSize = u32(f)
            datSize = u32(f)
            hdrSize = u16(f)
            f.seek(3,1)#palletCount + unk
            self.mipcount = u8(f)
            f.seek(1,1)#Unk maybe palletFormat
            self.pixelformat = u8(f)
            self.width = u16(f)
            self.height = u16(f)
            f.seek((head+hdrSize)-8)
            self.id = u32(f)
            f.seek(head+hdrSize)
            self.imgdat = f.read(datSize)
            self.pallet = f.read(palSize)
            find = False
            for x in knownFMT:
                if x == self.pixelformat: find = True
            if(not find):
                print("UNK FMT:%s"%hex(self.pixelformat))
    def __init__(self):
        self.files = []
    def read(self,f):
        f.seek(6)
        count = u16(f)
        f.seek(16)
        for x in range(count):
            tmp = self.Entry() 
            tmp.read(f)
            self.files.append(tmp)

infile = open(sys.argv[1],'rb')
NUT = NTPP()
NUT.read(infile)
for x in NUT.files:
    bpp = 8
    palette_format = ImageFormats.RGBA8888
    img_width = x.width
    img_height = x.height
    palette_data = x.pallet
    match x.pixelformat:
        case 0x83:
            bpp = 32
            image_format = ImageFormats.RGBA8888
        case 0x84:
            bpp = 4
            image_format = ImageFormats.PAL4
        case 0x85:
            bpp = 8
            image_format = ImageFormats.PAL8
    unswizzled_file_data  = unswizzle_psp(x.imgdat, img_width, img_height, bpp)
    #unswizzled_file_data = psp_image_padding(unswizzled_file_data, img_width, img_height, bpp)
    image_decoder = ImageDecoder()
    wrapper = PillowWrapper()
    if(not x.pixelformat == 0x83):
        decoded_image_data: bytes = image_decoder.decode_indexed_image(
            unswizzled_file_data, palette_data, img_width, img_height, image_format, palette_format
        )
    else:
        decoded_image_data: bytes = image_decoder.decode_image(
            unswizzled_file_data, img_width, img_height, image_format
        )

    pil_image = wrapper.get_pillow_image_from_rgba8888_data(decoded_image_data, img_width, img_height)
    pil_image.save(str("%s_%s.png"%(sys.argv[1],x.id)))
                
        

