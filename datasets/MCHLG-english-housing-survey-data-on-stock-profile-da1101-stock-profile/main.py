#!/usr/bin/env python
# coding: utf-8

# In[86]:


from gssutils import *
from databaker.framework import *
import pandas as pd
from gssutils.metadata import THEME
from gssutils.metadata import *
import datetime
from gssutils.metadata import Distribution, GOV
pd.options.mode.chained_assignment = None
import json

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]


info = json.load(open('info.json')) 
landingPage = info['dataURL'] 
landingPage 


# Note: 'sub-national area' has been omitted since one third of the data for this dimension is labelled as 'rest of England' which has no way to be translated into an Area Code.

# In[87]:


scraper = Scraper(landingPage) 
scraper.select_dataset(latest=True) 
dist = scraper.distribution(title=lambda x: x.startswith('DA1101'))
scraper.dataset.title = dist.title   
dist


# In[88]:


tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table DA1101'))

    remove = cell.expand(DOWN).filter(contains_string('Source:')).shift(0,-2).expand(DOWN).expand(RIGHT)

    period_year = tab.name
    
    tenure = cell.shift(1,3).expand(RIGHT)
        
    dwelling_detail = cell.shift(0,5).expand(DOWN) - remove
    
    observations = dwelling_detail.fill(RIGHT).is_not_blank()

    dwelling_headings = dwelling_detail - observations.shift(LEFT)
    
    dimensions = [
        HDimConst('Period', period_year),
        HDim(tenure, 'Tenure', DIRECTLY, ABOVE),
        HDim(dwelling_detail, 'Dwelling Detail', DIRECTLY, LEFT),
        HDim(dwelling_headings, 'Dwelling Headings', CLOSEST, ABOVE),
        HDimConst('Measure Type', 'Count'),
        HDimConst('Unit', 'Dwellings')
        ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[89]:


pd.set_option('display.float_format', lambda x: '%.0f' % x)

df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['OBS'] = df['OBS'] * 1000

df['Period'] = 'year/' + df['Period']

df['Occupancy Status'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'occupancy status' else 'All', axis = 1)
df['Dwelling Age'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'dwelling age' else 'All', axis = 1)
df['Dwelling Type'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'dwelling type' else 'All', axis = 1)
df['Dwelling Size'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'size' else 'All', axis = 1)
df['Area Type'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'area type' else 'All', axis = 1)
df['Deprived Local Areas'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'deprived local areas' else 'All', axis = 1)
df['Deprived Districts'] = df.apply(lambda x: x['Dwelling Detail'] if x['Dwelling Headings'] == 'deprived districts' else 'All', axis = 1)

df = df.drop(['Dwelling Detail', 'Dwelling Headings'], axis=1)

indexNames = df[ df['Tenure'].str.contains('floor area')].index
df.drop(indexNames, inplace = True)

indexNames = df[ df['Tenure'].str.contains('market value')].index
df.drop(indexNames, inplace = True)

indexNames = df[ df['Tenure'].str.contains('all dwellings')].index
df.drop(indexNames, inplace = True)

indexNames = df[ df['Tenure'].str.contains('sample size')].index
df.drop(indexNames, inplace = True)

df = df.replace({'Tenure' : {
    'all\nsocial' : 'All Social', 
    'all \nprivate' : 'All Private', 
    'housing\nassociation' : 'Housing Associations',
    'local\nauthority' : 'Local Authorities', 
    'owner\noccupied' : 'Owner Occupied', 
    'private\nrented' : 'Private Enterprise'},
                'Dwelling Size' : { #Check how to add note on Dwelling Size unit (M^2)
    '110m2 or more' : '110 or more', 
    '50 to 69m2' : '50-69', 
    '50-69m2' : '50-69', 
    '70 to 89m2' : '70-89', 
    '70-89m2' : '70-89',
    '90 to 109m2' : '90-109', 
    '90-109m2' : '90-109', 
    'less than 50m2' : 'less than 50'}, 
                'Deprived Local Areas' : {
    'least deprived 10% of areas' : 'least deprived 10%',
    'most deprived 10% of areas' : 'most deprived 10%'},
                'DATAMARKER' : {
    '*' : 'too small for reliable estimate',
    'u' : 'too small for reliable estimate'}})

df.rename(columns={'OBS' : 'Value',
                   'Tenure' : 'MCHLG Tenure',
                   'DATAMARKER' : 'Marker'}, inplace=True)

for column in df:
    if column in ('Marker', 'MCHLG Tenure','Occupancy Status','Dwelling Age','Dwelling Type','Dwelling Size','Area Type','Deprived Local Areas','Deprived Districts'):
        df[column] = df[column].map(lambda x: pathify(x))

df


# In[90]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[91]:


tables = {}
occ_status = df[['Period','MCHLG Tenure','Occupancy Status','Value','Marker','Measure Type','Unit']]
tables['Occupancy Status'] = occ_status
dwelling_age = df[['Period','MCHLG Tenure','Dwelling Age','Value','Marker','Measure Type','Unit']]
tables['Dwelling Age'] = dwelling_age
dwelling_type = df[['Period','MCHLG Tenure','Dwelling Type','Value','Marker','Measure Type','Unit']]
tables['Dwelling Type'] = dwelling_type
dwelling_size = df[['Period','MCHLG Tenure','Dwelling Size','Value','Marker','Measure Type','Unit']]
tables['Dwelling Size'] = dwelling_size
area_type = df[['Period','MCHLG Tenure','Area Type','Value','Marker','Measure Type','Unit']]
tables['Area Type'] = area_type
deprived_local_areas = df[['Period','MCHLG Tenure','Deprived Local Areas','Value','Marker','Measure Type','Unit']]
tables['Deprived Local Area'] = deprived_local_areas
deprived_districts = df[['Period','MCHLG Tenure','Deprived Districts','Value','Marker','Measure Type','Unit']]
tables['Deprived Districts'] = deprived_districts


# In[92]:


GROUP_ID = 'MCHLG-english-housing-survey-data-on-stock-profile-da1101-stock-profile'.lower()

for i in tables:
    
    tidy = tables.get(i)
    
    destinationFolder = Path('out')
    destinationFolder.mkdir(exist_ok=True, parents=True)

    TAB_NAME = pathify('English Housing Survey data on stock profile (DA1101: stock profile), ' + i)

    tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

    scraper.dataset.family = 'affordable-housing'
    
    if 'Dwelling Size' in i:
        scraper.dataset.comment = """
            Source: English Housing Survey, dwelling sample
            Dwelling Size values are in M^2 (Square metre)
            """
    elif 'Deprived Local Areas' in i:
        scraper.dataset.comment = """
            Source: English Housing Survey, dwelling sample
            Deprived Local Areas ranked in 10 Percentage groups, eg: 2nd relates to 10-20% most deprived area, 3rd to 20-30% most deprived etc.
            """
    else:
        scraper.dataset.comment = """
            Source: English Housing Survey, dwelling sample
            """
    
    scraper.dataset.title = 'English Housing Survey data on stock profile (DA1101: stock profile), ' + i
    scraper.set_dataset_id(f'gss_data/affordable-housing/{GROUP_ID}/{TAB_NAME}')  

    with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
        metadata.write(scraper.generate_trig())

    csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
    csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
    tidy


# In[ ]:




