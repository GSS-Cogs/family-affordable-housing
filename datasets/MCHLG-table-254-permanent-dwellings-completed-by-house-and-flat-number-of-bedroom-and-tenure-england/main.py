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

year = int(right(str(datetime.datetime.now().year),2)) - 1

scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building')
dist = scraper.distribution(title=lambda x: x.startswith('Table 254'))
scraper.dataset.title = dist.title
#scraper.dataset.description = 'Live tables on house building: new build dwellings completed, by house and flat, number of bedroom and tenure, England'    
dist


# In[4]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 254'))

    remove = tab.filter(contains_string('E-Mail'))

    period = cell.shift(0,3).expand(RIGHT).is_not_blank() - remove

    tenure = cell.shift(0,5).expand(DOWN).is_not_blank() - tab.filter(contains_string('Houses')) - tab.filter(contains_string('Flats'))  - remove
    
    Type = cell.shift(0,5).expand(DOWN).is_not_blank() - tenure - remove
    
    bedrooms = cell.shift(2,7).expand(DOWN).is_not_blank() - remove

    observations = bedrooms.fill(RIGHT).is_not_blank() - remove

    dimensions = [
            HDim(period, 'Period', DIRECTLY, ABOVE),
            HDim(bedrooms, 'Bedrooms', DIRECTLY, LEFT),
            HDim(tenure, 'Tenure', CLOSEST, ABOVE),
            HDim(Type, 'Type', CLOSEST, ABOVE),
            HDimConst('Measure Type', 'Percentage'),
            HDimConst('Unit', 'Percent'),
            HDimConst('Area', tab.name)
    ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[5]:


pd.set_option('display.float_format', lambda x: '%.0f' % x)
df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4))


df = df.replace({'Bedrooms' : {
    '1 bedroom' : 'One Bedroom', 
    '2 bedrooms' : 'Two Bedrooms', 
    '3 bedrooms' : 'Three Bedrooms', 
    '4 or more bedrooms' : 'Four or More Bedrooms'},
                 'Area' : {
    'East Midlands' : 'E12000004',
    'East of England' : 'E12000006', 
    'England' : 'E92000001', 
    'London' : 'E12000007', 
    'North East' : 'E12000001',
    'North West' : 'E12000002', 
    'South East' : 'E12000008', 
    'South West' : 'E12000009', 
    'West Midlands' : 'E12000005',
    'Yorkshire and the Humber' : 'E12000003'
                 }})


df.rename(columns={'Tenure' : 'MCHLG Tenure',
                   'Type' : 'Housing Type',
                   'OBS' : 'Value'}, inplace=True)

df.head(50)


# In[6]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[7]:


tidy = df[['Area','Period','MCHLG Tenure','Housing Type','Bedrooms','Value','Measure Type','Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Tenure', 'Housing Type','Bedrooms'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[8]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        Figures for 2001/02 onwards are based on just NHBC figures, so there is some degree of variability owing to partial coverage.
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




