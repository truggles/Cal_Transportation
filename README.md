# Cal_Transportation
Research into the impacts of California policy on transportation and GHG emissions.




# Data sources

## Population

Using State of CA Dept of Finance historical values: http://www.dof.ca.gov/Forecasting/Demographics/Estimates/
 * See E-4 Historical Population Estimates for Cities, Counties, and the State:
   * `E-4_2019InternetVersion.xls`
   * 2000-2010 currently has a broken link

## GDP

Local Area Gross Domestic Product from U.S. Bureau of Economic Analysis: 
 * Current 2015-2018 data: https://www.bea.gov/data/gdp/gdp-county-metro-and-other-areas
   * `BEA_Real_Gross_Domestic_Product_by_County_2015-2018.xlsx`
 * Archives: https://apps.bea.gov/regional/histdata/
   * Gross Domestic Product by Metropolitan Area, Advance 2017, and Revised 2001-2016: `gdpmetro0918.zip`, copied all `*_CA_*` files to `data/gdp` directory

## VMT

Options include using Caltrans Highway Performance Monitoring System (HPMS) Data which has VMT by MPO
   * https://dot.ca.gov/programs/research-innovation-system-information/highway-performance-monitoring-system
   * CARB has mentioned issues with their regional data see Nov 2018 report (https://ww2.arb.ca.gov/resources/documents/tracking-progress) Appendix A

## VMT & Energy Intensity & GHG

Alternative is to use CARB's model EMFAC2017
 * https://ww2.arb.ca.gov/our-work/programs/mobile-source-emissions-inventory/msei-modeling-tools
 * Actual web database: https://www.arb.ca.gov/emfac/2017/
 * benefit of being synced with CARB's policy work
 * only runs on Windows (I need to use web database)
 * can decompose data regionally by: MPO, county, sub-region, state level
 * have downloaded data for 2 counties: Alameda and San Mateo
   * `data/EMFAC2017/`
   * From web databased used:
     * data type = emissions
     * region = county --> San Mateo / Alameda
     * calendar year = 2000 through 2020
     * season = annual
     * vehicle categories = EMFAC2011 categories: LDA, LDT1, LDT2, MDV, MCY, LHD1, LHD2 (need to figure out of the last 4 are included in LDV policy and regulations)
     * model year = aggregated (could do interesting work with retirement)
     * speed = aggregated
     * fuel = all

## Vehicle definitions

From EMFAC2017 Volume III - Technical Documentation:
EMFAC2017 uses EMFAC2011 vehicle and technology classifications.  See table on pdf 202, Table 6.1-1 "Summary List of Vehicle Classes"
- LDA = passenger cars
- LDT1 = Light-Duty Trucks (GVWR <6000 lbs. and ETW <= 0-3750 lbs) 
- LDT2 = Light-Duty Trucks (GVWR <6000 lbs. and ETW 3751-5750 lbs) 

From Institute for Local Government: https://www.ca-ilg.org/post/basics-sb-375

 * "SB 375, authored by Senator Darrell Steinberg, directs the Air Resources Board to set regional targets for the reduction of greenhouse gas emissions. Aligning these regional plans is intended to help California achieve GHG reduction goals for cars and light trucks under AB 32, the state’s landmark climate change legislation."

We only deal with codes LDA, LDT1, LDT2 (to be confirmed)
