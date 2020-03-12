# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *

scraper = Scraper('https://www.communities-ni.gov.uk/publications/topic/8182?search=%22Northern+Ireland+Housing+Statistics%22&sort_by=field_published_date')
tabs = { tab.name: tab for tab in scraper.distributions[6].as_databaker() } 

next_table = pd.DataFrame()

# +
# %%capture

# %run "T1.1.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.2.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.3.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.4.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.5.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.6.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.7.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.8.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.9.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.10.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.11a.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.11b.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.12.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.13.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.14.py"
next_table = pd.concat([next_table, new_table])
# %run "T1.15.py"
next_table = pd.concat([next_table, new_table])
# -

next_table = next_table[next_table['Geography'].isnull() == False]

next_table = next_table[next_table['Geography'] != 'Republic of Ireland']

next_table['NI Geography'] = next_table['Geography'].apply(pathify)

next_table['NI Geography'] = next_table['NI Geography'].map(
    lambda x: {
'northern-ireland': 'n92000002',
'great-britain': 'k03000001',
'ards-and-north-down': 'n09000011',
'armagh-city-banbridge-and-craigavon': 'n09000002',
'belfast': 'n09000003',
'causeway-coast-and-glens': 'n09000004',
'derry-city-and-strabane': 'n09000005',
'fermanagh-and-omagh': 'n09000006',
'lisburn-and-castlereagh': 'n09000007',
'mid-and-east-antrim': 'n09000008',
'mid-ulster': 'n09000009',
'newry-mourne-and-down': 'n09000010',
'antrim-and-newtownabbey': 'n09000001',
'antrim-newtownabbey': 'n09000001',
'ards-north-down': 'n09000011',
'armagh-city-banbridge-craigavon': 'n09000002',
'belfast-city': 'n09000003',
'causeway-coast-glens': 'n09000004',
'derry-city-strabane': 'n09000005',
'fermanagh-omagh': 'n09000006',
'lisburn-castlereagh': 'n09000007',
'mid-east-antrim': 'n09000008',
'newry-mourne-down': 'n09000010',
'strategic-planning-division': 'n92000002',
'armagh-banbridge-and-craigavon': 'n09000002',
'derry-and-strabane': 'n09000005',
}.get(x, x))

next_table['NI Housing Description'] = next_table['NI Housing Description'].apply(pathify)

next_table['NI Housing Supply'] = next_table['NI Housing Supply'].apply(pathify)


# +
def user_perc(x):
    
    if (str(x) ==  '-')  | (str(x) == '..') | (str(x) == 'Â®') : 
        
        return 'not-defined'
    else:
        return 'no-marker'
    
next_table['NI Marker'] = next_table.apply(lambda row: user_perc(row['NI Marker']), axis = 1)
# -

next_table = next_table[['Period','NI Geography','NI Housing Description','NI Housing Supply','Unit','Value','Measure Type','NI Marker']]

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
next_table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'affordable-housing'
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    scraper.dataset.license = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')

next_table['Unit'].unique()


