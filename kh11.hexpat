struct KHeader{
    u32 magic;
    u8 day;
    u8 month;
    u16 year;
    u8 sec;
    u8 min;
    u16 hour;
    u16 numEntries;
    u16 unk4;
    u32 attack_list;
    u32 throw_info;
    u16 moveGrpIdx1;
    u16 moveGrpCount1;
    u16 moveGrpIdx2;
    u16 moveGrpCount2;
    u16 hurtIdx;
    u16 hurtCount;
    u16 neutralIdx;
    u16 neutralCount;
};
u32 attack_count = 0;
struct smallbit{
u32 unk0;
u32 unk1;
u32 unk2;
u32 unk3;
};
struct largebit{
smallbit unkpack[5];
u32 tail0;
u32 tail1;
};
struct moves{
s16 motionIdx;
u16 unkMotion;
u32 unk0;
float motion_multiplier;
float speed_multiplier;
u32 unk1;

u32 unk2;
u32 unk3;
float unk4;

u32 unk5;
u32 unk6;
u32 unk7;
u32 unk8;

float unknown_multiplier;
s16 frameCount;
u16 frameCountUnk;
u32 cancel_address;
u8 test @ cancel_address;
s32 attack_index;
s32 attack_index2;
u32 idk;
if(attack_index > 0){
attack_count = attack_index+1;
}
if(attack_index2 > 0){
attack_count = attack_count+1;
}
};
struct vec3short{
s16 x;
s16 y;
s16 z;
};
struct attacks {
    u16 hitbox; //hitbox limb?? 40 40 = right leg? 80 80 = left leg ??
    
    u16 unk1;
    u32 unk2;
    
    vec3short normal_vec;
    vec3short normal_launch_vec;
    vec3short counter_vec;
    vec3short counter_launch_vec;
    vec3short airborne_vec;
    vec3short block_vec;
    vec3short grounded_vec;
    
    u16 hit_level;
    
    u16 stange_guard;
    u16 startup;
    u16 active;
    u16 dmg;
    
    u16 block_stun;
    u16 hit_stun;
    u16 counter_stun;
    
    u16 blockstun_alt;
    u16 hit_stun_alt;
    u16 counter_stun_alt;
    
    u16 hit_effect;
    u16 counter_effect;
    
    u16 unk_effect;
    
    u16 block_effect;
    u16 block_crush_effect;
    padding[13];
    u8 end;
};
struct KHFile{
KHeader hdr;
moves movGroup1[hdr.moveGrpCount1];
moves movGroup2[hdr.moveGrpCount2];
moves hurtGroup[hdr.hurtCount];
moves neturalGroup[hdr.neutralCount];
attacks aChunk[attack_count];

};

KHFile file @ 0;