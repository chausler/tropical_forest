import pandas as pd
from pandas import DataFrame
import json


"""
Using pandas api to recongizing time stamps and separating the data in quarterly interval.
"""
DATA_PATH = '../data/hilary'
lst = json.load(open(DATA_PATH+'/hilary.json'))
df = DataFrame(lst, columns=['date', 'email'])
df.date = pd.to_datetime(df.date)
df= df[(df.date.dt.year >= 2009) & (df.date.dt.year <=2012)]
for label, df in df.groupby(df.date.dt.year.map(str)+":"+ df.date.dt.month.map(lambda x: str(x%4))):
    print(label)
    print(df)
    lst = df.values.tolist()
    lst = [x[1] for x in lst]
    json.dump(lst, open('{}.json'.format(label), 'w'))
