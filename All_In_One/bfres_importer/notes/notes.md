Spm texture channels:
red:   specular
green: metal
blue:  unused

For bones: maybe "Smooth Mtx Idx" is really "group ID", to correspond with the vertex groups. So instead of adding 2, we use the bone that has the matching group ID.
Maybe "smooth matrix" is just someone's way of describing the whole vertex group/weight thing, and they don't really refer to a matrix?

bee u0: (22464, 10104) (1370, 2112) (55092, 53581) (9476, 26471) (33738, 19565) (12310, 45140) (57864, 33886) (4604, 30817) (27794, 12662) (40550, 639) (52128, 34650) (59632, 52558) (14784, 16492) (55444, 60747) (22464, 55672) (33737, 46189)

fox u0: (51, 104) (6, 234) (127, 213) (208, 132) (130, 60) (247, 21) (51, 104) (127, 213) (6, 234) (208, 132) (130, 60) (247, 21) (51, 104) (6, 234) (127, 213) (208, 132)

    |Vtxs|Faces|Tris|Bones|Texs
----|----|-----|----|-----|----
Link|5557| 7104|7104|  115|  35
Rena|5033| 7797|9612|  440|   3

I assume the bones need to have the same names...
may not matter if there are additional bones
same for textures

so the actual process would be:
- rename bones, vtx groups, textures to match original model
- replace bones, vertices, textures in the file
    - attributes p0, u0, i0?

poach, pod are things on the belt
Pod_A is shield attach?
each bone has a corresponding group
actually the rigs might be too different,
may need to re-rig the new model manually...
or make a script which compares bones in each rig to find those closest, renaming one to match the other
    - if source model has multiple bones in close proximity and target just has one, it could merge them, averaging their weights
for now I'm going with "manual" rigging (mostly Blender auto weights)

as for exporting to bfres, we can probably do that, but there are many unknown parameters we would need to generate:
- shader params
- render params
- material params
- relocation table
- all unknown fields
without generating most of these correctly, games probably won't accept the file.
we can cheat a bit and use the properties from a previously imported file.

if we want to just export a new model overtop of the existing one, all we really need to replace are the attributes (buffer data) and textures
we can probably just tack the new data on to the end of the file and point them to it. worry about actually rebuilding the file and replacing the old data later, once it works.

Attribute formats for Link:
FVTX|p0     |n0   |t0   |b0   |c0   |u0     |u1    |i0   |w0   |FSHP
----|-------|-----|-----|-----|-----|-------|------|-----|-----|------------------------
   0|half[4]|10bit|u8[4]|u8[4]|none |half[2]|u16[2]|u8[4]|u8[4]|Belt_A_Buckle__Mt_Belt_A
   1|half[4]|10bit|u8[4]|u8[4]|none |u16[2] |none  |u8[2]|u8[2]|Belt_C_Buckle__Mt_Belt_C
   2|half[4]|10bit|u8[4]|u8[4]|none |u16[2] |none  |u8   |none |Earring__Mt_Earring
   3|half[4]|10bit|u8[4]|u8[4]|none |half[2]|none  |u8   |none |Eye_L__Mt_Eyeball_L
   4|half[4]|10bit|u8[4]|u8[4]|none |s16[2] |none  |u8   |none |Eye_R__Mt_Eyeball_R
   5|half[4]|10bit|u8[4]|u8[4]|none |u16[2] |none  |u8[4]|u8[4]|Eyelashes__Mt_Eyelashes
   6|half[4]|10bit|u8[4]|u8[4]|u8[4]|u16[2] |u16[2]|u8[4]|u8[4]|Face__Mt_Face
   7|half[4]|10bit|u8[4]|u8[4]|u8[4]|u16[2] |u16[2]|u8[4]|u8[4]|Face__Mt_Head
   8|half[4]|10bit|u8[4]|u8[4]|none |u16[2] |none  |u8[4]|u8[4]|Skin__Mt_Lower_Skin
   9|half[4]|10bit|u8[4]|u8[4]|none |u16[2] |none  |u8[4]|u8[4]|Skin__Mt_Underwear
  10|half[4]|10bit|u8[4]|u8[4]|none |u16[2] |none  |u8[4]|u8[4]|Skin__Mt_Upper_Skin

