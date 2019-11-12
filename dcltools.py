from transliterate import translit
import random
import os
import time
import requests
from tqdm import tqdm
from datetime import datetime
import pandas as pd
from tabula.wrapper import read_pdf
import re
import json
from itertools import count
from bs4 import BeautifulSoup as bs


def parse_piece(n):
    name = n.find("div", {"class":"col-sm-3"}).text
    position = n.find("div", {"class":"col-sm-6"}).text
    daterow = n.find("div", {"class":"text-right"}).text
    date = re.search(r"\d\d\.\d\d.\d{4}$", daterow).group()
    office = n.find("div", {"class":"col-sm-9"}).text
    doc_url = "declaration.gov.ge" + n.find("a")["href"]
    return name, position, date, office, doc_url


def jsoner(name, position, date, office, doc_url):
    return {
        "name":name,
        "position":position,
        "date":date,
        "office":office,
        "doc_url":doc_url
    }


def transli(n):
    return translit(n, 'ka', reversed=True).lower()


def grab_dcl(path, y):
    DATA_KA = []

    # y = input(f"choose year from 1998 to {datetime.now().year} :")
    n = count(1)

    with tqdm() as pbar:
        while True:
        # for i in range(1,5):
            i = next(n)

            r = requests.get(f"https://declaration.gov.ge/Home/DeclarationList?YearSelectedValue={y}&page={i}")
            s = bs(r.text, "lxml")
            
            time.sleep(random.uniform(2.5, 3.5))
            
            pieces = s.find_all("div", {"class": "declaration1"})
            
            if pieces:
            
                for piece in pieces:
                    name, position, date, office, doc_url = parse_piece(piece)

                    j = jsoner(name, position, date, office, doc_url)
                    DATA_KA.append(j)

                pbar.update(len(pieces))
            
            else:
                break


    DF = pd.DataFrame(DATA_KA)
    DF.loc[:,'name_lat'] = DF.name.apply(transli)
    DF.loc[:,'office_lat'] = DF.office.apply(transli)
    DF.loc[:,'position_lat'] = DF.position.apply(transli)

    DF.loc[:,'id'] = list(map(lambda x: int(y+str(x)), DF.index.values))

    if DF.shape == (0, 0):
        return None, None, DF

    if not os.path.exists(path):
        os.mkdir(path)

    pj_dir_y = os.path.join(path, y)

    if not os.path.exists(pj_dir_y):
        os.mkdir(pj_dir_y)

    FILENAME = os.path.join(pj_dir_y, f"declarations_{y}.xlsx")

    writer = pd.ExcelWriter(
        FILENAME,
        engine='xlsxwriter',
        options={'strings_to_urls': False}
        )

    DF.to_excel(writer, index=False)

    writer.save()

    return pj_dir_y, FILENAME, DF


def dwn_lst(df, p):
     
    l = []

    for i, r in df.iterrows():
        name = str(r.id)+".pdf"
        if not name in os.listdir(p):
            path = os.path.join(p, name)
            t = (path, r.doc_url) 
            l.append(t)

    return l


def url_response(pu):
    path, url = pu

    if not re.search(r'^https://', url):
        url = 'https://'+url

    r = requests.get(url, stream = True)
    
    with open(path, 'wb') as f:
        f.write(r.content)
    
    time.sleep(random.uniform(1.5, 2.5))


def dwn(df, p):

    if not os.path.exists(p):
        os.mkdir(p)

    dwnlst = dwn_lst(df, p)
    
    with tqdm(total=len(dwnlst)) as pbar:
        for pu in dwnlst:
            url_response(pu)
            pbar.update()

    print(f"{len(os.listdir(p))} PDF's DONE")


def wow(data, i):
    data.loc[i-1] = data.loc[i-1].combine(data.loc[i], lambda a, b: a+' '+b)
    data.drop(i, inplace = True)
    
    
def make_fdf():
    return pd.DataFrame(
        columns=[
            'first_name',
            'last_name',
            'place_of_birth',
            'date_of_birth',
            'relationship'
        ]
    )

    

def make_pdf(): 
    return pd.DataFrame(
        columns=[
            'owner',
            'type',
            'purchase_date',
            'purchase_type',
            'price',
            'location_area',
            'owners'
        ]
    )


def fullrows(df, col):
    for i in df[df[col] == ''].index.values[::-1]:
        wow(df, i)

    return df


def get_info(df, columns):
    df = df.drop([0,1])

    df.rename(
        columns=columns, 
        inplace=True
    )

    return df


