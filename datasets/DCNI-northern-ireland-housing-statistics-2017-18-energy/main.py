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
tabs = { tab.name: tab for tab in scraper.distributions[1].as_databaker() } 

next_table = pd.DataFrame()

# +
# %%capture

# %run "T2.1.py"
next_table = pd.concat([next_table, new_table])
# %run "T2.2.py"
next_table = pd.concat([next_table, new_table])
# %run "T2.3.py"
next_table = pd.concat([next_table, new_table])
# %run "T2.4.py"
next_table = pd.concat([next_table, new_table])
# %run "T2.5.py"
next_table = pd.concat([next_table, new_table])
# -

next_table['Period'] = next_table['Period'].str.replace('\.0', '')

next_table['NI Household Description'] = next_table['NI Household Description'].apply(pathify)

next_table['NI Household Energy Status'] = next_table['NI Household Energy'].apply(pathify)

next_table['NI Household Energy Status'] = next_table['NI Household Energy Status'].map(lambda cell: cell.replace('/','-'))

next_table['NI Household Energy Status'] = next_table['NI Household Energy Status'].str.lstrip('-')


# +
def user_perc(x):
    
    if (str(x) ==  '*')  | (str(x) == '..'): 
        
        return 'not-defined'
    else:
        return 'no-marker'
    
next_table['NI Marker'] = next_table.apply(lambda row: user_perc(row['NI Marker']), axis = 1)
# -

next_table = next_table[['Period','NI Household Description','NI Household Energy Status','Unit','Value','Measure Type','NI Marker']]

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
