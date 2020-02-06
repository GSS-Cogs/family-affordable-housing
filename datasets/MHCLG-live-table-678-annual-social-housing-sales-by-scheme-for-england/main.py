#!/usr/bin/env python
# coding: utf-8

# In[3]:


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
    scraper.dataset.title = 'Annual Social Housing Sales by Scheme for England'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/850295/LT_678.xlsx'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government'
    scraper.dataset.description = 'The table provides statistics on the sales of social housing stock – whether owned by local authorities or private registered providers.'
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-social-housing-sales')
scraper


# In[12]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 678'))

    remove = cell.expand(DOWN).filter(contains_string('Notes')).shift(0,-2).expand(DOWN).expand(RIGHT)

    period = cell.shift(0,4).expand(DOWN).is_not_blank() - remove

    area = 'E92000001'
        
    scheme = cell.shift(0,2).expand(RIGHT).is_not_blank()
        
    scheme_type = cell.shift(0,3).expand(RIGHT).is_not_blank()

    observations = period.fill(RIGHT).is_not_blank()

    dimensions = [
        HDim(period, 'Period', DIRECTLY, LEFT),
        HDim(scheme, 'scheme', CLOSEST, LEFT),
        HDim(scheme_type, 'Scheme Type', DIRECTLY, ABOVE),
        HDimConst('Area', area),
        HDimConst('Measure Type', 'Count'),
        HDimConst('Unit', 'Dwellings')
        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[13]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x, 4))

df = df.replace({'scheme' : {
    'Private Registered Provider (PRP) Social Housing Sales6' : 'Private Registered Provider (PRP) Social Housing Sales',},
                'DATAMARKER' : {
    '..' : 'not available'
                },
                'Scheme Type' : {
    '(LA, Preserved and Voluntary 2) Right to Buy Sales' : 'Right to Buy Sales',
    '(Preserved and Voluntary 2,3) Right to Buy Sales' : 'Right to Buy Sales', 
    'Other Sales to tenants' : 'Other Sales', 
    'Sales to Private Sector 3,4' : 'Sales to Private Sector', 
    'Total1' : 'Total'
                }})

df.rename(columns={'OBS' : 'Value',
                   'DATAMARKER' : 'Marker',
                   'scheme' : 'MCHLG Scheme',
                   'Scheme Type' : 'MCHLG Scheme Type'}, inplace=True)

df.head(50)


# In[11]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[16]:


tidy = df[['Area','Period', 'MCHLG Scheme', 'MCHLG Scheme Type', 'Value', 'Marker', 'Measure Type', 'Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Scheme', 'MCHLG Scheme Type'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head(50)


# In[17]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        The total local authority social housing sales reported in this table differs slightly from the total sales by local authority reported in live table 682. The local authority data is this table is sourced from LAHS and DELTA, whereas the data in live table 682 is sourced entirely from LAHS.
        Does not include sales from one PRP to another PRP.
        Further information on other types of social housing sales (such as more detail at a local authority level and on Right to Buy), are available here-
        https://www.gov.uk/government/collections/social-housing-sales-including-right-to-buy-and-transfersections/social-housing-sales-including-right-to-buy-and-transfers
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




