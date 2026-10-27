import struct
import json
import sys

def read_null_string(data, offset):
    if offset >= len(data):
        return ""
    end = data.find(b'\x00', offset)
    if end == -1:
        end = len(data)
    try:
        return data[offset:end].decode('latin-1')
    except Exception:
        return ""

def parse_d3dx_constants(container_bytes):
    constants = {}
    if len(container_bytes) < 0x24:
        return constants
        
    c_table_offset = struct.unpack_from(">I", container_bytes, 0x10)[0]
    if c_table_offset == 0:
        return constants
        
    ct_base = c_table_offset + 4
    if ct_base + 28 > len(container_bytes):
        return constants
        
    size, creator_off, version, num_consts, const_info_off, flags, target_off = struct.unpack_from(">IIIIIII", container_bytes, ct_base)
    
    info_pos = ct_base + const_info_off
    for _ in range(num_consts):
        if info_pos + 20 > len(container_bytes):
            break
            
        name_off, reg_set, reg_idx, reg_count, _, type_off, _ = struct.unpack_from(">IHHIHII", container_bytes, info_pos)
        name = read_null_string(container_bytes, ct_base + name_off)
        
        if name:
            constants[name] = {
                "register_index": reg_idx,
                "register_count": reg_count,
                "register_type": "Float" if reg_set == 2 else ("Sampler" if reg_set == 3 else "Other")
            }
        info_pos += 20
        
    return constants

def dump_namco_mappings(nsh_path, output_json):
    with open(nsh_path, "rb") as f:
        data = f.read()

    file_len = len(data)
    magic, file_size, version, total_programs = struct.unpack_from(">4sIHH", data, 0)
    assert magic == b"NSXR", "Not an NSXR file!"

    current_pos = 0x20
    all_materials = {}

    while current_pos + 0x20 <= file_len:
        material_id, sub_count, table_rel_offset = struct.unpack_from(">III", data, current_pos)
        group_size = struct.unpack_from(">I", data, current_pos + 0x18)[0]
        
        if group_size == 0 or group_size > (file_len - current_pos):
            break

        mat_key = f"0x{material_id:08X}"
        entry_table_pos = current_pos + table_rel_offset
        
        # 1. Grab registers from the VS & PS containers (Entries 0 & 1)
        vs_constants = {}
        ps_constants = {}
        for stage_idx, target_dict in [(0, vs_constants), (1, ps_constants)]:
            if entry_table_pos + (stage_idx + 1) * 16 <= file_len:
                f_off, _, size, _ = struct.unpack_from(">IIII", data, entry_table_pos + stage_idx * 16)
                if f_off != 0 and size != 0 and (current_pos + f_off + size) <= file_len:
                    shader_data = data[current_pos + f_off : current_pos + f_off + size]
                    target_dict.update(parse_d3dx_constants(shader_data))

        # 2. Grab Namco Binding Tables (Entries 2 & 3)
        param_bindings = {}
        for entry_idx in [2, 3]: # VS params, PS params
            if entry_table_pos + (entry_idx + 1) * 16 > file_len:
                break
                
            f_off, s_type, size, _ = struct.unpack_from(">IIII", data, entry_table_pos + entry_idx * 16)
            
            if f_off != 0 and size != 0 and (current_pos + f_off + size) <= file_len:
                table_base = current_pos + f_off
                
                first_str_off = struct.unpack_from(">I", data, table_base)[0]
                
                # Check: string offset must be past the table start (f_off)
                if first_str_off > f_off:
                    records_len = min(first_str_off - f_off, size)
                    num_records = records_len // 0x20
                else:
                    num_records = size // 0x20
                
                for r in range(num_records):
                    rec_pos = table_base + r * 0x20
                    if rec_pos + 32 > file_len:
                        break
                        
                    shader_name_off, _, engine_name_off, _, _, count, _, _ = struct.unpack_from(">IIIIIIII", data, rec_pos)
                    
                    if shader_name_off == 0 or engine_name_off == 0:
                        continue
                        
                    if (current_pos + shader_name_off) < file_len and (current_pos + engine_name_off) < file_len:
                        shader_param = read_null_string(data, current_pos + shader_name_off)
                        engine_param = read_null_string(data, current_pos + engine_name_off)
                        
                        if engine_param and shader_param:
                            reg_info = vs_constants.get(shader_param) or ps_constants.get(shader_param) or {}
                            param_bindings[engine_param] = {
                                "shader_param": shader_param,
                                "vector_count": count,
                                "register": f"c{reg_info.get('register_index', '?')}" if reg_info else "c?"
                            }

        all_materials[mat_key] = {
            "parameters": param_bindings
        }

        current_pos += group_size

    with open(output_json, "w") as out:
        json.dump(all_materials, out, indent=4)

    print(f"Exported mapping for {len(all_materials)} materials to {output_json}")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "shader.nsh"
    dump_namco_mappings(input_file, "material_bindings.json")