def parser(fn, path):

    famheader = {
        0:'first_name',
        1:'last_name',
        2:'place_of_birth',
        3:'date_of_birth',
        4:'relationship'
    }

    propheader = {
        0:'owner',
        1:'type',
        2:'purchase_date',
        3:'purchase_type',
        4:'price',
        5:'location_area',
        6:'owners'
    }

    fam = 'თქვენი ოჯახის წევრების (მეუღლე, არასრულწლოვანი შვილი, (გერი), თქვენთან მუდმივად მცხოვრები პირი) მონაცემები'
    prop = 'თქვენი, თქვენი ოჯახის წევრის საკუთრებაში არსებული უძრავი ქონება'

    rdate = re.compile(r'\s*\d\d\.\d\d.\d{4}$')
    place_and_date = 'დაბადების ადგილი, დაბადების თარიღი:\s*'

    dcl_data = {}

    FDF = make_fdf()
    PDF = make_pdf()

    dfs = read_pdf(
        os.path.join(path, fn),
        pages='all',
        lattice=True,
        multiple_tables=True
    )

    inf_flag = dfs[1].loc[0, 0]

    p_n_d = re.search(place_and_date+'(.+)', inf_flag)

    if p_n_d:

        pnd = p_n_d.group(1)
        place = re.sub(rdate, '', pnd)
        dcl_data['palse_of_birth'] = place


        date = re.search(rdate, pnd)

        if date:

            date = date.group().strip()
            dcl_data['date_of_birth'] = date

    for df in dfs[2:]:
        if df.shape != (0,0):

            if df.loc[0,0] == fam:
                FDF = FDF.append(get_info(df, famheader))

            if df.loc[0,0] == prop:
                PDF = PDF.append(get_info(df, propheader))
    
    if FDF.shape != (0, 0):

        FDF.fillna('', inplace=True)
        FDF.reset_index(drop=True, inplace=True)

        FDF = fullrows(FDF, 'first_name')

        FDF

        FDF.loc[:,'first_name'] = FDF.first_name.apply(transli)
        FDF.loc[:,'last_name'] = FDF.last_name.apply(transli)
        FDF.loc[:,'place_of_birth'] = FDF.place_of_birth.apply(transli)
        FDF.loc[:,'relationship'] = FDF.relationship.apply(transli)

        dcl_data['family'] = json.loads(FDF.to_json(orient = "records", force_ascii=False))

    if PDF.shape != (0, 0):

        PDF.fillna('', inplace=True)
        PDF.reset_index(drop=True, inplace=True)
        PDF = fullrows(PDF, 'owner')

        for i in PDF[PDF['location_area'].str.endswith(',')].index.values[::-1]+1:
            wow(PDF, i)

        PDF.loc[:,'owner'] = PDF.owner.str.replace('\r', ' ')
        PDF.loc[:,'location_area'] = PDF.location_area.str.replace('\r', ' ')

        PDF.loc[:,'owner'] = PDF.owner.apply(transli)
        PDF.loc[:,'type'] = PDF.type.apply(transli)
        PDF.loc[:,'purchase_type'] = PDF.purchase_type.apply(transli)
        PDF.loc[:,'location_area'] = PDF.location_area.apply(transli)
        PDF.loc[:,'owners'] = PDF.owners.apply(transli)

        dcl_data['purchase'] = json.loads(PDF.to_json(orient = "records", force_ascii=False))

    return dcl_data


def parse_pdf(df, cwd, pdfs_path, y=''):
    jdcl = json.loads(df.to_json(orient = "records", force_ascii=False))

    errors = []

    with tqdm(total=len(jdcl)) as pbar:
        for ii, dc in enumerate(jdcl):

            fn = str(dc["id"])+".pdf"

            try:
                dcl_data = parser(fn, pdfs_path)

                if dcl_data.keys():
                    jdcl[ii].update(dcl_data)

            except Exception as exce:
                e = (ii, exce, fn)
                errors.append(e)
            #     print(e)

            pbar.update()

    with open(os.path.join(cwd, y+'dcl_done_data.json'), 'w') as f:
        json.dump(jdcl, f, ensure_ascii=False)

    print('DONE')

    if errors:
        erdf = pd.DataFrame(errors, columns=['index', 'Error', 'file_name'])
        efname = os.path.join(cwd, 'erros_log.xlsx')
        erdf.to_excel(efname, index=False)
        print(f'ERRORS SAFED IN {efname}')