Vtx attr names:
b: binormal
c: color
i: index (vtx group)
n: normal
p: position
t: tangent
u: UV coord
w: weight

pointers are also in RLT section 2 which is empty?
that can't be right, we use the RLT to find the buffers
`if rel: pos += self.rlt.sections[1]['curOffset'] # XXX`
section 1 curOffs=0x38000 size=0xA690 entryIdx=246 entryCnt=1
entry 246: curOffs=0x0150 structs=1 offsets=1 padding=0
not sure what that means, but I think the buffers are the only use of the RLT?
so if we changed that pointer, it might be enough
we could test by duplicating the data, changing the pointer to it, and testing
maybe changing some of the texture coords to see a difference
first we need to get the damn mods to load at all

- open a bfres file
- locate the buffer data
- change the pointers to new data
- scan the RLT for those old pointers
- change those too

original buffer layout:
n|size|strd|contents   |types  
0|0D50|0008|p0         |half[4]
1|0D50|0008|w0 i0      |u8[4], u8[4]
2|1AA0|0010|n0 t0 u0 u1|10bit, u8[4], half[2], u16[2]
3|06A8|0004|b0         |u8[4]
so it's mostly combined types of the same size
not sure why two different buffers for p0 and w0/i0

vtx_stridesize_offs =>
    int32_t stride;
    uint32_t divisor; //should be 0
    uint32_t reserved1;
    uint32_t reserved2;
    
Similarly, the pointer at FVTX + 0x38
(currently marked as "vertex buffer size") is another 0x10-long struct
which is composed of
    uint32_t size;
    uint32_t gpuAccessFlags; //should be 5
    uint32_t reserved1;
    uint32_t reserved2;

field        | orig  | modif | data
-------------|-------|-------|-----
dataOffs     | 42690 | 71C10 | floats?
bufSize      |  6450 | 71B80 | 0xD50, 0xD50, 0x1AA0, 0x6A8
strideSize   |  6490 | 71B90 | 8, 8, 16, 4
BS.size      | 39000 | 39000 | D000 D400 D700... looks like part of whatever is at 38000
BS.offs      | 38000 | 38000 | 0000 0100 0200...
vtx_buf_offs |  A690 | 39C10 | 0800 0000 1000 6200 167C 0300, last is \*"uking_enable_scene_color0_fog"
data from    | 42690 | 71C10 |
vtx_buf_offs == RLT.section[1].size
0x38000 + 0x39000 = 0x71000

RLT     |original|modified|note
--------|--------|--------|-------- "end of string pool"
0 base  |       0|       0|
0 offset|       0|       0|
0 size  |   37DAE|   37DAE| string pool ends here
0 total |   37DAE|   37DAE|
--------|--------|--------|-------- "index buffer"
1 base  |       0|       0|
1 offset|   38000|   38000| BufferSection.offset
1 size  |    A690|    A690|
1 total |   42690|   42690|
--------|--------|--------|-------- "vertex buffer"
2 base  |       0|       0|
2 offset|   42690|   71C10| pointer to buffer data
2 size  |   2E970|   2E970|
2 total |   71000|   A0580|
--------|--------|--------|-------- "memory pool"
3 base  |       0|       0|
3 offset|   71000|   71000| 0x38000 + 0x39000
3 size  |     120|     120|
3 total |   71120|   71120|
--------|--------|--------|-------- "external files"
4 base  |       0|       0|
4 offset|   71200|   71200|
4 size  |     100|     100|
4 total |   71300|   71300|
