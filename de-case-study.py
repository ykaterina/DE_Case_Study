import tabula
import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_values

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
      
  )

  cursor = conn.cursor()
  insertQuery = """
    INSERT INTO certificate_holders_smt (date, total_principal_funds_available)
    VALUES %s
    
    ON CONFLICT (date)
    DO UPDATE SET 
      total_principal_funds_available = EXCLUDED.total_principal_funds_available"""

  execute_values(cursor, insertQuery, data)
  conn.commit()
  conn.close()
  
extract_principal_fund_available()