#!/usr/bin/env python
# coding: utf-8

# In[17]:


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
    scraper.dataset.title = 'Permanent dwellings started and completed, by tenure, England (quarterly seasonally adjusted)'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/861410/LiveTable222.xlsx'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government'
    scraper.dataset.description = 'Live tables on house building: new build dwellings started and completed, by tenure, England (quarterly seasonally adjusted).'
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building')
scraper


# In[18]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 222'))

    remove = cell.expand(DOWN).filter(contains_string('1. ')).expand(RIGHT).expand(DOWN)

    year = cell.shift(0,5).expand(DOWN).is_not_blank() - remove

    period = cell.shift(1,5).expand(DOWN).is_not_blank()

    completions = cell.shift(4,3).expand(RIGHT).is_not_blank()

    tenure = completions.shift(-1,1).expand(RIGHT).is_not_blank()

    observations = tenure.shift(DOWN).fill(DOWN).is_not_blank() - remove

    dimensions = [
            HDim(year, 'Year', CLOSEST, ABOVE),
            HDim(period, 'Period', DIRECTLY, LEFT),
            HDim(tenure, 'Tenure', DIRECTLY, ABOVE),
            HDim(completions, 'Completions', CLOSEST, LEFT),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Dwellings')
    ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[19]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')


df = df.replace({'Completions' : {
    'Completed': 'Completions', 
    'Started' : 'Starts'},
                'Tenure' : {
    'All\nDwellings' : 'All Dwellings'},
                'DATAMARKER' : {
    '-' : 'Less than five'}})

df['Period'] = df.apply(lambda x: 'quarter/' + left(x['Year'],4) + '-' + x['Period'] if 'Q' in x['Period'] else 'year/' + left(x['Year'],4), axis = 1)

df = df.drop(['Year'], axis=1)

df['Area'] = 'E92000001'

df.rename(columns={'Completions' : 'MCHLG Completions',
                   'Tenure' : 'MCHLG Tenure',
                   'DATAMARKER' : 'Marker',
                   'OBS' : 'Value'}, inplace=True)

df#.head()


# In[20]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[21]:


tidy = df[['Area','Period','MCHLG Tenure','MCHLG Completions','Value','Marker','Measure Type','Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure', 'MCHLG Completions'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[22]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        Seasonally adjusted estimates are not constrained to unadjusted financial year totals. Seasonal factors for the house building time series are re-calculated annually back to 1990. This is usually done in the second quarter of the calendar year.  Therefore the seasonally adjusted house building figures throughout the whole period change slightly at that time.
        Local authorities series is seasonally adjusted to December 1992 only
        For detailed definitions of all tenures, see Definitions of housing terms in Housing Statistics home page
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




