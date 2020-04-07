#!/usr/bin/env python3

import pandas as pd
import numpy as np
from glob import glob
import calendar

import matplotlib.pyplot as plt
import matplotlib



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
    df2['pop'] = np.zeros(len(df2.index))
    for county in county_names:
        df2['pop'] += df2[county]
    df2 = df2[['year', 'pop']]
    df2 = df2.set_index('year')

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



def get_GDP_from_Metro_files(files, years):

    years_map = {}
    for y in years:
        years_map[str(y)] = []
    for f in files:
        df = pd.read_csv(f'data/gdp/{f}')
        assert(df.loc[0, 'Description'] == 'All industry total'), "Misalignment in assumptions that first row is always good"

        for y in years:
            years_map[str(y)].append(float(df.loc[0, str(y)]))

    df = pd.DataFrame(years_map)
    df = df.T
    df['year'] = years
    df = df.set_index('year')
    df['gdp'] = np.zeros(len(df.index))
    for col in df.columns:
        df['gdp'] += df[col]
    df = df[['gdp']]

    return df



# EMFAC has different files for each year, so we can save time
# by only loading the years we are interested in
def get_EMFAC_data(mpo, years):

    # total values per year
    vmt = []
    co2 = []
    fuel = []

    for y in years:

        # suffix is date/time I downloaded the file
        f_name = glob(f'data/EMFAC2017/MPOs/EMFAC2017-EI-2011Class-{mpo}-{y}-Annual-*.csv')
        assert(len(f_name) == 1), "Must have unique file"
        df = pd.read_csv(f_name[0], header=7)

        df = df.where( (df['Vehicle Category'] == 'LDA') |
            (df['Vehicle Category'] == 'LDT1') |
            (df['Vehicle Category'] == 'LDT2'), 0)

        n_days = 366 if calendar.isleap(y) else 365
        vmt.append(df['VMT'].sum()*n_days) # originally, miles/day for VMT
        co2.append(df['CO2_TOTEX'].sum()*n_days) #  originally, tons/day for Emissions
        fuel.append(df['Fuel Consumption'].sum()*n_days) # originally, 1000 gallons/day for Fuel Consumption

    df = pd.DataFrame({
        'year' : years,
        'vmt' : vmt,
        'co2' : co2,
        'eLDV' : fuel
    })
    df = df.set_index('year')

    return df
    

# Make one df only covering desired years
def stitch(df_pop, df_gdp, df_emfac):

    df_emfac['gdp'] = df_gdp['gdp']
    df_emfac['pop'] = df_pop.loc[df_emfac.index[0]:df_emfac.index[-1], 'pop']

    return df_emfac



def plot_relative_changes(df, save_name):

    fig, ax = plt.subplots()

    for var in ['vmt', 'co2', 'eLDV', 'gdp', 'pop']:
        ax.plot(df.index, df[var]/df.iloc[0][var]*100., label=var)

    ax.set_ylabel(f"cumulative percent change ({df.index[0]} base)")
    ax.set_xlabel("years")
    
    plt.legend()
    plt.savefig(f"plots/{save_name}_relative_change.png")


def plot_relative_changes_Kaya(df, save_name):

    fig, ax = plt.subplots()

    #for var in ['vmt', 'co2', 'eLDV', 'gdp', 'pop']:
    ax.plot(df.index, df['pop']/df.iloc[0]['pop']*100., label='Pop')
    ax.plot(df.index, (df['gdp']/df['pop'])/(df.iloc[0]['gdp']/df.iloc[0]['pop'])*100., label='GDP/Pop')
    ax.plot(df.index, (df['vmt']/df['gdp'])/(df.iloc[0]['vmt']/df.iloc[0]['gdp'])*100., label='VMT/GDP')
    ax.plot(df.index, (df['eLDV']/df['vmt'])/(df.iloc[0]['eLDV']/df.iloc[0]['vmt'])*100., label=r'E$_{LDV}$/VMT')
    ax.plot(df.index, (df['co2']/df['eLDV'])/(df.iloc[0]['co2']/df.iloc[0]['eLDV'])*100., label=r'GHG$_{LDV}$/E$_{LDV}$')

    ax.set_ylabel(f"cumulative percent change ({df.index[0]} base)")
    ax.set_xlabel("years")
    
    plt.legend()
    plt.savefig(f"plots/{save_name}_relative_change_Kaya.png")


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

years = [y for y in range(2010, 2018)]

print(years)

for mpo, info in mpo_map.items():

    print(mpo)
    print(f"Counties: {info['counties']}")
    #print(info['gdp_files'])

    df_pop = get_population(info['counties'])

    df_gdp = get_GDP_from_Metro_files(info['gdp_files'], years)

    df_emfac = get_EMFAC_data(mpo, years)

    df = stitch(df_pop, df_gdp, df_emfac)

    plot_relative_changes(df, mpo)
    plot_relative_changes_Kaya(df, mpo)



