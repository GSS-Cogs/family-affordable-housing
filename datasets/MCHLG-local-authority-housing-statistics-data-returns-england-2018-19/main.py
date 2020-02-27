# # MCHLG-local-authority-housing-statistics-data-returns-england-2018-19 

from gssutils import * 
import json 
import numpy as np

info = json.load(open('info.json')) 
landingPage = info['Landing Page'] 
landingPage 

# +
#### Add transformation script here #### 

scraper = Scraper(landingPage) 
scraper 
# -
try:
    sheets = scraper.distributions[0].as_databaker()
except Exception as e:
    print(str(e))

eng = 'England'
engCde = 'E92000001'
metShire = 'Met and Shire County Totals'
sngTieAu = 'Lower and Single Tier Authority Data'
onsGeogy = 'ONS Geography'
areaCode = 'MHCLG Area Code'
ovAlArea = 'Overall Area'
statCode = 'MHCLG Statistic Code'
nmes = []


def setNames(nme):
    if nme == 0:
        return [
                'Ownership',
                'House Type',
                'Total Dwellings',
                'Spare 1',
                statCode
            ]
    elif nme == 1:
        return [
                'Right to buy Dwelling type',
                'Sales Transfer Type',
                'Total Dwellings',
                'Sales Transfer Breakdown',
                statCode
            ]
    elif nme == 2:
        return [
                'Allocation Criteria 4th',
                'Allocation Criteria 3rd',
                'Allocation Criteria 2nd',
                'Allocation Criteria 1st',
                statCode
            ]
    elif nme == 3:
        return [
                'Lettings & Nominations Criteria 4th',
                'Lettings & Nominations Criteria 3rd',
                'Lettings & Nominations Criteria 2nd',
                'Lettings & Nominations Criteria 1st',
                statCode
            ]
    elif nme == 4:
        return [
                'Dwellings Vacant',
                'Vacant Criteria',
                'Vacant 1st',
                'Vacant 2nd',
                statCode
            ]
    elif nme == 5:
        return [
                'Condition of Stock Criteria 4th',
                'Condition of Stock Criteria 3rd',
                'Condition of Stock Criteria 2nd',
                'Condition of Stock Criteria 1st',
                statCode
            ]
    elif nme == 6:
        return [
                'Stock Management 4th',
                'Stock Management 3rd',
                'Stock Management 2nd',
                'Stock Management 1st',
                statCode
            ]
    elif nme == 7:
        return [
                'Rent & Arrears 4th',
                'Rent & Arrears 3rd',
                'Rent & Arrears 2nd',
                'Rent & Arrears 1st',
                statCode
            ]
    elif nme == 8:
        return [
                'Supply 4th',
                'Supply 3rd',
                'Supply 2nd',
                'Supply 1st',
                statCode
            ]
    elif nme == 9:
        return [
                'Start Type',
                'Developer Contributions',
                'Owner',
                'Starts 1st',
                statCode
            ]


def extractTable(tab, colNmes):
    try:
        col1 = tab.excel_ref('A8').fill(DOWN).is_not_blank()
        col2 = tab.excel_ref('B8').fill(DOWN).is_not_blank()
        col3 = tab.excel_ref('C8').fill(DOWN).is_not_blank()
        col4 = tab.excel_ref('D8').fill(DOWN).is_not_blank()
        col5 = tab.excel_ref('E8').fill(DOWN).is_not_blank()
        col6 = tab.excel_ref('E5').expand(RIGHT).is_not_blank() 
        col7 = tab.excel_ref('E8').fill(RIGHT).fill(DOWN).is_not_blank()
        col8 = tab.excel_ref('E4').expand(RIGHT).is_not_blank()
        col9 = tab.excel_ref('E3').expand(RIGHT).is_not_blank()
        col10 = tab.excel_ref('E6').expand(RIGHT).is_not_blank()
        col11 = tab.excel_ref('E7').expand(RIGHT).is_not_blank()
       
        Dimensions = [
            HDim(col1, ovAlArea, DIRECTLY, LEFT),
            HDim(col2, areaCode, DIRECTLY, LEFT),
            HDim(col3, onsGeogy, DIRECTLY, LEFT),
            HDim(col4, metShire, DIRECTLY, LEFT),
            HDim(col5, sngTieAu, DIRECTLY, LEFT),
            HDim(col6, colNmes[0], DIRECTLY, ABOVE),
            HDim(col8, colNmes[1], DIRECTLY, ABOVE),
            HDim(col9, colNmes[2], DIRECTLY, ABOVE),
            HDim(col10, colNmes[3], DIRECTLY, ABOVE),
            HDim(col11, colNmes[4], DIRECTLY, ABOVE)
            ]

        c1 = ConversionSegment(col7, Dimensions, processTIMEUNIT=True)
        c1 = c1.topandas()
        
        tbl = c1
        return tbl
    except Exception as e:
        return "extract_sheet_single_table: " + str(e)


