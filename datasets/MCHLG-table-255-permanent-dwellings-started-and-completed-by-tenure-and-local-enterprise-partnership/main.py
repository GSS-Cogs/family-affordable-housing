#!/usr/bin/env python
# coding: utf-8

# In[58]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None
import inspect

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

year = int(right(str(datetime.datetime.now().year),2)) - 1

def temp_scrape(scraper, tree):
    scraper.dataset.title = 'Permanent Dwellings Started and Completed, by Tenure and Local Enterprise Partnership'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/861416/LiveTable255.xlsx'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government'
    scraper.dataset.description = 'Live tables on house building: new build dwellings started and completed, by tenure and local enterprise partnership.'
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building')
scraper


# In[59]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 255'))

    remove = tab.filter(contains_string('List of the local authorities')).expand(RIGHT).expand(DOWN)

    period = tab.name
    
    completions = cell.shift(2,4).expand(RIGHT).is_not_blank().is_not_blank()

    tenure = cell.shift(2,5).expand(RIGHT).is_not_blank().is_not_blank()
    
    area = cell.shift(0,5).fill(DOWN).is_not_blank().is_not_whitespace() - remove

    observations = area.fill(RIGHT).is_not_blank().is_not_whitespace()

    dimensions = [
            HDimConst('Period', period),
            HDim(completions, 'Completions', CLOSEST, LEFT),
            HDim(tenure, 'Tenure', DIRECTLY, ABOVE),
            HDim(area, 'Area', DIRECTLY, LEFT),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Dwellings')
    ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[60]:


pd.set_option('display.float_format', lambda x: '%.0f' % x)
df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4))

df['Completions'] = df.apply(lambda x: 'Completions' if 'Private' in x['Tenure'] and ' ' in x['Completions'] else x['Completions'], axis = 1)
df['Completions'] = df.apply(lambda x: 'Completions' if 'completed' in str(x['Completions']).lower() else x['Completions'], axis = 1)
df['Completions'] = df.apply(lambda x: 'Starts' if 'start' in x['Completions'] else x['Completions'], axis = 1)
df['Completions'] = df.apply(lambda x: 'Starts' if x['Completions'] == '' else x['Completions'], axis = 1)

df = df.replace({'Tenure' : {
    'All' : 'All Tenures', 
    'Local\nAuthority' : 'Local Authorities',
    'Private\nEnterprise' : 'Private Enterprise'},
                 'Area' : {
    'Black Country' : 'E37000001', 
    'Buckinghamshire Thames Valley' : 'E37000002',
    'Cheshire and Warrington' : 'E37000003', 
    'Coast to Capital' : 'E37000004',
    'Cornwall and the Isles of Scilly' : 'E37000005', 
    'Coventry and Warwickshire' : 'E37000006',
    'Cumbria' : 'E37000007', 
    'Derby, Derbyshire, Nottingham and Nottinghamshire' : 'E37000008',
    'Dorset' : 'E37000009', 
    'England4' : 'E92000001', 
    'Enterprise M3' : 'E37000010', 
    'Gloucestershire' : 'E37000011',
    'Greater Birmingham and Solihull' : 'E37000012',
    'Greater Cambridge & Greater Peterborough' : 'E37000042', 
    'Greater Lincolnshire' : 'E37000014',
    'Greater Manchester' : 'E37000015', 
    'Heart of the South West' : 'E37000016', 
    'Hertfordshire' : 'E37000017',
    'Humber' : 'E37000018', 
    'Lancashire' : 'E37000019', 
    'Leeds City Region' : 'E37000020',
    'Leicester and Leicestershire' : 'E37000021', 
    'Liverpool City Region' : 'E37000022', 
    'London' : 'E37000023',
    'New Anglia' : 'E37000024', 
    'North Eastern' : 'E37000025', 
    'Northamptonshire' : 'E37000026', 
    'Oxfordshire LEP' : 'E37000027',
    'Sheffield City Region' : 'E37000040', 
    'Solent' : 'E37000029', 
    'South East' : 'E37000030', 
    'South East Midlands' : 'E37000041',
    'South East Midlands5' : 'E37000041', 
    'Stoke-on-Trent and Staffordshire' : 'E37000032',
    'Swindon and Wiltshire' : 'E37000033', 
    'Tees Valley' : 'E37000034', 
    'Thames Valley Berkshire' : 'E37000035',
    'The Marches' : 'E37000036', 
    'West of England' : 'E37000037', 
    'Worcestershire' : 'E37000038',
    'York and North Yorkshire' : 'E37000039'}})


df.rename(columns={'Tenure' : 'MCHLG Tenure',
                   'Completions' : 'MCHLG Completions',
                   'OBS' : 'Value'}, inplace=True)

df.head(50)


# In[61]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[62]:


tidy = df[['Area','Period','MCHLG Tenure','MCHLG Completions','Value','Measure Type','Unit']]

for column in tidy:
    if column in ('MCHLG Tenure', 'MCHLG Completions'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head()


# In[63]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        Figures are rounded to the nearest 10, 0 represents the range 0 - 4. Totals may not equal the sum of the component parts due to rounding to the nearest 10.        
        
        For detailed definitions of all tenures, see definitions of housing terms on Housing Statistics
        Where local authorities are overlapped by two LEPs, they have been included in both LEPs calculations, meaning the England total will not equal the sum of all LEPs.
        National figures are published DCLG housebuilding statistics. England figures include estimates for missing returns.
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




