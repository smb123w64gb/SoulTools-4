import os
import struct,sys

def extract_nsxr(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(file_path, "rb") as f:
        data = f.read()

    file_len = len(data)
    
    # 4s = magic (4), I = fileSize (4), H = version (2), H = totalPrograms (2)
    magic, file_size, version, total_programs = struct.unpack_from(">4sIHH", data, 0)
    
    if magic != b"NSXR":
        print(f"Error: Expected 'NSXR', got {magic}")
        return

    print(f"File Size: {file_size} bytes")
    print(f"Version: {version >> 8}.{version & 0xFF}")
    print(f"Header Program Count: {total_programs}")

    current_pos = 0x20  # Payload starts at 0x20
    group_index = 0
    extracted_count = 0

    while current_pos + 0x20 <= file_len:
        material_id, sub_count, table_rel_offset = struct.unpack_from(">III", data, current_pos)
        group_size = struct.unpack_from(">I", data, current_pos + 0x18)[0]
        
        # Stop if we hit zero padding at EOF
        if group_size == 0 or group_size > (file_len - current_pos):
            break

        entry_table_pos = current_pos + table_rel_offset
        
        # Each group has up to 4 entries (VS, PS, VS Params, PS Params)
        for entry_idx in range(4):
            if entry_table_pos + (entry_idx + 1) * 16 > file_len:
                break
                
            file_rel_offset, shader_type, total_size, _ = struct.unpack_from(
                ">IIII", data, entry_table_pos + entry_idx * 16
            )
            
            if file_rel_offset != 0 and total_size != 0:
                target_address = current_pos + file_rel_offset
                
                if target_address + 4 <= file_len:
                    magic_check = struct.unpack_from(">I", data, target_address)[0]
                    
                    # 0x102A1101 = VS, 0x102A1100 = PS
                    if (magic_check & 0xFFFFFFFE) == 0x102A1100:
                        stage = "vs" if (magic_check & 1) else "ps"
                        shader_bytes = data[target_address : target_address + total_size]
                        
                        filename = f"mat_{group_index:04d}_{material_id:08X}_{stage}_entry{entry_idx}.bin"
                        with open(os.path.join(output_dir, filename), "wb") as out:
                            out.write(shader_bytes)
                        
                        extracted_count += 1
        
        current_pos += group_size
        group_index += 1

    print(f"Done! Scanned {group_index} material groups and extracted {extracted_count} shader binaries.")

# Run extraction

extract_nsxr(sys.argv[1], sys.argv[1]+"_extracted")