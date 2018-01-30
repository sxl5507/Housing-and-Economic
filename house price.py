# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 11:12:34 2018

@author: Siyan
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
plt.style.use('ggplot')




# load data based on <RegionName>, set smaller chunksize for small RAM
# filename: csv file name, RegionName: str or number or False, chunksize: number
def LoadData(filename, RegionName=False, chunksize=50000):
    temp=[]
    chunk_load=pd.read_csv('v6 (Dec_2017)/'+filename,
                           chunksize=chunksize,
                           engine ='c', # c engine is faster
                           skip_blank_lines=True)

    # filter data, drop empty columns, set date as index
    if RegionName == False:
        print('loading...')
        for chunk in chunk_load:          
            temp.append(chunk)  
        print('Done!')     
    else:
        print('loading...')
        for chunk in chunk_load:            
            temp.append(chunk[chunk['RegionName']==RegionName])
        print('Done!')
             
    df = pd.concat(temp).dropna(axis=1,how='all')
    df['Date']=pd.to_datetime(df['Date']) 
    df.set_index('Date', drop=True, inplace=True) # set Date as index
    return df





# return features with all types of houses (all home, condo, 1 bedroom, etc.)
# df: DataFrame, column_list: 1d list (meta_feature)
def SelectColumn(df, column_list):
    column_match={}
    for n in column_list:
        for col in df.columns:
            if re.match(n+'_',col):
                column_match.setdefault(n, [])
                column_match[n].append(col)

    flat_list = [item for sublist in column_match.values() for item in sublist]
    df= df[['RegionName'] + flat_list] # add Date and RegionName to df
    return df, column_match





# plot df with selected columns
# df: DataFrame
# feature: 1d list of string (same meta_feature), eg.[MedianListingPrice_AllHomes, MedianListingPrice_1Bedroom]
def TS_Plot(df, feature, groupby='M', group_method='median'):           
    # region name and title
    plt.figure(figsize=(15,9))
    title= str(feature[0].split('_')[0]) # title use meta feature        
    regionname= df['RegionName'].unique()   
    if len(regionname) >1:
        regionname='All'    
        plt.title(title + ' ('+ group_method.title() +' of '+ regionname +' Region)', fontsize=23)    
    else: 
        regionname= str(regionname[0])
        plt.title(title + ' (Region: '+regionname +')', fontsize=24)    
    
    # plot graph, resample, and aggregate
    sub_feature=[]
    method= {'mean': pd.DataFrame.mean, 'median': pd.DataFrame.median, 'mode': pd.DataFrame.mode,
             'max': pd.DataFrame.max, 'min': pd.DataFrame.min}
    for _ in feature:       
        sub_feature.append(_.split('_')[1]) # use sub feature as legend
        df.resample(groupby).apply(method[group_method])[_].plot(fontsize=15, linewidth=2)
          
    # axis labels           
    if re.search('Ratio', title): ylabel= 'Ratio'
    elif re.match('Pct',title): ylabel= 'Percent (%)'
    else: ylabel= 'Price ($)'
    plt.xlabel('Date', fontsize=18)
    plt.ylabel(ylabel,fontsize=18)
    l= plt.legend(sub_feature, loc='best', fontsize=18)
       
    # thickness of legend
    for line in l.get_lines():
        line.set_linewidth(4.0)   
    plt.show()





# display n top and n bottom regions on bar plot
# df: DataFrame, year: num or str
# feature: str, eg. MedianListingPrice_AllHomes or MedianListingPrice_1Bedroom
def Swarm_Plot_AllRegion(df, feature, year=2017, ntop=5, nbottom=5):
    if type(feature)==type(['list_type']): return print('Feature Error: string only, no list!')
  
    # filter by year, include feature, drop nan rows, group by region, sort by feature
    df_year= df.loc[str(year)][['RegionName', str(feature)]].dropna()
    df_region= df_year.groupby('RegionName').mean().sort_values(by=str(feature), ascending=False)
    
    
    # slice and plot
    region_sort_list= df_region.index.values # store sorted region name in a list
    df_year= df_year.set_index('RegionName') # set RegionName as index for easy slice later
    top= df_year.loc[region_sort_list[:ntop]]
    bottom= df_year.loc[region_sort_list[-nbottom:]]
    
    sns.set(font_scale= 1.75)
    plt.figure(figsize=(15,15)).add_subplot(211)
    plt.title('Top {} Regions in Year {} (Ranked by 12 Months Mean)'.format(ntop, year), fontsize=24)
    sns.swarmplot(x= 'RegionName', y= feature, data= top.reset_index(), size=9)
    plt.xticks(rotation=20)
    
    plt.figure(figsize=(15,15)).add_subplot(212)
    plt.title('Bottom {} Regions in Year {} (Ranked by 12 Months Mean)'.format(nbottom, year), fontsize=24)
    sns.swarmplot(x= 'RegionName', y= feature, data= bottom.reset_index(), size=9)
    plt.xticks(rotation=20)
    plt.show()
    
    

#%%

# columns included for each file
meta_feature=['MedianListingPrice', 'MedianRentalPrice', 'MedianSoldPrice',
          'PctOfHomesIncreasingInValues', 'PctOfHomesSellingForGain',
          'PriceToRentRatio', 'Turnover']


# filter and plot data for <zip_time_series.csv>
#zipcode=78731
#zip_raw = LoadData('zip_time_series.csv', RegionName=zipcode, chunksize=150000)
#zip_df, zip_column_match = SelectColumn(zip_raw, meta_feature)
#TS_Plot(zip_df, zip_column_match['MedianListingPrice'])



# filter and plot data for <state_time_series.csv>
state=False

state_raw = LoadData('State_time_series.csv', RegionName=state, chunksize=150000)
state_df, state_column_match = SelectColumn(state_raw, meta_feature)

print(state_column_match)
# feature: 1d list of string (same meta_feature), eg.[MedianListingPrice_AllHomes, MedianListingPrice_1Bedroom]
TS_Plot(state_df, ['MedianRentalPrice_1Bedroom'], groupby='M', group_method='mean') 
Swarm_Plot_AllRegion(state_df, year=2017, feature='MedianRentalPrice_1Bedroom', ntop=10)