def reconfigureTable(nme, inx):
    mainTbls[inx][sngTieAu][mainTbls[inx][ovAlArea] == eng] = 'Total'

    mainTbls[inx][areaCode].fillna(value = pd.np.nan, inplace = True)
    mainTbls[inx][areaCode] = mainTbls[inx][areaCode].fillna(value = 'N/A')

    mainTbls[inx][onsGeogy] = mainTbls[ind][onsGeogy].fillna(value = 'N/A')
    mainTbls[inx][onsGeogy][(mainTbls[inx][ovAlArea] == 'Unitary Authorities') & (mainTbls[inx][onsGeogy] == 'N/A')] = 'E06'
    mainTbls[inx][onsGeogy][(mainTbls[inx][ovAlArea] == 'London Boroughs') & (mainTbls[inx][onsGeogy] == 'N/A')] = 'E09'
    mainTbls[inx][onsGeogy][(mainTbls[inx][ovAlArea] == 'Shire Districts') & (mainTbls[inx][onsGeogy] == 'N/A')] = 'E10'
    mainTbls[inx][onsGeogy][(mainTbls[inx][ovAlArea] == 'Metropolitan Districts') & (mainTbls[inx][onsGeogy] == 'N/A')] = 'E08'

    mainTbls[inx][metShire].fillna(value = pd.np.nan, inplace = True)
    mainTbls[inx][metShire] = mainTbls[inx][metShire].ffill()
    mainTbls[inx][metShire][mainTbls[inx][ovAlArea] == eng] = 'Total'
    mainTbls[ind][metShire] = mainTbls[inx][metShire].fillna(value = 'Total')

    mainTbls[inx][ovAlArea].fillna(value = pd.np.nan, inplace = True)
    mainTbls[inx][ovAlArea] = mainTbls[inx][ovAlArea].ffill()

    mainTbls[inx][sngTieAu].fillna(value = pd.np.nan, inplace = True)
    mainTbls[inx][sngTieAu] = mainTbls[inx][sngTieAu].fillna(value = 'Total')
    
    if inx == 0:
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].fillna(value = 'All')

        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].ffill()
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)

    elif inx == 1:
        mainTbls[inx][nme[0]] = 'Right to buy ' + mainTbls[inx][nme[0]]  
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]][mainTbls[inx][nme[1]] == 'Right to Buy'] = mainTbls[inx][nme[0]]
        mainTbls[inx][nme[1]][pd.isnull(mainTbls[inx][nme[1]])] = mainTbls[inx][nme[0]]
        mainTbls[inx][nme[1]] = mainTbls[1][nme[1]].ffill()
        mainTbls[inx][nme[1]][pd.isnull(mainTbls[inx][nme[1]])] = mainTbls[inx][nme[2]]
        
        mainTbls[inx].drop(nme[0], axis=1, inplace=True)
        mainTbls[inx].drop(nme[2], axis=1, inplace=True)
        
        mainTbls[inx][nme[3]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[3]] = mainTbls[inx][nme[3]].fillna(value = 'N/A')
    elif inx == 2:
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[2]][mainTbls[inx][nme[1]] == 'Rent arrears'] = 'Waiting list criteria'
        mainTbls[inx][nme[2]][mainTbls[inx][nme[1]] == 'Includes a local connections test'] = 'Waiting list criteria'
        mainTbls[inx][nme[2]][mainTbls[inx][nme[1]] == 'Years that local authority have had a residency test'] = 'Waiting list criteria'
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 3:
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].ffill()
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 4:
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]]
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx].drop(nme[2], axis=1, inplace=True)
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 5:
        mainTbls[inx][onsGeogy][mainTbls[inx][ovAlArea] == eng] = engCde
        
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].ffill()
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 6:    
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx].drop(nme[2], axis=1, inplace=True)
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 7:   
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[1]][mainTbls[inx][nme[0]] == 'N/A'] = 'N/A'
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].ffill()
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 8:   
        mainTbls[inx][nme[0]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[0]] = mainTbls[inx][nme[0]].fillna(value = 'N/A')
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx][nme[2]][mainTbls[inx][nme[1]].str.contains('Affordable units granted final planning')] = 'N/A'
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].ffill()
        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].fillna(value = 'N/A')
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)
    elif inx == 9:   
        mainTbls[inx][onsGeogy][mainTbls[inx][ovAlArea] == eng] = engCde
        
        mainTbls[inx][nme[1]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[1]] = mainTbls[inx][nme[1]].ffill()
        
        mainTbls[inx][nme[2]].fillna(value = pd.np.nan, inplace = True)
        mainTbls[inx][nme[2]] = mainTbls[inx][nme[2]].ffill()
        
        mainTbls[inx].drop(nme[3], axis=1, inplace=True)


