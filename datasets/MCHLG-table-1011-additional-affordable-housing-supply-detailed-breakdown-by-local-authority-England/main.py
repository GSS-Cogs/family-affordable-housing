#!/usr/bin/env python
# coding: utf-8

# In[28]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

year = int(right(str(datetime.datetime.now().year),2)) - 1

def temp_scrape(scraper, tree):
    scraper.dataset.title = 'Additional affordable housing supply, detailed breakdown by local authority'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/847659/Live_Table_1011.xlsx'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government'
    scraper.dataset.description = 'Affordable housing supply statistics (AHS) 2017-18'
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-affordable-housing-supply')
scraper


# In[29]:


dist = scraper.distributions[0]
#tabs = (t for t in dist.as_pandas(sheet_name = 'data'))
df = dist.as_pandas(sheet_name = 'data')

df.head()


# In[38]:


tidy = df[['LA code','Year','Tenure','Completions','LT1000','Units']]

tidy.rename(columns={'LA code' : 'Area',
                     'Year' : 'Period',
                     'Completions' : 'MCHLG Scheme Type',
                     'Tenure' : 'MCHLG Tenure',
                     'LT1000' : 'MCHLG Scheme',
                     'Units' : 'Value'}, inplace=True)

tidy['Period'] = tidy['Period'].map(lambda x: 'gregorian-interval/' + left(x,4) + '-04-01T00:00:00/P1Y')
tidy['MCHLG Scheme Type'] = tidy['MCHLG Scheme Type'].map(lambda x: 'Completions' if 'Y' in x else 'Starts')
tidy['Measure Type'] = 'Count'
tidy['Unit'] = 'Dwellings'

tidy = tidy.replace({'MCHLG Scheme' : {
    'Right to Buy recycled receipts' : 'Right  To  Buy  Additions  With  Recycled  Receipts',
    's106 nil grant' : 'Section  106  Nil  Grant',
    's106 part grant' : 'Section  106  Partial  Grant',
    'Private Registered Provider HE/GLA funded' : 'Private Registered Providers HE/GLA funded',
    'Private Registered Provider other funding' : 'Private Registered Providers other funding',
    'Affordable Homes Guarantees' : 'Affordable Housing Guarantees',
    'Local Authority HE/GLA funded' : 'Local  Authorities  He/Gla  Grant  Funded',
    'Local Authority other funding' : 'Local  Authorities  Other  Funding',
    'Non-Registered Provider HE funded' : 'Non  Registered  Providers  He  Funded'},
                'MCHLG Tenure' : {
    'Unknown' : 'Unknown Tenure'
                }})

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure', 'MCHLG Scheme', 'MCHLG Scheme Type'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[39]:


from IPython.core.display import HTML
for col in tidy:
    if col not in ['Value']:
        tidy[col] = tidy[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(tidy[col].cat.categories)    


# In[40]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:



