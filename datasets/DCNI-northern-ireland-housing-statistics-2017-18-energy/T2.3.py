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
tab = tabs['T2_3']

# +
cell = tab.excel_ref('A3')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
grants = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = grants.fill(RIGHT).is_not_blank().is_not_whitespace()
measure = cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',CLOSEST,LEFT),
            HDim(grants,'NI Household Energy',DIRECTLY,LEFT ),
            HDim(measure,'Unit',DIRECTLY,ABOVE),  
            HDim(measure,'Measure Type',DIRECTLY,ABOVE),
            HDimConst('NI Household Description','Warm Homes Scheme Grants Processed')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'gregorian-interval/' + new_table['Year'].astype(str).str[:4] + '-03-31T00:00:00/P1Y'
# new_table['Geography'] = 'Northern Ireland'
# -

new_table['Measure Type'] = new_table['Measure Type'].map(
    lambda x: {
        'Number' : 'Count', 
        'Value' : 'gbp-total'}.get(x, x))


new_table['Unit'] = new_table['Unit'].map(
    lambda x: {
        'Number' : 'grants', 
        'Value' : 'gbp'}.get(x, x))
