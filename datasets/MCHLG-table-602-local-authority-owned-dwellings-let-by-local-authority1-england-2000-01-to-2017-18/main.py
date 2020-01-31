#!/usr/bin/env python
# coding: utf-8

# In[92]:


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
    scraper.dataset.title = 'Local authority owned dwellings let by local authority, England'
    dist = Distribution(scraper)
    dist.title = 'A distribution'
    dist.downloadURL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/861106/Live_Table_602.xlsx'
    dist.mediaType = Excel
    scraper.distributions.append(dist)
    scraper.dataset.publisher = 'https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government'
    scraper.dataset.description = 'This is one of 6 tables from the live tables on rents, lettings and tenancies'
    return

scrapers.scraper_list = [('https://www.gov.uk/government/statistical-data-sets/', temp_scrape)]
scraper = Scraper('https://www.gov.uk/government/statistical-data-sets/live-tables-on-rents-lettings-and-tenancies')
scraper


# In[93]:


dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())

tidied_sheets = []

for tab in tabs:
    
    cell = tab.filter(contains_string('Table 602'))

    remove = tab.filter(contains_string('Source:')).expand(DOWN).expand(RIGHT)

    period = cell.shift(0,4).expand(DOWN).is_not_blank() - remove

    lets = cell.shift(1,4).expand(RIGHT).is_not_blank()
    
    observations = period.fill(RIGHT).is_not_blank()

    dimensions = [
            HDim(period, 'Period', DIRECTLY, LEFT),
            HDim(lets, 'Lets', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Dwellings'),
            HDimConst('Area', 'E92000001'),
            HDimConst('MCHLG Provider', 'Local Authority')
    ]

    tidy_sheet = ConversionSegment(tab, dimensions, observations)
    savepreviewhtml(tidy_sheet, fname="Preview.html")

    tidied_sheets.append(tidy_sheet.topandas())
        


# In[94]:


pd.set_option('display.float_format', lambda x: '%.1f' % x)
df = pd.concat(tidied_sheets, ignore_index = True, sort = False).fillna('')

df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4))


df = df.replace({'Lets' : {
    'Existing lets3' : 'Existing lets', 
    'Mutual exchanges4' : 'Mutual exchanges', 
    'New lets2' : 'New lets', 
    'Total lets5' : 'Total lets',
    'Total lets as % of LA stock (at year end)' : 'Total of stock (at year end)'}})

df.rename(columns={'OBS' : 'Value'}, inplace=True)

df['Value'] = df.apply(lambda x: x * 100 if x['Lets'] == 'Total of stock (at year end)' else x, axis = 1)
df['Value'] = df.apply(lambda x: left(str(x['Value']), len(str(x['Value'])) - 2) if x['Lets'] != 'Total of stock (at year end)' else x['Value'], axis = 1)

df['Measure Type'] = df.apply(lambda x: 'Percentage' if 'Total of stock (at year end)' in x['Lets'] else x['Measure Type'], axis = 1)
df['Unit'] = df.apply(lambda x: 'Percent' if 'Total of stock (at year end)' in x['Lets'] else x['Unit'], axis = 1)

df.head()


# In[95]:


from IPython.core.display import HTML
for col in df:
    if col not in ['Value']:
        df[col] = df[col].astype('category')
        display(HTML(f"<h2>{col}</h2>"))
        display(df[col].cat.categories)    


# In[96]:


tidy = df[['Area','Period', 'MCHLG Provider','Lets','Value','Measure Type','Unit']]

for column in tidy:
    if column in ('Marker', 'MCHLG Provider', 'Lets'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))

tidy.head(200)


# In[97]:


destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

TAB_NAME = 'observations'

tidy.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

scraper.dataset.family = 'affordable-housing'
scraper.dataset.comment = """
        Source: \n Local Authority Housing Statistics, or it predecessors, Housing Strategy Statistical Appendix (HSSA) and the Housing Investment Programme (HIP) returns. \n\n
        The decreasing number of lettings is associated with local authorities transferring their stock to private registered providers (PRPs) through large scale voluntary transfers (LSVT), Right to Buy (RTB) and other sales, and demolitions. Information was collected from 2009-10 using questions which had been restructured from questions asked in previous years. As a result the quality of data is less certain for 2009-10. \n\n
        A new social tenant is one that was not living in a social housing dwelling (whether owned or managed by your local authority or another social landlord) immediately prior to the letting of the dwelling owned by a local authority.  \n\n
        An existing social tenant is one which immediately before the current let had a secure, assured, flexible, fixed term, introductory, starter, demoted or family intervention tenancy (this list includes terms which are used inter-changeable for the same tenancy type). \n\n
        A mutual exchange tenant is one who swaps dwellings with another social tenant. \n\n
        Totals may not equal the sum of components because of rounding (to the nearest 100). \n\n
        """

with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())

csvw = CSVWMetadata('https://gss-cogs.github.io/family-affordable-housing/reference/')
csvw.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')
tidy


# In[ ]:




