#pragma endian big

enum RegisterSet : u16 {
    Bool    = 0,
    Int4    = 1,
    Float4  = 2,
    Sampler = 3
};

enum ParameterClass : u16 {
    Scalar = 0,
    Vector,
    MatrixRows,
    MatrixColumns,
    Literal,
    Struct,
    Object
};

enum ParameterType : u16 {
    Void = 0,
    BoolType,
    IntType,
    FloatType,
    StringType,
    Texture,
    Texture1D,
    Texture2D,
    Texture3D,
    TextureCube,
    SamplerType,
    Sampler1D,
    Sampler2D,
    Sampler3D,
    SamplerCube,
    PixelShader,
    VertexShader,
    PixelFragment,
    VertexFragment,
    Unsupported
};

struct String {
    char value[];
} [[inline]];

struct D3DXShaderTypeInfo {
    ParameterClass paramClass;
    ParameterType  paramType;
    u16 rows;
    u16 columns;
    u16 elements;
    u16 structMembers;
    u32 structMemberInfoOffset;
};

struct ConstantInfo {
    u32 nameOffset;
    RegisterSet registerSet;
    u16 registerIndex;
    u16 registerCount;
    u16 reserved;
    u32 typeInfoOffset;
    u32 defaultValueOffset;
    
    // Relative to ConstantTable
    if (nameOffset != 0) {
        String name @ (addressof(parent) + nameOffset);
    }
    if (typeInfoOffset != 0) {
        D3DXShaderTypeInfo typeInfo @ (addressof(parent) + typeInfoOffset);
    }
};

struct ConstantTable {
    u32 size;
    u32 creatorOffset;
    u32 version;
    u32 constantsCount;
    u32 constantInfoOffset;
    u32 flags;
    u32 targetOffset;
    
    if (creatorOffset != 0) {
        String creator @ (addressof(this) + creatorOffset);
    }
    if (targetOffset != 0) {
        String targetProfile @ (addressof(this) + targetOffset);
    }

    ConstantInfo constants[constantsCount] @ (addressof(this) + constantInfoOffset);
};

struct ConstantTableContainer {
    u32 containerLength;
    ConstantTable constantTable;
};

struct MicrocodeBlock {
    u32 microcodeSize;
    u8  microcode[microcodeSize];
};

struct X360ShaderContainer {
    u32 flags;                      // 0x102A1101 = VS, 0x102A1100 = PS
    u32 virtualSize;
    u32 physicalSize;
    u32 reservedC;
    u32 constantTableOffset;
    u32 definitionTableOffset;
    u32 shaderOffset;
    u32 reserved1C;
    u32 reserved20;

    if (constantTableOffset != 0) {
        ConstantTableContainer cTable @ (addressof(this) + constantTableOffset);
    }
    if (shaderOffset != 0) {
        MicrocodeBlock microcode @ (addressof(this) + shaderOffset);
    }
};

struct ParameterTable {
    u8 rawData[parent.totalSize];
};

struct ShaderEntry {
    u32 fileOffset;                 // Relative to start of THIS ShaderGroup
    u32 shaderType;
    u32 totalSize;
    u32 reserved;

    if (fileOffset != 0 && totalSize != 0) {
        u128 targetAddress = addressof(parent) + fileOffset;
        u32 targetMagic @ targetAddress;

        // Verify if it is an Xbox 360 shader container (0x102A1100 or 0x102A1101)
        if ((targetMagic & 0xFFFFFFFE) == 0x102A1100) {
            X360ShaderContainer shader @ targetAddress;
        } else {
            ParameterTable paramTable @ targetAddress;
        }
    }
};

struct ShaderGroup {
    u32 materialShaderID;
    u32 subShaderCount;
    u32 entryTableOffset;           // Relative to this group start
    u32 reservedOffsets[3];
    u32 groupSize;                  // Total size in bytes of this group
    u32 reserved;

    // The 4 entries (VS, PS, VS Params, PS Params)
    ShaderEntry entries[4] @ (addressof(this) + entryTableOffset);

    // Consume entire group size so next group starts at the right byte
    u8 _groupPayload[groupSize - ($ - addressof(this))];
};

struct NSHHeader {
    char magic[4];                  // "NSXR"
    u32 fileSize;
    u16 version;                    // 0x0200
    u16 totalPrograms;              // Total programs in file (0x016D = 365)
    u32 reserved1[5];

    // Array of shader groups (can be expanded up to totalPrograms)
    ShaderGroup groups[totalPrograms];
};

NSHHeader nsh @ 0x00;