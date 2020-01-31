#!/usr/bin/env python
# coding: utf-8

# In[117]:


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

def mid(s, offset, amount):
    return s[offset:offset+amount]

def temp_scrape(scraper, tree):
    scraper.dataset.title = 'Vacant dwellings by local authority district, England'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/784593/LT_615.xls'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government'
    scraper.dataset.description = 'This table brings together figures on vacant dwellings in England at local authority district level drawn from several separately published sources, as at 11 March 2018 and previous years.'
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-dwelling-stock-including-vacants')
scraper


# In[118]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if 'Notes' not in tab.name:
    
        cell = tab.filter(contains_string('Table 615'))

        remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(DOWN).expand(RIGHT)

        period_year = cell.shift(5,5).expand(RIGHT).is_not_blank()

        period_start = cell.shift(0,3).expand(RIGHT).is_not_blank() | cell.shift(0,4).expand(RIGHT).is_not_blank()

        area = cell.shift(2,11).expand(DOWN).is_not_blank() | tab.filter('ENGLAND') - remove

        observations = area.shift(2,0).fill(RIGHT) & period_year.expand(DOWN)

        if 'All vacants' in tab.name or 'All long-term vacants' in tab.name:
            dimensions = [
                    HDim(period_year, 'Period Year', DIRECTLY, ABOVE),
                    HDim(period_start, 'Period Start', DIRECTLY, ABOVE),
                    HDim(area, 'Area', DIRECTLY, LEFT),
                    HDimConst('Measure Type', 'Count'),
                    HDimConst('Unit', 'Dwellings'),
                    HDimConst('Dwellings', tab.name)
            ]
        else:
            dimensions = [
                HDim(period_year, 'Period Year', DIRECTLY, ABOVE),
                HDim(period_start, 'Period Start', CLOSEST, LEFT),
                HDim(area, 'Area', DIRECTLY, LEFT),
                HDimConst('Measure Type', 'Count'),
                HDimConst('Unit', 'Dwellings'),
                HDimConst('Dwellings', tab.name)
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
        


# In[119]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['Period'] = df.apply(lambda x: 'gregorian-interval/' + x['Period Start'] + 'T00:00:00/P1Y' if mid(x['Period Start'], 4, 1) == '-' else x['Period Start'], axis = 1)
df['Period'] = df.apply(lambda x: 'gregorian-interval/' + left(x['Period Year'], 4) + '-04-01T00:00:00/P1Y' if 'April' in x['Period Start'] else ('gregorian-interval/' + left(x['Period Year'], 4) + '-03-31T00:00:00/P1Y' if 'March' in x['Period Start'] else x['Period']), axis = 1)

df['DATAMARKER'] = df.apply(lambda x: '..' if x['OBS'] == '' else x['DATAMARKER'], axis = 1)

df = df.drop(['Period Start', 'Period Year'], axis=1)

df = df.replace({'Area' : {
    'ENGLAND' : 'E92000001'},
                'DATAMARKER' : {
    '..' : 'not applicable or not reported'
                }})

df.rename(columns={'OBS' : 'Value',
                   'DATAMARKER' : 'Marker',
                   'Dwellings' : 'MCHLG Tenure'}, inplace=True)

indexNames = df[ (df['Area'] == 'E06000053') & (df['Value'] == '') ].index
df.drop(indexNames, inplace = True)

df.head(50)


# In[120]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[121]:


tidy = df[['Area','Period', 'MCHLG Tenure','Value','Marker','Measure Type','Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head(200)


# In[122]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        The guidance notes which accompanied the data collection for 2017-2018, and which give details on what should be included in the data, can be found at the following link. https://www.gov.uk/government/publications/completing-local-authority-housing-statistics-2017-to-2018-guidance-notes
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




