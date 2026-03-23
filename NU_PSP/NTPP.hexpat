struct HDR{
char MAGIC[4];
u16 ver;
u16 count;
padding[8];
};
struct entry{
u32 totalSize;
u32 palletSize;
u32 dataSize;
u16 headerSize;
u16 unk1;
u8 unk2;
u8 mipcount;
u8 unk3;
u8 pixelFormat;
u16 Width;
u16 Height;
u32 unk4;
u32 unk5;

u32 unk6;
u32 unk7;
u32 unk8;
u32 unk9;

padding[headerSize-0x50];

u32 eXT[4];
char GIDX[4];
u32 unk10;//Always 0x10
u32 hashID;
padding[4];
u8 data[dataSize];
u8 dataEX[palletSize];

};
struct NTPP{
HDR header;
entry ent[header.count];
};

NTPP Texture @ 0;