#!/usr/bin/env python3

import pandas as pd
import numpy as np
from glob import glob
import calendar

import matplotlib.pyplot as plt
import matplotlib



def get_population_files(counties, f_name):

    df = pd.read_excel(f'data/{f_name}', 
            sheet_name='Table 1 County State', header=3, index_col=0)


    # Drop the data with April (Census) dates as they become 
    # approximately redundant with other 1 January 20XX values
    # and are not consistent.
    to_keep = []
    for col in df.columns:
        if col.month == 1:
            to_keep.append(col)

    df = df[to_keep]

    df = df.T
    df['year'] = df.index.year

    # There are lots of stupid spaces at the end of the county names
    county_names = []
    for col in df.columns:
        for county in counties:
            if county in col:
                county_names.append(col)
    assert(county_names != [])

    df = df.reset_index()
    df['pop'] = np.zeros(len(df.index))
    for county in county_names:
        df['pop'] += df[county]
    df = df[['year', 'pop']]
    df = df.set_index('year')

    return df



def get_population(counties):

    # For years 2000-2010
    df1 = get_population_files(counties, 'E-4_2009InternetVersion.xls')

    # For years 2011-2019
    df2 = get_population_files(counties, 'E-4_2019InternetVersion.xls')

    df1 = df1.append(df2)
    return df1


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
def stitch_and_add_decomposition(df_pop, df_gdp, df_emfac):

    df_emfac['gdp'] = df_gdp['gdp']
    df_emfac['pop'] = df_pop.loc[df_emfac.index[0]:df_emfac.index[-1], 'pop']

    df_emfac['GDP/Pop'] = df_emfac['gdp']/df_emfac['pop']
    df_emfac['VMT/GDP'] = df_emfac['vmt']/df_emfac['gdp']
    df_emfac['eLDV/vmt'] = df_emfac['eLDV']/df_emfac['vmt']
    df_emfac['co2/eLDV'] = df_emfac['co2']/df_emfac['eLDV']

    return df_emfac



def plot_relative_changes(df, save_name):

    fig, ax = plt.subplots()

    for var in ['vmt', 'co2', 'eLDV', 'gdp', 'pop']:
        ax.plot(df.index, df[var]/df.iloc[0][var]*100., label=var)

    ax.set_ylabel(f"cumulative percent change ({df.index[0]} base)")
    ax.set_xlabel("years")
    
    plt.legend()
    plt.savefig(f"plots/{save_name}_relative_change.png")


def get_kaya_label_map():

    return {
        'pop' : ['Pop', 'blue'],
        'GDP/Pop' : ['GDP/Pop', 'orange'],
        'VMT/GDP' : ['VMT/GDP', 'green'],
        'eLDV/vmt' : [r'E$_{LDV}$/VMT', 'red'],
        'co2/eLDV' : [r'GHG$_{LDV}$/E$_{LDV}$', 'gray'],
    }

def plot_relative_changes_Kaya(df, save_name):

    fig, ax = plt.subplots()

    for var, info in get_kaya_label_map().items():
        ax.plot(df.index, df[var]/df.iloc[0][var]*100., color=info[1], label=info[0])

    ax.set_ylabel(f"cumulative percent change ({df.index[0]} base)")
    ax.set_xlabel("years")
    
    plt.legend()
    plt.savefig(f"plots/{save_name}_relative_change_Kaya.png")


def plot_simple_Kaya_decomposition(df, save_name):

    fig, ax = plt.subplots()

    # Calculate relative difference for each var
    # at each annual step.
    # Need to keep track of cumulative positions b/c of negative bars
    cum_top = [0. for _ in range(len(df.index))]
    cum_bottom = [0. for _ in range(len(df.index))]
    for var, info in get_kaya_label_map().items():
        ary = df[var] - df[var].shift(periods=1)
        ary = ary/df[var].shift(periods=1)*100.
        for i in range(1, len(df.index)):
            label=info[0] if i == 1 else '_nolegend_'
            if ary.iloc[i] >= 0:
                ax.bar(df.index[i], ary.iloc[i], bottom=cum_top[i], color=info[1], label=label, alpha=.3)
                cum_top[i] += ary.iloc[i]
            else: # negative
                ax.bar(df.index[i], ary.iloc[i], bottom=cum_bottom[i], color=info[1], label=label, alpha=.3)
                cum_bottom[i] += ary.iloc[i]
    co2 = df['co2'] - df['co2'].shift(periods=1)
    co2 = co2/df['co2'].shift(periods=1)*100.
    ax.scatter(df.index, co2, marker='^', color='black', label='GHG') 

    ax.set_ylim(ax.get_ylim()[0]*1.5, ax.get_ylim()[1]*1.5)
    ax.set_ylabel(f"cumulative percent change ({df.index[0]} base)")
    ax.set_xlabel("years")
    
    plt.legend(ncol=2)
    plt.savefig(f"plots/{save_name}_simple_Kaya_decomposition.png")


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

years = [y for y in range(2001, 2018)]

print(years)

for mpo, info in mpo_map.items():

    print(mpo)
    print(f"Counties: {info['counties']}")

    df_pop = get_population(info['counties'])

    df_gdp = get_GDP_from_Metro_files(info['gdp_files'], years)

    df_emfac = get_EMFAC_data(mpo, years)

    df = stitch_and_add_decomposition(df_pop, df_gdp, df_emfac)

    plot_relative_changes(df, mpo)
    plot_relative_changes_Kaya(df, mpo)
    plot_simple_Kaya_decomposition(df, mpo)



