import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import dotenv_values
from sqlalchemy import create_engine
from pypdf import PdfReader 
import logging

config = dotenv_values()
database = config.get("DATABASE")
user = config.get("USER")
password = config.get("PASSWORD")

def extract_page_from_pdf(file, pagenum):
    reader = PdfReader(file) 
    
    page = reader.pages[pagenum] 

    content = page.extract_text()
    contentlist = content.splitlines()

    res = [i for i in contentlist if "Total Principal Funds Available" in i]
    value = None
    if len(res) > 0:
        value = res[0].split("Available:", 1)[1].strip()
 
    return value

def extract_principal_fund_available():
    folderpath = '~/Documents/PYTHON/DE_Case_Study/Case_Study_Files/DE_Citi_Certificate Holders Statement/'
    files = os.listdir(os.path.expanduser(folderpath))
    fullpath = os.path.expanduser(folderpath)
    data = []

    conn = psycopg2.connect(
                host="localhost",
                database=database,
                user=user,
            )

    cursor = conn.cursor()
    for f in files:
        if f.endswith('.pdf'):
            filenamelen = len(f)
            date = f'20{f[len(f)-8:filenamelen-4]}'

            total_principal_funds_available = extract_page_from_pdf(fullpath + f, 5)
            ctr = 0
            while(total_principal_funds_available is None):
                total_principal_funds_available = extract_page_from_pdf(fullpath + f, ctr)
                ctr = ctr + 1
                
            # print('total_principal_funds_available',total_principal_funds_available)
            data.append((date, total_principal_funds_available.replace(',','')))

            
            insertQuery = """
            INSERT INTO certificate_holders_smt (date, total_principal_funds_available)
            VALUES %s

            ON CONFLICT (date)
            DO NOTHING"""

            execute_values(cursor, insertQuery, data)
            conn.commit()

    conn.close()


def get_loan_level_data():
    folderpath = os.path.expanduser(
        '~/Documents/PYTHON/DE_Case_Study/Case_Study_Files/DE_Citi_Loan Level Data/')
    files = os.listdir(folderpath)

    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost:5432/{database}")
    for f in files:
        csv_path = folderpath + f
        filenamelen = len(f)
        date = f'20{f[len(f)-8:filenamelen-4]}'
        if f.endswith('.csv'):
            df = pd.read_csv(csv_path)
            df.columns = [x.lower().replace(' ', '').replace('#', 'no').replace('&', 'and')
                          .replace(',', '').replace('/', '').replace('%', 'perc')
                          for x in df.columns]
            df.insert(0, 'yyyymm',date)

            if 'dealid' not in df.columns:
                df.insert(1, 'dealid', None)

            df.to_sql('loanleveldata', engine, if_exists='replace',
                      index=False)


def get_loan_detail_cml():
    folderpath = os.path.expanduser(
        '~/Documents/PYTHON/DE_Case_Study/Case_Study_Files/DE_Citi_Enhanced_Loan_Level_Data/')
    files = os.listdir(folderpath)

    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost:5432/{database}")
    for f in files:
        csv_path = folderpath + f
        if f.endswith('.csv'):
            df = pd.read_csv(csv_path)
            df.columns = [x.lower().replace(' ', '').replace(
                '#', 'no').replace('/', '') for x in df.columns]

            df.to_sql('enhancedloanleveldata', engine, if_exists='append',
                      index=False)


get_loan_detail_cml()
extract_principal_fund_available()
get_loan_level_data()
