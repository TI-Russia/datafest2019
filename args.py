import argparse
from datetime import datetime

argparser = argparse.ArgumentParser()

argparser.add_argument(
    "--pj_path", 
    type=str, 
    default=".",
    help="Path to project directory"
    )
argparser.add_argument(
    "--y", 
    type=str, 
    choices=list(range(1998, datetime.now().year)),
    default=str(datetime.now().year),
    help="Declarations year"
    )
argparser.add_argument(
    "--table", 
    type=str,
    help="Path to the table with declarations"
    )
argparser.add_argument(
    "--p", 
    type=str,
    default="./docs",
    help="path to directory with PDF's"
    )


args = argparser.parse_args()