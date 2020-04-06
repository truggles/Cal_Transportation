#!/usr/bin/env python3

import pandas as pd
import numpy as np




def get_population(counties):

    # For years 2000-2009
    # Broken link at the moment...

    # For years 2010-2019
    df2 = pd.read_excel('data/E-4_2019InternetVersion.xls', 
            sheet_name='Table 1 County State', header=3, index_col=0)


    df2 = df2.T
    df2['year'] = df2.index.year

    # There are lots of stupid spaces at the end of the county names
    county_names = []
    for col in df2.columns:
        for county in counties:
            if county in col:
                county_names.append(col)
    assert(county_names != [])

    df2 = df2.reset_index()
    df2['population'] = np.zeros(len(df2.index))
    for county in county_names:
        df2['population'] += df2[county]
    df2 = df2[['year', 'population']]


    return df2


# Real GDP by chained 2012 dollars
def get_county_GDP(county):

    df1 = pd.read_excel(f'data/BEA_Real_Gross_Domestic_Product_by_County_2012-2015_CA.xlsx',
            sheet_name='Real GDP', header=3, index_col=False)

    df1 = df1.rename(columns={'Unnamed: 0': 'FIPS',
        'Unnamed: 1': 'County',
        'Unnamed: 2': 'State',
        'Unnamed: 3': 'LineCode',
        'Unnamed: 4': 'IndustryName',
        })
    df1 = df1.set_index('County')

    df2 = pd.read_excel(f'data/BEA_Real_Gross_Domestic_Product_by_County_2015-2018_CA.xlsx',
            sheet_name='Table 1', header=3, index_col=False)
    df2 = df2.rename(columns={'Unnamed: 0': 'County'})
    df2 = df2.set_index('County')

    df = df1[[2012, 2013, 2014, 2015]]
    df[2016] = df2[2016]
    df[2017] = df2[2017]
    df[2018] = df2[2018]

    return df



def get_GDP_from_Metro_files(files):

    print(files)

    years = {}
    for y in range(2001, 2018):
        years[str(y)] = []
    for f in files:
        df = pd.read_csv(f'data/gdp/{f}')
        assert(df.loc[0, 'Description'] == 'All industry total'), "Misalignment in assumptions that first row is always good"

        for y in range(2001, 2018):
            years[str(y)].append(float(df.loc[0, str(y)]))

    df = pd.DataFrame(years)
    df = df.T
    df['gdp'] = np.zeros(len(df.index))
    for col in df.columns:
        df['gdp'] += df[col]
    df = df[['gdp']]

    return df






# FIXME import this from `region_mapping.xlsx`
mpo_map = {
        'SANDAG' : {
            'counties' : ['San Diego',],
            'gdp_files' : ['MAGDP2_CA_San-Diego-Carlsbad_2001_2017.csv',]
        },
        'SCAG' : {
            'counties' : ['Imperial', 'Los Angeles', 'Orange', 
                    'Ventura', 'Riverside', 'San Bernardino'],
            'gdp_files' : ['MAGDP2_CA_El-Centro_2001_2017.csv',
                    'MAGDP2_CA_Los-Angeles-Long-Beach-Anaheim_2001_2017.csv',
                    'MAGDP2_CA_Oxnard-Thousand-Oaks-Ventura_2001_2017.csv',
                    'MAGDP2_CA_Riverside-San-Bernardino-Ontario_2001_2017.csv'],
        }
}

for mpo, info in mpo_map.items():

    print(mpo)
    print(info['counties'])
    print(info['gdp_files'])

    df = get_population(info['counties'])

    #print(df.head())

    get_GDP_from_Metro_files(info['gdp_files'])
    #df_gdp = get_county_GDP(counties)
