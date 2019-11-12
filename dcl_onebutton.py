import pandas as pd
from args import args
from dcltools import dwn, grab_dcl, parse_pdf
import os


def main():
    pj_path, y = args.pj_path, args.y

    pj_dir_y, FILENAME, df = grab_dcl(pj_path, y)

    if df.shape != (0, 0):

        print(f'List of declarations saved in {FILENAME}')

        p = os.path.join(pj_dir_y, 'docs')

        if not os.path.exists(p):
            os.mkdir(p)

        dwn(df, p)
        parse_pdf(df, pj_dir_y, p, f'{y}_')

    else:
        print(f"NO DECLARATIONS IN {y}")

if __name__ == "__main__":
    main()