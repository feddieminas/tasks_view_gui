import os
import pandas as pd

def data():
    df = pd.read_excel(os.path.join(os.getcwd(), "data", "Tasks.xlsx"),
                       engine='openpyxl', sheet_name='Sheet1',
                       parse_dates=True
                       )

    lst = ['Team', 'Tasks', 'Description', 'Details (Free Text)', 'Notes']
    df[lst] = df[lst].astype(str).replace('nan', '')
    df['Duration (Hours)'].fillna(0, inplace=True)
    df['Period'] = pd.to_datetime(df['Period'].astype(str))

    return df
