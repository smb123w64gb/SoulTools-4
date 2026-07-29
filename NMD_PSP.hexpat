struct bones{

float start[4];
float end[4];
float rot[3];
u32 stroff;
float scale[3];
u8 type;
u8 bind;
u8 inx;
u8 unk1;
};

struct nmd{
char magic[4];
u8 unk1;
u8 ver;
u8 unk2;
u8 unk3;
u16 unk4;
u16 boneCount;
u32 unk5;
u32 unk6;
u32 off1;
u32 off2;
u32 nameOff;
u32 signoff;
};

nmd test @ 0;
bones tes2[test.boneCount] @ 0x40;