#!/usr/bin/env python
# coding: utf-8

# In[64]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

year = int(right(str(datetime.datetime.now().year),2)) - 1

def temp_scrape(scraper, tree):
    scraper.dataset.title = 'Additional Affordable Homes Provided by Type of Scheme'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/847217/Live_Table_1000.xlsx'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-affordable-housing-supply')
scraper


# In[65]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if 'Live Table' in tab.name and right(tab.name,1) is not '0': #all data in 'Live Table 1000' is included in 'Live Table 1000C'
        
        cell = tab.filter("England")
        
        period = cell.shift(RIGHT).expand(RIGHT).is_not_blank()
        
        remove = tab.filter("Notes:").expand(RIGHT).expand(DOWN)
        
        tenure = cell.shift(0,2).expand(DOWN).is_not_blank().filter(contains_string("of which:")) | tab.filter(contains_string('All affordable'))
        
        scheme = cell.shift(0,2).expand(DOWN).is_not_blank() - tenure
        
        observations = cell.shift(1,2).expand(DOWN).expand(RIGHT).is_not_blank() - remove
        
        dimensions = [
                HDim(period, 'Period', DIRECTLY, ABOVE),
                HDimConst('Area', 'E92000001'),
                HDim(tenure, 'Tenure', CLOSEST, ABOVE),
                HDim(scheme, 'Scheme', CLOSEST, ABOVE),
                HDimConst('Measure Type','Count'),
                HDimConst('Unit','Dwellings'),
        ]
        
        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
        


# In[66]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')
df['Period'] = df['Period'].map(lambda x: 'gregorian-interval/' + left(x,4) + '-04-01T00:00:00/P1Y')

df.rename(columns={'OBS':'Value',
                   'DATAMARKER':'Marker'}, inplace=True)

df = df.replace({'Tenure' : { 
    'Affordable Home Ownership3, of which:' : 'Affordable Home Ownership', 
    'Affordable Rent, of which:' : 'Affordable Rent',
    'All affordable8' : 'All affordable', 
    'Intermediate Rent9, of which:' : 'Intermediate Rent',
    'London Affordable Rent, of which:' : 'London Affordable Rent', 
    'Shared Ownership3, of which:' : 'Shared Ownership',
    'Social Rent, of which:' : 'Social Rent', 
    'Unknown tenure, of which:' : 'Unknown tenure'},
                    'Scheme' : {
    '' : 'All', 
    'Affordable Housing Guarantees 2' : 'Affordable Housing Guarantees',
    'Local Authorities1 HE/GLA grant funded' : 'Local Authorities HE/GLA grant funded',
    'Local Authorities1 HE/GLA grant funded 3' : 'Local Authorities HE/GLA grant funded',
    'Non-Registered Providers1 HE funded' : 'Non-Registered Providers HE funded', 
    'Other 7' : 'Other',
    'Permanent Affordable Traveller Pitches 6 ' : 'Permanent Affordable Traveller Pitches',
    'Private Finance Initiative 5' : 'Private Finance Initiative',
    'Private Registered Providers1 HE/GLA funded' : 'Private Registered Providers HE/GLA funded',
    'Section 106 (nil grant) 4' : 'Section 106 (nil grant)', },
                    'Marker' : {
    '..' : 'not applicable'}})

for column in df:
    if column in ('Marker', 'Tenure', 'Scheme'):
        df[column] = df[column].map(lambda x: pathify(x))

from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[67]:


tidy = df[['Period','Area','Tenure','Scheme','Value','Marker','Measure Type','Unit']]
tidy.rename(columns={'Tenure':'MCHLG Tenure',
                     'Scheme':'MCHLG Scheme'}, inplace=True)
tidy


# In[68]:


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