mainTbls = []
mainTitles = []
ind = 0
for t in sheets:
    if t.name == 'Menu':
        i = 0
    else:
        nmes = setNames(ind)
        mainTbls.append(extractTable(t, nmes)) 
        reconfigureTable(nmes, ind)
        mainTitles.append(t.name.replace(' - ','-').replace(' ','-').lower())
        print(t.name)
        ind = ind + 1
        if ind > 9:
            break

mainTbls[0].head(60)

# +
# Remove the number from the end of the strings that represent  a reference to comments at the bottom of the spreadsheet
k = 0
for t in mainTbls:
    for c in t.columns:
        if (str(c) != 'OBS') & (str(c) != onsGeogy) & (str(c) != 'DATAMARKER') & (str(c) != statCode):
            print(str(c))
            #mainTbls[k][str(c)] = mainTbls[k][str(c)].apply(pathify)
          #  for x in range(10): 
           #     if (x > 0):
            #        t[statCode] = t[statCode].str.strip(str(x))
             #       t[statCode] = t[statCode].str.strip()
            #for x in range(10): 
             ##   if (x > 0):
               #     t[statCode] = t[statCode].str.strip(str(x))
                #    t[statCode] = t[statCode].str.strip()
        
#mainTbls[1].head(60)

# +
mainTbls[ind][metShire] = mainTbls[ind][metShire].apply(pathify)
mainTbls[ind][sngTieAu] = mainTbls[ind][sngTieAu].apply(pathify)
mainTbls[ind][ovAlArea] = mainTbls[ind][ovAlArea].apply(pathify)
mainTbls[ind][areaCode] = mainTbls[ind][areaCode].apply(pathify)
mainTbls[ind][onsGeogy] = mainTbls[ind][onsGeogy].apply(pathify)

mainTbls[ind][name1] = mainTbls[ind][name1].apply(pathify)
mainTbls[ind][name2] = mainTbls[ind][name2].apply(pathify)
mainTbls[ind][name3] = mainTbls[ind][name3].apply(pathify)
mainTbls[ind][name4] = mainTbls[ind][name4].apply(pathify)

# +
#### Set up the folder path for the output files
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True, parents=True)
# -

mainTbls[ind].drop_duplicates().to_csv(out / (mainTitles[0] + '-observations.csv'), index = False)

mainTitles[0] 


