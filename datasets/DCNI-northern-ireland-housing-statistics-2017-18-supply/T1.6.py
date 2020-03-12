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
tabs = { tab.name: tab for tab in scraper.distributions[6].as_databaker() } 
tab = tabs['T1.6']

# +
cell = tab.excel_ref('A3')
Year = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
development = cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace() 
observations = development.fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('D48')
Dimensions = [
            HDim(Year,'Year',DIRECTLY,LEFT),
            HDimConst('Geography','Northern Ireland'),
            HDim(development,'NI Housing Supply',DIRECTLY,ABOVE),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Housing Description','Building Control New Dwelling Starts by Development Type')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
# +
def user_perc(x):
    
    if (str(x).split(' ')[0] ==  'Apr') : 
        
        return 'quarter/' + str(x)[-4:] + '-Q1'
    elif (str(x).split(' ')[0] ==  'Jul') : 
        
        return 'quarter/' + str(x)[-4:] + '-Q2'
    elif (str(x).split(' ')[0] ==  'Oct') : 
        
        return 'quarter/' + str(x)[-4:] + '-Q3'
    elif (str(x).split(' ')[0] ==  'Jan') : 
        
        return 'quarter/' + str(int(str(x)[-4:])-1) + '-Q4'
    else:
        return 'gregorian-interval/' + str(x)[0:4] + '-03-31T00:00:00/P1Y'
    
new_table['Period'] = new_table.apply(lambda row: user_perc(row['Year']), axis = 1)
# -

new_table['NI Housing Supply'] = new_table['NI Housing Supply'].map(
    lambda x: {
        'Private owner/ speculative development' : 'Private owner or speculative development' ,
       'Total \nNew Dwelling \nStarts' : 'Total New Dwelling Starts'        
        }.get(x, x))
