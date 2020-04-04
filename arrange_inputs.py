#!/usr/bin/env python3

import pandas as pd
import numpy as np




def get_county_population(county):

    # For years 2000-2009
    # Broken link at the moment...

    # For years 2010-2019
    df2 = pd.read_excel('data/E-4_2019InternetVersion.xls', 
            sheet_name='Table 1 County State', header=3, index_col=0)


    df2 = df2.T
    df2['year'] = df2.index.year

    # There are lots of stupid spaces at the end of the county names
    county_name = None
    for col in df2.columns:
        if county in col:
            county_name = col
            break
    assert(county_name != None)

    df2 = df2.reset_index()
    df2['population'] = df2[county_name]
    df2 = df2[['year', 'population']]


    return df2


# Real GDP by chained 2012 dollars
def get_county_GDP(county):

    df1 = pd.read_excel(f'data/BEA_Real_Gross_Domestic_Product_by_County_2012-2015_CA.xlsx',
            header=3, index_col=False)

    df1 = df1.rename(columns={'Unnamed: 0': 'FIPS',
        'Unnamed: 1': 'County',
        'Unnamed: 2': 'State',
        'Unnamed: 3': 'LineCode',
        'Unnamed: 4': 'IndustryName',
        })
    print(df1.head())

    df2 = pd.read_excel(f'data/BEA_Real_Gross_Domestic_Product_by_County_2015-2018_CA.xlsx',
            header=3, index_col=False)
    print(df2.head())





counties = ['Alameda', 'San Mateo']

for county in counties:

    df = get_county_population(county)

    print(county)
    print(df.head())

    get_county_GDP(county)
