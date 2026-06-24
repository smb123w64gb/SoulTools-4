//This is for the 360 nsh but can be adapted to 

struct string{
char value[];
};
enum RegisterSet : u16 // D3DXREGISTER_SET
{
    Bool,
    Int4,
    Float4,
    Sampler
};
u32 currentbase = 0;
struct ConstantInfo // D3DXSHADER_CONSTANTINFO
{
    u32 name;
    string name_str @ currentbase+name;
    RegisterSet registerSet;
    u16 registerIndex;
    u16 registerCount;
    u16 reserved;
    u32 typeInfo;
    u32 defaultValue;
};
struct ConstantTable // D3DXSHADER_CONSTANTTABLE
{
    currentbase = $;
    u32 size;
    u32 creator;
    string creator_str @ currentbase+creator;
    u32 version;
    u32 constants;
    u32 constantInfo;
    u32 flags;
    u32 target;
    ConstantInfo CosntInfo[constants];
};
struct ConstantTableContainer
{
    u32 size;
    ConstantTable constantTable;
};
struct X3ShaderContainor{
    
    u32 flags;
    u32 virtualSize;
    u32 physicalSize;
    u32 fieldC;
    u32 constantTableOffset;
    u32 definitionTableOffset;
    u32 shaderOffset;
    u32 field1C;
    u32 field20;
};


struct intTwin{
u32 one;
u32 two;
};
struct NSH{
u32 MAGIC;
u32 file_size;
u16 unk1;
u16 programCount;
u32 unk2[5];
u32 materialShaderID;
u32 unk3[5];
u32 unk4;
u32 unk5[17];
intTwin unk6[16];
X3ShaderContainor test;
ConstantTableContainer test2;
};

be NSH test @ 0;