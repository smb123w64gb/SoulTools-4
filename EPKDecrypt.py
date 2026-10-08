import struct
import sys

def reverse_bits32(n: int) -> int:
    n = ((n >> 1) & 0x55555555) | ((n & 0x55555555) << 1)
    n = ((n >> 2) & 0x33333333) | ((n & 0x33333333) << 2)
    n = ((n >> 4) & 0x0F0F0F0F) | ((n & 0x0F0F0F0F) << 4)
    n = ((n >> 8) & 0x00FF00FF) | ((n & 0x00FF00FF) << 8)
    return (((n >> 16) | (n << 16)) & 0xFFFFFFFF)

def rotl32(x: int, r: int) -> int:
    return (((x << r) | (x >> (32 - r))) & 0xFFFFFFFF)

def rotr32(x: int, r: int) -> int:
    return (((x >> r) | (x << (32 - r))) & 0xFFFFFFFF)

def decrypt_chunk(data: bytearray, offset: int, key1: int, key2: int) -> bytearray:
    length = len(data)
    total_words = (length + 3) // 4
    block_index = offset >> 10
    word_in_block = (offset & 0x3FF) >> 2

    buf_idx = 0
    while total_words > 0:
        # Per 1024-byte block seed
        v = (block_index + key1) & 0xFFFFFFFF
        v = (v + reverse_bits32(v)) & 0xFFFFFFFF
        rot = ((block_index * 3) % 29 + 2) & 0x1F
        seed = rotr32(v, rot) ^ key2

        # Fast-forward if starting within block
        for _ in range(word_in_block):
            seed = ((rotl32(seed, 3) * 5) + 1) & 0xFFFFFFFF

        words_in_block = min(256 - word_in_block, total_words)
        for _ in range(words_in_block):
            ks = seed.to_bytes(4, 'little')
            for b in range(4):
                pos = buf_idx * 4 + b
                if pos < length:
                    data[pos] ^= ks[b]

            buf_idx += 1
            seed = ((rotl32(seed, 3) * 5) + 1) & 0xFFFFFFFF

        total_words -= words_in_block
        block_index += 1
        word_in_block = 0

    return data

def decrypt_epk(input_path: str, output_path: str):
    print(f"Opening {input_path}...")
    with open(input_path, "rb") as fin:
        # Read the first 0x800 header to check and extract keys
        header = bytearray(fin.read(0x800))
        if len(header) < 0x800:
            print("File is too small to be a valid data.epk")
            return

        word_0 = struct.unpack_from("<I", header, 0x000)[0]
        word_7fc = struct.unpack_from("<I", header, 0x7FC)[0]

        # Check if already decrypted
        if word_0 == 0x204B5043 and word_7fc == 0x49524329:
            print("File is already a decrypted CPK archive!")
            return

        # Derive keys
        key1 = word_0 ^ 0xC12811F9 ^ 0x83145CA9  # word_0 ^ 0x423c4d50
        key2 = word_7fc ^ 0xC6ABEE05 ^ 0xD82BBFD5  # word_7fc ^ 0x1e8051d0

        print(f"Derived Key 1: 0x{key1:08X}")
        print(f"Derived Key 2: 0x{key2:08X}")

        # Decrypt header
        decrypt_chunk(header, 0, key1, key2)

        # Restore CPK magic headers
        struct.pack_into("<I", header, 0x000, 0x204B5043)  # "CPK "
        struct.pack_into("<I", header, 0x7FC, 0x49524329)  # ")CRI"

        with open(output_path, "wb") as fout:
            fout.write(header)

            offset = 0x800
            chunk_size = 0x20000  # 128 KB chunks
            while True:
                chunk = bytearray(fin.read(chunk_size))
                if not chunk:
                    break
                decrypt_chunk(chunk, offset, key1, key2)
                fout.write(chunk)
                offset += len(chunk)
                print(f"\rDecrypted: {offset / (1024*1024):.2f} MB", end="")

    print(f"\nFinished! Decrypted archive saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python decrypt.py <data.epk> <output.cpk>")
    else:
        decrypt_epk(sys.argv[1], sys.argv[2])