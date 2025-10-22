import pandas as pd, os

def read_excel_file(file_path='./feature_excel/feature_map.xlsx'):
    """
    Check if file exists and return dataframe dictionary
    """
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return None
    
    """
    Reads an Excel file and returns its content as a pandas DataFrame.
    """
    try:
        all_dfs = pd.read_excel(file_path, sheet_name=None)
        return all_dfs
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    
dfs = read_excel_file()

# for sheet_name, df in dfs.items():
#     print(f"Sheet name: {sheet_name}")
#     print(f"DF Size: {len(df)} rows, {len(df.columns)} columns")
#     # print(df.head())

# for df in dfs:
#     df.ffill()

df = dfs['Features'].ffill() # type: ignore
# print(df)
# print(df.columns.tolist())
# df1 = df.ffill()
# print(df1)
# print(df1.columns.tolist())

data_list = df.to_dict(orient='records')
for item in data_list:
    print(item)