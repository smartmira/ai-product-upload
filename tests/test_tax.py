import pandas as pd

xls = pd.ExcelFile(
    "app/taxonomy/TAXONOMY_CATEGORIZATION_9TH.xlsx"
)

first_sheet = xls.sheet_names[0]

print("FIRST SHEET:", first_sheet)

df = pd.read_excel(
    "app/taxonomy/TAXONOMY_CATEGORIZATION_9TH.xlsx",
    sheet_name=first_sheet
)

print(df.columns.tolist())
print(df.head())