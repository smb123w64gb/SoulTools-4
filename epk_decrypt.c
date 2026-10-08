#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static inline uint32_t rotl32(uint32_t x, uint32_t r) {
    return (x << r) | (x >> (32 - r));
}

static inline uint32_t rotr32(uint32_t x, uint32_t r) {
    return (x >> r) | (x << (32 - r));
}

static inline uint32_t reverse_bits32(uint32_t x) {
    x = ((x >> 1) & 0x55555555) | ((x & 0x55555555) << 1);
    x = ((x >> 2) & 0x33333333) | ((x & 0x33333333) << 2);
    x = ((x >> 4) & 0x0F0F0F0F) | ((x & 0x0F0F0F0F) << 4);
    x = ((x >> 8) & 0x00FF00FF) | ((x & 0x00FF00FF) << 8);
    return (x >> 16) | (x << 16);
}

void crypt_buffer(uint8_t *buffer, size_t length, uint32_t offset, uint32_t key1, uint32_t key2) {
    uint32_t block_index = offset >> 10;
    uint32_t word_in_block = (offset & 0x3FF) >> 2;

    size_t total_words = (length + 3) >> 2;
    uint32_t *buf32 = (uint32_t *)buffer;
    uint32_t last_seed = 0;

    while (total_words > 0) {
        uint32_t v = block_index + key1;
        v = v + reverse_bits32(v);
        uint32_t rot = ((block_index * 3) % 29 + 2) & 0x1F;
        uint32_t seed = rotr32(v, rot) ^ key2;

        for (uint32_t i = 0; i < word_in_block; ++i) {
            seed = (rotl32(seed, 3) * 5) + 1;
        }

        uint32_t words_in_block = 256 - word_in_block;
        if (words_in_block > total_words) {
            words_in_block = (uint32_t)total_words;
        }

        for (uint32_t i = 0; i < words_in_block; ++i) {
            last_seed = seed;
            *buf32 ^= seed;
            buf32++;
            seed = (rotl32(seed, 3) * 5) + 1;
        }

        total_words -= words_in_block;
        block_index++;
        word_in_block = 0;
    }

    uint32_t trailing = length & 3;
    if (trailing != 0) {
        static const uint32_t masks[4] = { 0, 0xFFFFFF00, 0xFFFF0000, 0xFF000000 };
        buf32[-1] ^= (masks[trailing] & last_seed);
    }
}

#define CHUNK_SIZE (4 * 1024 * 1024) // 4 MB I/O buffer

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Usage: %s <input data.epk> <output.cpk>\n", argv[0]);
        return 1;
    }

    FILE *fin = fopen(argv[1], "rb");
    if (!fin) {
        perror("Failed to open input file");
        return 1;
    }

    uint8_t header[0x800];
    if (fread(header, 1, 0x800, fin) != 0x800) {
        printf("File too small!\n");
        fclose(fin);
        return 1;
    }

    uint32_t word_0 = *(uint32_t *)(header + 0x000);
    uint32_t word_7fc = *(uint32_t *)(header + 0x7FC);

    if (word_0 == 0x204B5043 && word_7fc == 0x49524329) {
        printf("File is already decrypted CPK!\n");
        fclose(fin);
        return 0;
    }

    uint32_t key1 = word_0 ^ 0xC12811F9 ^ 0x83145CA9;
    uint32_t key2 = word_7fc ^ 0xC6ABEE05 ^ 0xD82BBFD5;

    printf("Derived Key 1: 0x%08X\n", key1);
    printf("Derived Key 2: 0x%08X\n", key2);

    FILE *fout = fopen(argv[2], "wb");
    if (!fout) {
        perror("Failed to open output file");
        fclose(fin);
        return 1;
    }

    // Decrypt and patch header
    crypt_buffer(header, 0x800, 0, key1, key2);
    *(uint32_t *)(header + 0x000) = 0x204B5043; // "CPK "
    *(uint32_t *)(header + 0x7FC) = 0x49524329; // ")CRI"
    fwrite(header, 1, 0x800, fout);

    uint8_t *chunk = (uint8_t *)malloc(CHUNK_SIZE);
    uint32_t offset = 0x800;
    size_t bytes_read = 0;

    printf("Decrypting...\n");
    while ((bytes_read = fread(chunk, 1, CHUNK_SIZE, fin)) > 0) {
        crypt_buffer(chunk, bytes_read, offset, key1, key2);
        fwrite(chunk, 1, bytes_read, fout);
        offset += bytes_read;
        printf("\rProgress: %.2f MB", (double)offset / (1024.0 * 1024.0));
        fflush(stdout);
    }

    printf("\nDone!\n");
    free(chunk);
    fclose(fin);
    fclose(fout);
    return 0;
}