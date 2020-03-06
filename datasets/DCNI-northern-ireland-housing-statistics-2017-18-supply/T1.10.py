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
tab = tabs['T1.10']

# +
cell = tab.excel_ref('A5')
Year = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
quarter = cell.shift(1,0).fill(DOWN).is_not_blank().is_not_whitespace()
supply = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
observations = supply.fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('D74')
Dimensions = [
            HDim(Year,'Year',CLOSEST,ABOVE),
            HDim(quarter,'quarter',DIRECTLY,LEFT),
            HDimConst('Geography','Northern Ireland'),
            HDim(supply,'NI Housing Supply',DIRECTLY,ABOVE),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Housing Description','Chained Volume Measure of Housing Output')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
# new_table['NI Housing Supply'] = new_table['house']+ ' ' + new_table['NI Housing Supply']
# new_table['NI Housing Supply'] = new_table['NI Housing Supply'].str.rstrip('123457')
# def user_perc(x):
    
#     if (str(x) ==  'Totals '): 
        
#         return 'gregorian-interval/2010-03-31T00:00:00/P8Y'
#     else:
#         return 'gregorian-interval/' + str(x)[0:4] + '-03-31T00:00:00/P1Y'
    
# new_table['Period'] = new_table.apply(lambda row: user_perc(row['Year']), axis = 1)
# +
def user_perc(y,x):
    
    if (str(x)[0:3] ==  'Apr') : 
        
        return 'quarter/' + str(y)[:4] + '-Q2'
    elif (str(x)[0:3] ==  'Jul') : 
        
        return 'quarter/' + str(y)[:4] + '-Q3'
    elif (str(x)[0:3] ==  'Oct') : 
        
        return 'quarter/' + str(y)[:4] + '-Q4'
    elif (str(x)[0:3] ==  'Jan') : 
        
        return 'quarter/' + str(y)[:4] + '-Q1'
    else:
        return 'gregorian-interval/' + str(x)[0:4] + '-03-31T00:00:00/P1Y'
    
new_table['Period'] = new_table.apply(lambda row: user_perc(row['Year'],row['quarter']), axis = 1)
