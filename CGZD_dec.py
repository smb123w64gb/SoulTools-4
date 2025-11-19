import zlib
import sys

file_in = open(sys.argv[1],'rb')
file_out = open(sys.argv[1] + '.dec','wb')

file_in.seek(8)
file_out.write(zlib.decompress(file_in.read()))
file_out.close()
file_in.close()