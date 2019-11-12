import pandas as pd
from args import args
from dcltools import dwn


table, p = args.table, args.p

df = pd.read_excel(table)

dwn(df, p)
