import pandas as pd
import sys

pd.set_option('display.max_rows', 10)

xl = pd.ExcelFile('c:/Users/Valen/Desktop/A_projects/lcs2026/data/Laurier Financial OS Data.xlsx')
df = xl.parse('Gas Prices Canada')

print(df.head())
print(df.dtypes)
