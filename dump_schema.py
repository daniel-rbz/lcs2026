import pandas as pd
import json

xl = pd.ExcelFile('c:/Users/Valen/Desktop/A_projects/lcs2026/data/Laurier Financial OS Data.xlsx')
schema = {}
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    schema[sheet] = {
        "columns": df.columns.tolist(),
        "first_row": df.iloc[0].to_dict() if not df.empty else None,
        "unique_campuses": df['campus'].unique().tolist() if 'campus' in df.columns else None,
        "unique_residencies": df['residency'].unique().tolist() if 'residency' in df.columns else None
    }

with open('schema_dump.json', 'w') as f:
    json.dump(schema, f, indent=4)
