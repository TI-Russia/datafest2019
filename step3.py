from args import args
from dcltools import parse_pdf
import pandas as pd

cwd, table, pdfs_path = args.pj_path, args.table, args.p

df = pd.read_excel(table)

parse_pdf(df, cwd, pdfs_path)