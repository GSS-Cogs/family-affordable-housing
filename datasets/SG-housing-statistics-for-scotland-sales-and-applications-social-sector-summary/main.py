#!/usr/bin/env python
# coding: utf-8
# %% [markdown]
# ## Housing Statistics for Scotland - Sales and applications - social sector summary

# %%
from gssutils import *
from gssutils.metadata import THEME
scraper = Scraper('https://www2.gov.scot/Topics/Statistics/Browse/Housing-Regeneration/HSfS/SalesApplications')
scraper


# %%
dist = scraper.distributions[0]
tabs = (t for t in dist.as_databaker())
tidied_sheets = []

# %%
for tab in tabs:
    
    if 'tsScotSalesSummary' in tab.name:
        
        remove1 = tab.excel_ref('A26').expand(DOWN).expand(RIGHT)
        period = tab.excel_ref('A4').expand(DOWN).is_not_blank() - remove1
        public_authority_type = tab.excel_ref('B3').expand(RIGHT)
        local_authority_type = tab.excel_ref('B4').expand(RIGHT)
        type_of_sale_application = tab.excel_ref('B2').expand(RIGHT)
        observations = local_authority_type.fill(DOWN).is_not_blank() - remove1

        dimensions = [
            HDim(period, 'Period', DIRECTLY, LEFT),
            HDim(public_authority_type, 'Public Authority Type', DIRECTLY, ABOVE),
            HDim(local_authority_type, 'Local Authority Type', DIRECTLY, ABOVE),
            HDim(type_of_sale_application, 'Sales or Application Type', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Sales'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        savepreviewhtml(tidy_sheet, fname="Preview.html")
        tidied_sheets.append(tidy_sheet.topandas())
    
    if 'tsScotAppsSummary' in tab.name: 
        
        remove1 = tab.excel_ref('A26').expand(DOWN).expand(RIGHT)
        period = tab.excel_ref('A4').expand(DOWN).is_not_blank() - remove1
        public_authority_type = tab.excel_ref('B3').expand(RIGHT)
        local_authority_type = tab.excel_ref('B4').expand(RIGHT)
        type_of_sale_application = tab.excel_ref('B2').expand(RIGHT)
        observations = local_authority_type.fill(DOWN).is_not_blank() - remove1
        
        dimensions = [
            HDim(period, 'Period', DIRECTLY, LEFT),
            HDim(public_authority_type, 'Public Authority Type', DIRECTLY, ABOVE),
            HDim(local_authority_type, 'Local Authority Type', DIRECTLY, ABOVE),
            HDim(type_of_sale_application, 'Sales or Application Type', DIRECTLY, ABOVE),
            HDimConst('Measure Type', 'Count'),
            HDimConst('Unit', 'Applications'),
        ]

        tidy_sheet = ConversionSegment(tab, dimensions, observations)        
        savepreviewhtml(tidy_sheet, fname="Preview2.html")
        tidied_sheets.append(tidy_sheet.topandas())

# %%
df = pd.concat(tidied_sheets, ignore_index = True, sort = False)


# %%
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

df.rename(columns={'OBS' : 'Value','DATAMARKER' : 'Marker'}, inplace=True)
df['Period'] = df['Period'].map(lambda x: 'year/' + left(x,4))

f1=((df['Local Authority Type'] =='right to buy (modernised terms)') | 
    (df['Local Authority Type'] == 'voluntary sales')| 
    (df['Local Authority Type'] == 'rent to mortgage')|
    (df['Public Authority Type'] == 'Scottish Homes')| 
    (df['Public Authority Type'] == 'Housing association')| 
    (df['Public Authority Type'] == 'Total')) & (df['Unit']=='Sales')
df.loc[f1,'Sales or Application Type'] = 'Sales to sitting tenants'


f2=((df['Local Authority Type'] =='right to buy (modernised terms)') | 
    (df['Local Authority Type'] == 'rent to mortgage')| 
    (df['Local Authority Type'] == 'voluntary sales'))
df.loc[f2,'Public Authority Type'] = 'Local authority'

#  Sitting tenants sales include right to buy (old terms), right to buy (modernised terms from 2003 q4 onwards) and rent to mortgage (discontinued from January 2003)
f3=((df['Local Authority Type'] =='rent to mortgage') & (df['Unit']=='Sales') 
    & ((df['Period']=='year/2004')|(df['Period']=='year/2005')|(df['Period']=='year/2006')| 
       (df['Period']=='year/2007')|(df['Period']=='year/2008')|(df['Period']=='year/2009')| 
       (df['Period']=='year/2010')|(df['Period']=='year/2011')|(df['Period']=='year/2012')| 
       (df['Period']=='year/2013')|(df['Period']=='year/2014')|(df['Period']=='year/2015')|
       (df['Period']=='year/2016')|(df['Period']=='year/2017')|(df['Period']=='year/2018')))
df.loc[f3,'Marker'] = 'Discontinued'
df.loc[f3,'Value'] = ''

f4=((df['Local Authority Type'] =='right to buy (modernised terms)')| 
    (df['Local Authority Type'] == 'rent to mortgage')|
    (df['Public Authority Type'] == 'Local authority')| 
    (df['Public Authority Type'] == 'Scottish Homes')|
    (df['Public Authority Type'] == 'Housing association')| 
    (df['Public Authority Type'] == 'Total')) & (df['Unit']=='Applications')
df.loc[f4,'Sales or Application Type'] = 'Applications by sitting tenants'

#  Symbols Used '..' : not available, - : nil, na : not applicable
df = df.replace({'Marker' : {'..' : 'Not Available', '-' : 'Nil', 'na' : 'Not Applicable'}})
df['Marker'] = df['Marker'].fillna('Not Applicable')
df = df.replace({'Public Authority Type' : {'' : 'Not Applicable'}})
df = df.replace({'Local Authority Type' : {'' : 'Not Applicable'}})


# %%
tidy = df[['Period','Sales or Application Type','Local Authority Type','Public Authority Type','Value', 'Marker', 'Measure Type']] #'Unit']]

for column in tidy:
    if column in ('Marker', 'Public Authority Type', 'Local Authority Type','Sales or Application Type'):
        tidy[column] = tidy[column].map(lambda x: pathify(x))


# %%
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
