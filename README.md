This is a case study on creating a POC for a system that would allow an analyst to audit past transactions and run quality checks to test for potential issues.

**REQUIREMENTS**
1. Extract the value for “Total Principal Funds Available”
   - PDFReader library is used to extract the target value 
   - date column is added which contains yyyydd date format of the report period
   - Issues encountered:
      * The target data is in different page in some of the files. The script will try to extract data from p6 which the data is commonly found. If not, it will loop through all the pages until the data is found
      * As the extracted data from PDF is text, and contains comma(,), the scripts removed the comma first before inserting the data into the database

2. Load the data from loan-level data into a database
   - The script loaded the data from CSV into a DataFrame and used to_sql() method to insert data into the database.
   - There are 2 functions for this: get_loan_level_data and get_loan_detail_cml()
   - Issues encountered:
      * In Loan-Level Data, the columns count is not the same in all files, some files would have 'Deal ID', and some do not. The script checks if 'Deal ID' column is present in the DataFrame, and add it if not found.
      * Special Characters in the CSV headers. The script removes special characters from the headers in the dataframe and converts them to lower case.
      * Column yyyymm is also added in Loan-Level Data to easily identify which period the data is from.
      * 1 column (modificationdate) was created as a numeric field because it contained numbers (e.g.202402) as with other 'date' fields in some of the files, but some files has values of xxxxxxxx which created a mismatch. I changed the data type in DB as varchar to accept this value.

3. Query the database to verify the total principal in loan level data and the certificate holders statement (PDF) matches
     - I created a query to get the columns in the PDF from enhanced loan-level data that sums up the total principal funds available. The query includes diff column which mean the difference in the total_principal_funds_available from the PDF with the sum of all the columns from the loan_level_data
     - Issue encountereds: 
         * Unable to find find 2 column/value from the PDF in the CSV files (net liquidation proceeds and substitution pricipan), causing significant the value in the diff column.
         * There is no enhanced loan level data from 2006-10 to 2007-06 to compare with the PDF values

4. **SUMMARY**

   Due to missing columns from the validation query, it cannot be determined whether the PDF and CSV data matched. But data in some manually checked reports do not match

      Potential improvements for this project:
      - Find the missing columns for more accurate query results. If these fields are aggregated values of different columns, it would be helpful to have a visibility on what the columns mean.
      - Create a RegEx to better filter special characters in columns.
      - Use indexing options to improve querying experience
      - Add primary key for quick reference when quering (I attempted to do this but found that loan identification number have duplicates in one of the reports)
      - clean the data for uniformity (ex. remove 'xxxxxx' value in modificationdate column)
      - If new reports would be added periodically, creating a workflow for these tasks is recommended
