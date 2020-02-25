# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *

scraper = Scraper('https://www.communities-ni.gov.uk/publications/topic/8182?search=%22Northern+Ireland+Housing+Statistics%22&sort_by=field_published_date')
tabs = { tab.name: tab for tab in scraper.distributions[1].as_databaker() } 
tab = tabs['T2_2']

# +
cell = tab.excel_ref('A3')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
sap = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = Year.shift(0,1).fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('A18').fill(RIGHT).fill(DOWN)
Dimensions = [
            HDim(Year,'Year',DIRECTLY,ABOVE),
            HDim(sap,'NI Household Energy',DIRECTLY,LEFT ),
            HDimConst('Unit','sap-scale'),  
            HDimConst('Measure Type','rate'),
            HDimConst('NI Household Description','Household energy SAP Rating')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/' + new_table['Year']
# new_table['Geography'] = 'Northern Ireland'
# -

savepreviewhtml(c1)


