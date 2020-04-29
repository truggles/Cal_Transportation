#!/usr/bin/env python3

import pandas as pd
import numpy as np
from glob import glob
import calendar

import matplotlib.pyplot as plt
import matplotlib

import helpers


def open_cvrp_rebate_file():

    df = pd.read_excel('data/CVRP_stats_data_updated_3Feb2020.xlsx',
            sheet_name='CVRP')

    df['Application Year'] = df.agg({'Application Date': lambda x: x.year})

    # Only return used columns
    return df[['Rebate Dollars', 'Application Date', 'Application Year',
        'Vehicle Category', 'County']]

def get_cvrp_rebate_info(df_cvrp, counties):
    
    # All years we could have data for:
    years = [y for y in range(2000, 2021)]

    n_rebates = []
    rebate_dollars = []
    county_list = []
    year_list = []
    for y in years:
        for county in counties:
            year_list.append(y)
            county_list.append(county)
            idxs = (df_cvrp['County'] == county) & (df_cvrp['Application Year'] == y)
            n_rebates.append(idxs.sum())
            rebate_dollars.append(df_cvrp.loc[idxs, 'Rebate Dollars'].sum())

    df = pd.DataFrame({
        'year': year_list,
        'county': county_list,
        'n_rebates': n_rebates,
        'rebate_dollars': rebate_dollars
    })
    print(df)
    df.to_csv('data/cvrp_summary.csv')


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
    total_vehicles = []
    vmt = []
    co2 = []
    fuel = []

    # there are two merged MPOs that need 2 open EMFAC files per year,
    # deal with those here.
    merged_map = {
        'MTC_and_AMBAG' : ['MTC', 'AMBAG'],
        'SACOG_and_TMPO' : ['SACOG', 'TMPO']
    }

    for y in years:

        # merged files
        if mpo in merged_map.keys():
            # suffix is date/time I downloaded the file
            f_name = glob(f'data/EMFAC2017/MPOs/EMFAC2017-EI-2011Class-{merged_map[mpo][0]}-{y}-Annual-*.csv')
            assert(len(f_name) == 1), f"Must have unique file, returned files {f_name}"
            df = pd.read_csv(f_name[0], header=7)

            f_name = glob(f'data/EMFAC2017/MPOs/EMFAC2017-EI-2011Class-{merged_map[mpo][1]}-{y}-Annual-*.csv')
            assert(len(f_name) == 1), f"Must have unique file, returned files {f_name}"
            df2 = pd.read_csv(f_name[0], header=7)

            # append for to continue normal workflow
            df = df.append(df2)

        else:
            # suffix is date/time I downloaded the file
            f_name = glob(f'data/EMFAC2017/MPOs/EMFAC2017-EI-2011Class-{mpo}-{y}-Annual-*.csv')
            assert(len(f_name) == 1), f"Must have unique file, returned files {f_name}"
            df = pd.read_csv(f_name[0], header=7)

        df = df.where( (df['Vehicle Category'] == 'LDA') |
            (df['Vehicle Category'] == 'LDT1') |
            (df['Vehicle Category'] == 'LDT2'), 0)

        n_days = 366 if calendar.isleap(y) else 365
        total_vehicles.append(df['Population'].sum()) # number of vehicles?
        vmt.append(df['VMT'].sum()*n_days) # originally, miles/day for VMT
        co2.append(df['CO2_TOTEX'].sum()*n_days) #  originally, tons/day for Emissions
        fuel.append(df['Fuel Consumption'].sum()*n_days/1000.) # originally, 1000 gallons/day for Fuel Consumption

    df = pd.DataFrame({
        'year' : years,
        'n_vehicles' : total_vehicles,
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

    # simple Kaya decomposition
    for kaya in get_kaya_label_map().keys():
        df_emfac[f'{kaya}_pct'] = df_emfac[kaya] - df_emfac[kaya].shift(periods=1)
        df_emfac[f'{kaya}_pct'] = df_emfac[f'{kaya}_pct']/df_emfac[kaya].shift(periods=1)*100.
        df_emfac[f'{kaya}_diff'] = df_emfac[kaya] - df_emfac[kaya].shift(periods=1)

    return df_emfac


def add_cvrp_rebate_info(counties, df):

    df_cvrp = pd.read_csv('data/cvrp_summary.csv')

    n_rebates = np.zeros(len(df.index))
    rebate_dollars = np.zeros(len(df.index))
    for i, yr in enumerate(df.index):
        for county in counties:
            idxs = (df_cvrp['county'] == county) & (df_cvrp['year'] == yr)
            n_rebates[i] += df_cvrp.loc[idxs, 'n_rebates'].sum()
            rebate_dollars[i] += df_cvrp.loc[idxs, 'rebate_dollars'].sum()

    df['n_rebates'] = n_rebates
    df['rebate_dollars'] = rebate_dollars

    return df



def stitch_mpo_data(mpo, info):

    df_pop = get_population(info['counties'])
    df_gdp = get_GDP_from_Metro_files(info['gdp_files'], years)
    df_emfac = get_EMFAC_data(mpo, years)
    df = stitch_and_add_decomposition(df_pop, df_gdp, df_emfac)
    df = add_cvrp_rebate_info(info['counties'], df)

    df.to_csv(f'data/{mpo}.csv')



def plot_relative_changes(df, save_name):

    fig, ax = plt.subplots()

    for var in ['vmt', 'co2', 'eLDV', 'gdp', 'pop']:
        ax.plot(df.index, df[var]/df.iloc[0][var]*100., label=var)

    ax.set_ylabel(f"cumulative percent change ({df.index[0]} base)")
    ax.set_xlabel("years")
    
    plt.legend()
    plt.savefig(f"plots/{save_name}_relative_change.png")
    plt.close()


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
    plt.close()


def plot_simple_Kaya_decomposition(df, save_name):

    fig, ax = plt.subplots()

    # Calculate relative difference for each var
    # at each annual step.
    # Need to keep track of cumulative positions b/c of negative bars
    cum_top = [0. for _ in range(len(df.index))]
    cum_bottom = [0. for _ in range(len(df.index))]
    for var, info in get_kaya_label_map().items():
        ary = df[f'{var}_pct']
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
    ax.set_ylabel(r"CO2e (change from previous year)")
    ax.set_xlabel("years")
    
    plt.legend(ncol=2)
    plt.savefig(f"plots/{save_name}_simple_Kaya_decomposition.png")
    plt.close()




def plot_simple_correlations(df, mpo):


    for rebate, lab in {'n_rebates' : 'Number of CVRP rebates per 1,000 vehicles',
                        'rebate_dollars' : 'Total CVRP rebate dollars per 1,000 vehicles ($)'}.items():

        fig, ax = plt.subplots()
        
        for kaya, info in get_kaya_label_map().items():
            ax.scatter(df[rebate]/df['n_vehicles']*1000, df[f'{kaya}_pct'], label=info[0], color=info[1])

        ax.set_ylabel("Kaya factor percent change")
        ax.set_xlabel(lab)
        
        plt.legend(ncol=2)
        plt.savefig(f"plots/{mpo}_correlations_pct_{rebate}.png")
        plt.close()



def plot_agg_simple_correlations(df, save_name):

    mpo_map = helpers.get_mpo_map()

    for rebate, lab in {'n_rebates' : 'Number of CVRP rebates per 1,000 vehicles in region',
                        'rebate_dollars' : 'Total CVRP rebate dollars per 1,000 vehicles in region ($)',
                        }.items():
        
        for kaya, info in get_kaya_label_map().items():
            fig, ax = plt.subplots()

            for i, mpo in enumerate(mpo_map.keys()):

                m = 'o' if i < 10 else '^'

                #idxs = (df[rebate] > 0)
                idxs = (df['mpo'] == mpo)
                #ax.scatter(df.[rebate]/df['n_vehicles']*1000, df[f'{kaya}_pct'], label=info[0], color=info[1])
                ax.scatter(df.loc[idxs, rebate]/df.loc[idxs, 'n_vehicles']*1000, df.loc[idxs, f'{kaya}_pct'], label=mpo.replace('_and_',' & '), alpha=0.3, marker=m)

            ax.set_ylabel("Kaya factor percent change")
            ax.set_xlabel(lab)
            
            plt.legend(ncol=4, fontsize=8)
            plt.title(kaya)
            plt.savefig(f"plots/{save_name}_correlations_pct_{rebate}_{kaya.replace('/','_per_')}.png")
            plt.close()

            # Below is redundant for both rebate info types
            if rebate == 'rebate_dollars':
                continue

            # Next plot of var vs years
            fig, ax = plt.subplots()

            for i, mpo in enumerate(mpo_map.keys()):

                m = 'o' if i < 10 else '^'

                #idxs = (df[rebate] > 0)
                idxs = (df['mpo'] == mpo)
                #ax.scatter(df['year'], df[f'{kaya}_pct'], label=info[0], color=info[1])
                ax.scatter(df.loc[idxs, 'year'], df.loc[idxs, f'{kaya}_pct'], label=mpo.replace('_and_',' & '), alpha=0.3, marker=m)

            ax.set_ylabel("Kaya factor percent change")
            ax.set_xlabel("Year")
            
            plt.legend(ncol=4, fontsize=8)
            plt.title(kaya)
            plt.savefig(f"plots/{save_name}_correlations_pct_year_{kaya.replace('/','_per_')}.png")
            plt.close()


# Aggregate all mpo data files into one df
def aggregate_mpos():

    for i, mpo in enumerate(mpo_map.keys()):
        if i == 0:
            master = pd.read_csv(f'data/{mpo}.csv')
            mpo_col = [mpo for _ in range(len(master.index))]
            master['mpo'] = mpo_col
            #master = master.set_index(['mpo', 'year'])
        else:
            df = pd.read_csv(f'data/{mpo}.csv')
            mpo_col = [mpo for _ in range(len(df.index))]
            df['mpo'] = mpo_col
            #df = df.set_index(['mpo', 'year'])
            master = master.append(df)

    return master


make_cvrp_summary = True
make_cvrp_summary = False
prep_mpo_data = True
prep_mpo_data = False
plot_per_mpo_data = True
plot_per_mpo_data = False
plot_agg_mpo_data = True
#plot_agg_mpo_data = False

mpo_map = helpers.get_mpo_map()

years = [y for y in range(2001, 2018)]

print(years)

if make_cvrp_summary:
    print("Opening CVRP rebate file")
    df_cvrp = open_cvrp_rebate_file()
    get_cvrp_rebate_info(df_cvrp, helpers.get_all_counties())

if prep_mpo_data:
    print("prep_mpo_data")
    for mpo, info in mpo_map.items():
        print(mpo)
        print(f"Counties: {info['counties']}")
        stitch_mpo_data(mpo, info)

if plot_per_mpo_data:
    print("plot_per_mpo_data")

    for mpo, info in mpo_map.items():
        df = pd.read_csv(f'data/{mpo}.csv')
        plot_relative_changes(df, mpo)
        plot_relative_changes_Kaya(df, mpo)
        plot_simple_Kaya_decomposition(df, mpo)
        plot_simple_correlations(df, mpo)

if plot_agg_mpo_data:
    print("plot_agg_mpo_data")

    df = aggregate_mpos()
    plot_simple_correlations(df, 'AGGREGATE')
    plot_agg_simple_correlations(df, 'AGGREGATE')
