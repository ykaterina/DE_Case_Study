import tabula
import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import dotenv_values
from sqlalchemy import create_engine

config = dotenv_values()
database = config.get("DATABASE")
user = config.get("USER")
password = config.get("PASSWORD")


def extract_principal_fund_available():
    folderpath = '~/Documents/PYTHON/Xelure_Case_Study/Xelure Assessment/DE_Citi_Certificate Holders Statement/'
    files = os.listdir(os.path.expanduser(folderpath))
    data = []

    for f in files:
        if f.endswith('.pdf'):
            filenamelen = len(f)
            date = f'20{f[len(f)-8:filenamelen-4]}'
            df = tabula.io.read_pdf(
                folderpath + f, pages=6, columns=[0, 4], force_subprocess=True, multiple_tables=True, pandas_options={'header': None})

            if isinstance(df, list):
                if len(df) > 0:
                    if isinstance(df[0], pd.DataFrame):
                        df = df[0]
                    else:
                        raise ValueError("Unexpected data format in list.")
                else:
                    raise ValueError("Empty list returned.")
            else:
                raise ValueError("Unexpected data type returned.")

            # column containing total_principal_funds_available
            column4 = df[3].replace(',', '', regex=True).astype(float)
            total_principal_funds_available = column4.iloc[18]
            data.append((
                date,
                total_principal_funds_available
            ))

    conn = psycopg2.connect(
        host="localhost",
        database=database,
        user=user,
    )

    cursor = conn.cursor()
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
        '~/Documents/PYTHON/Xelure_Case_Study/Xelure Assessment/DE_Citi_Loan Level Data/')
    files = os.listdir(folderpath)

    conn = psycopg2.connect(
        host="localhost",
        database=database,
        user=user,
    )
    cursor = conn.cursor()

    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost:5432/{database}")
    for f in files:
        csv_path = folderpath + f

        if f.endswith('.csv'):
            tablename = f.replace('.csv', '').lower()

            df = pd.read_csv(csv_path)
            df.columns = [x.lower().replace(' ', '').replace('#', 'no').replace('&', 'and')
                          .replace(',', '').replace('/', '').replace('%', 'perc')
                          for x in df.columns]

            df.to_sql(tablename, engine, if_exists='replace',
                      index=False)


def get_loan_detail_cml():
    folderpath = os.path.expanduser(
        '~/Documents/PYTHON/Xelure_Case_Study/Xelure Assessment/DE_Citi_Enhanced_Loan_Level_Data/')
    files = os.listdir(folderpath)

    engine = create_engine(
        f"postgresql://{user}:{password}@localhost:5432/{database}")
    for f in files:
        csv_path = folderpath + f

        if f.endswith('.csv'):
            tablename = f.replace('.csv', '').lower()

            df = pd.read_csv(csv_path)
            df.columns = [x.lower().replace(' ', '').replace(
                '#', 'no').replace('/', '') for x in df.columns]

            df.to_sql(tablename, engine, if_exists='replace',
                      index=False)


get_loan_detail_cml()
extract_principal_fund_available()
get_loan_level_data()