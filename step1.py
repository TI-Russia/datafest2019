from args import args
from dcltools import grab_dcl


pj_path, y = args.pj_path, args.y

_, FILENAME, _ = grab_dcl(pj_path, y)

print(f'List of declarations saved in {FILENAME}')