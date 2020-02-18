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

scraper = Scraper('https://statswales.gov.wales/Catalogue/Housing/Social-Housing-Sales/totalsocialhousingsales-by-period-providertype',
                  session=CacheControl(Session(),
                                       cache=FileCache('.cache'),
                                       heuristic=ExpiresAfter(days=7)))
scraper
# -

if len(scraper.distributions) == 0:
    from gssutils.metadata import Distribution
    dist = Distribution(scraper)
    dist.title = 'Dataset'
    dist.downloadURL = 'http://open.statswales.gov.wales/dataset/hous0901'
    dist.mediaType = 'application/json'
    scraper.distributions.append(dist)
table = scraper.distribution(title='Dataset').as_pandas()
table

table.columns

# Columns selected based on tidy data requirements

# +
cols = {
    'Area_AltCode1': 'WG Geography',
    'Activity_Code': 'Social Landlord Housing Sales Activity',
    'Data': 'Value',
    'Period_Code': 'Year', 
    'Provider_Code': 'Social Landlord Housing Sales Provider',
    
}
to_remove = set(table.columns) - set(cols.keys())
table.rename(columns=cols, inplace=True)
table.drop(columns=to_remove, inplace=True)
table
# -

# The OData API offers an "Items" endpoint that enumerates the values of the various dimensions and provides information about the hierarchy.

try:
    items_dist = scraper.distribution(title='Items')
except:
    from gssutils.metadata import Distribution
    dist = Distribution(scraper)
    dist.title = 'Items'
    dist.downloadURL = 'http://open.statswales.gov.wales/dataset/hous0901'
    dist.mediaType = 'application/json'
    scraper.distributions.append(dist)
    items_dist = scraper.distribution(title='Items')
items = items_dist.as_pandas()
items

# +
from collections import OrderedDict
item_cols = OrderedDict([
    ('Description_ENG', 'Label'),
    ('Code', 'Notation'),
    ('Hierarchy', 'Parent Notation'),
    ('SortOrder', 'Sort Priority')
])

def extract_codelist(dimension):
    codelist = items[items['DimensionName_ENG'] == dimension].rename(
        columns=item_cols).drop(
        columns=set(items.columns) - set(item_cols.keys()))[list(item_cols.values())]
    codelist['Notation'] = codelist['Notation'].map(
        lambda x: str(int(x)) if str(x).endswith(".0") else str(x)
    )
    return codelist

codelists = {
    'Social Landlord Housing Sales Provider': extract_codelist('Provider'),
    'Social Landlord Housing Sales Activity': extract_codelist('Activity')
}

out = Path('out')
out.mkdir(exist_ok=True, parents=True)

for name, codelist in codelists.items():
    codelist.to_csv(out / f'{name}.csv', index = False)
    display(name)
    display(codelist)
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

table['Measure Type'] = 'Count'
table['Unit'] = 'housing-sales'


table = table.drop('Year', axis = 1)

table = table[['WG Geography','Period','Social Landlord Housing Sales Activity', 'Social Landlord Housing Sales Provider','Measure Type','Value','Unit']]

table.drop_duplicates().to_csv(out / 'observations.csv', index = False)

scraper.dataset.family = 'affordable-housing'
with open(out / 'observations.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(out / 'observations.csv', out / 'observations.csv-schema.json')
