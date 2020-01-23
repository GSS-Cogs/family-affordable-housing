#!/usr/bin/env python
# coding: utf-8

# In[43]:


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
    scraper.dataset.title = 'Dwelling stock estimates'
    scraper.dataset.publisher = 'Ministry of Housing, Communities & Local Government'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/814669/LT_100.xls'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    return

scrapers.scraper_list = [('https://www.gov.uk/government/collections/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/collections/dwelling-stock-including-vacants')
scraper


# In[44]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    if '2009' not in tab.name and '2010' in tab.name or '2011' in tab.name:
        #2009 removed as ONS codes are out of date, and data is therefore excluded until we decide on a replacement/fix for all the codes.
        print(tab.name)
        emailLoc = tab.filter('Latest update').shift(-3,0)

        email = right(str(emailLoc), len(str(emailLoc)) - str(emailLoc).find(':') - 2)[:-3]
        print(email)
        scraper.dataset.contactPoint = email

        year = tab.name

        cell = tab.filter("ONS code")

        remove = tab.filter("Sources:").expand(RIGHT).expand(DOWN)

        observations = cell.shift(5,1).expand(RIGHT).expand(DOWN).is_not_blank() - remove

        area = cell.expand(DOWN).is_not_blank() | tab.excel_ref('C').filter("ENGLAND").assert_one().shift(-2,0) - remove

        dwellings = cell.shift(5,0).expand(RIGHT).is_not_blank()

        dimensions = [
                HDimConst('Year', year),
                HDim(area, 'Area', DIRECTLY, LEFT, cellvalueoverride={"": "E92000001"}),
                HDim(dwellings, 'Dwellings', DIRECTLY, ABOVE),
                HDimConst('Measure Type','Count'),
                HDimConst('Unit','Dwellings'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())
    elif '2009' not in tab.name:
        print(tab.name)
        if '2018' not in tab.name:
            emailLoc = tab.filter('Latest update').shift(-3,-1)
        else:
            emailLoc = tab.filter('Latest update').shift(0,-2)

        email = right(str(emailLoc), len(str(emailLoc)) - str(emailLoc).find(':') - 2)[:-3]
            
        print(email)

        scraper.dataset.contactPoint = email

        year = tab.name

        cell = tab.filter("DCLG code").shift(RIGHT)

        area = cell.expand(DOWN).is_not_blank()
        
        if '2018' not in tab.name:
            observations = cell.shift(4,1).expand(RIGHT).expand(DOWN).is_not_blank() & area.fill(RIGHT)
        else:
            remove = tab.filter('Isles of Scilly').expand(RIGHT)
            observations = cell.shift(4,1).expand(RIGHT).expand(DOWN).is_not_blank() & area.fill(RIGHT) - remove

        dwellings = cell.shift(4,0).expand(RIGHT).is_not_blank()

        dimensions = [
                HDimConst('Year', year),
                HDim(area, 'Area', DIRECTLY, LEFT),
                HDim(dwellings, 'Dwellings', DIRECTLY, ABOVE),
                HDimConst('Measure Type','Count'),
                HDimConst('Unit','Dwellings'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)
        savepreviewhtml(tidy_sheet, fname="Preview.html")

        tidied_sheets.append(tidy_sheet.topandas())


# In[45]:


df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')
df['Period'] = 'gregorian-interval/' + df['Year'] + '-04-01T00:00:00/P1Y'
df.rename(columns={'OBS':'Value',
                   'DATAMARKER':'Marker'}, inplace=True)
df


# In[46]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)


# In[47]:


tidy = df[['Period','Area','Dwellings','Value','Marker','Measure Type','Unit']]

tidy = tidy.replace({'Dwellings' : { 
    'Local Authority (incl. owned by other LAs)' : 'Local Authority',
    'Local Authority (incl. owned by other LAs) (R)' : 'Local Authority', 
    'Other public sector (P R)1' : 'Other Public Sector', 
    'Private sector (P R)1' : 'Private Sector', 
    'Private sector (P)1' : 'Private Sector', 
    'Private sector (R)1' : 'Private Sector',
    'Total (P)1' : 'Total', 
    'Total (R)1' : 'Total', 
    'Total 1' : 'Total'},
                    'Marker' : {
    '.' : 'not-available'}})

tidy['Dwellings'] = tidy['Dwellings'].map(lambda x: pathify(x))
tidy


# In[48]:


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

