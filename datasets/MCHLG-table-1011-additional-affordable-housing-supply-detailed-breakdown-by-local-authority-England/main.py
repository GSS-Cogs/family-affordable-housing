#!/usr/bin/env python
# coding: utf-8

# In[13]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV

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


# In[ ]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if '1011' in tab.name:
        
        print(tab.name)
        
        cell = tab.filter("Row Labels")
        
        period = cell.fill(RIGHT).is_not_blank() - cell.fill(RIGHT).filter('Grand Total')
        
        tenure = cell.fill(DOWN).is_not_blank().filter(contains_string("Rent")) | tab.filter(contains_string('Shared Ownership')) | tab.filter(contains_string('Affordable Home Ownership')) | tab.filter(contains_string('Affordable Home Ownership')) | tab.filter('Unknown') | tab.filter(contains_string('Grand Total'))
                
        scheme = cell.fill(DOWN).is_not_blank() - tenure
        
        if 'C' in tab.name:
            scheme_type = 'Completions'
        elif 'S' in tab.name:
            scheme_type = 'Starts'
        else:
            scheme_type = 'ERROR'
        
        observations = cell.shift(1,2).expand(DOWN).expand(RIGHT).is_not_blank() - cell.fill(RIGHT).filter('Grand Total').fill(DOWN) - tenure.expand(RIGHT)
        
        dimensions = [
                HDim(period, 'Period', DIRECTLY, ABOVE),
                HDimConst('Area', 'E92000001'),
                HDim(tenure, 'Tenure', CLOSEST, ABOVE),
                HDim(scheme, 'Scheme', CLOSEST, ABOVE),
                HDimConst('Scheme Type', scheme_type),
                HDimConst('Measure Type', 'Count'),
                HDimConst('Unit', 'Dwellings')
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
        


# In[ ]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')
df['Period'] = df['Period'].map(lambda x: 'gregorian-interval/' + left(x,4) + '-04-01T00:00:00/P1Y')
df['OBS'] = df['OBS'].map(lambda x: int(x))

df.rename(columns={'OBS':'Value'}, inplace=True)

df = df.replace({'Scheme' : {
    'Right to Buy recycled receipts' : 'Right  To  Buy  Additions  With  Recycled  Receipts',
    's106 nil grant' : 'Section  106  Nil  Grant',
    's106 part grant' : 'Section  106  Partial  Grant',
    'Private Registered Provider HE/GLA funded' : 'Private Registered Providers HE/GLA funded',
    'Private Registered Provider other funding' : 'Private Registered Providers other funding',
    'Affordable Homes Guarantees' : 'Affordable Housing Guarantees',
    'Local Authority HE/GLA funded' : 'Local  Authorities  He/Gla  Grant  Funded',
    'Local Authority other funding' : 'Local  Authorities  Other  Funding',
    'Non-Registered Provider HE funded' : 'Non  Registered  Providers  He  Funded'}})

for column in df:
    if column in ('Marker', 'Tenure', 'Scheme', 'Scheme Type'):
        df[column] = df[column].map(lambda x: pathify(x))

from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    
df


# In[ ]:


tidy = df[['Period','Area','Tenure','Scheme','Scheme Type','Value','Measure Type','Unit']]
tidy.rename(columns={'Tenure':'MCHLG Tenure',
                     'Scheme':'MCHLG Scheme',
                     'Scheme Type' : 'MCHLG Scheme Type'}, inplace=True)
tidy


# In[ ]:


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




