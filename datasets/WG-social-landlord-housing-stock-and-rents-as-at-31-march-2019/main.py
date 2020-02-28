# ---
# jupyter:
#   jupytext:
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

# +
from gssutils import *
from requests import Session
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter

scraper = Scraper('https://statswales.gov.wales/Catalogue/Housing/Social-Housing-Stock-and-Rents/averageweeklyrentsinstockatsocialrent-by-area-accommodation-providertype',
                  session=CacheControl(Session(),
                                       cache=FileCache('.cache'),
                                       heuristic=ExpiresAfter(days=7)))
scraper
# -

if len(scraper.distributions) == 0:
    from gssutils.metadata import Distribution
    dist = Distribution(scraper)
    dist.title = 'Dataset'
    dist.downloadURL = 'http://open.statswales.gov.wales/dataset/hous0601'
    dist.mediaType = 'application/json'
    scraper.distributions.append(dist)
table = scraper.distribution(title='Dataset').as_pandas()
table

table.columns

# Columns selected based on tidy data requirements

# +
cols = {
    'Area_AltCode1': 'WG Geography',
    'Accommodation_Code': 'Social Housing Accommodation',
    'Bedrooms_Code' : 'Social Housing Bedrooms',
    'Data': 'Value',
    'Dwelling_Code' : 'Social Housing Dwelling Type',
    'Measure_ItemName_ENG' : 'Unit',
    'Provider_Code': 'Social Housing Provider',
    'Year_Code': 'Year', 
    
}
to_remove = set(table.columns) - set(cols.keys())
table.rename(columns=cols, inplace=True)
table.drop(columns=to_remove, inplace=True)
table
# -

table['Year'] = table['Year'].astype(str)

table['Year'] = table['Year'].astype(str).str[0:4]+ table['Year'].astype(str).str[-2:]   


# +
def user_perc(x):
    if 'Q' in str(x) :
        return 'quarter/' + str(x)[0:4]+ '-' + str(x)[-2:]
    else:
        return 'gregorian-interval/' + str(x)[0:4] + '-03-31T00:00:00/P1Y'
    
table['Period'] = table.apply(lambda row: user_perc(row['Year']), axis = 1)
# -

table['WG Geography'] = table['WG Geography'].apply(pathify)

table['Unit'] = table['Unit'].apply(pathify)


# +
def user_perc1(x):
    if str(x) == 'stock' :
        return 'Count'
    else:
        return 'GBP Total'
    
table['Measure Type'] = table.apply(lambda row: user_perc1(row['Unit']), axis = 1)
# -


table['Social Housing Accommodation'] = table['Social Housing Accommodation'].astype(str)
table['Social Housing Accommodation'] = table['Social Housing Accommodation'].map(lambda cell: cell.replace('.0', ''))

table['Social Housing Accommodation'] = table['Social Housing Accommodation'].apply(pathify)
table['Social Housing Accommodation'] = table['Social Housing Accommodation'].map(
    lambda x: {
        '2-1' : '5', 
        '2-2' : '6',
        '4-1': '7' }.get(x, x))

table = table.drop('Year', axis = 1)

table = table[['WG Geography','Period','Social Housing Accommodation', 'Social Housing Bedrooms','Social Housing Provider','Social Housing Dwelling Type','Measure Type','Value','Unit']]

out = Path('out')
out.mkdir(exist_ok=True, parents=True)
table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'affordable-housing'
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
