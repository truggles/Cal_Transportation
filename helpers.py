





def get_all_counties():
    return [
        'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras',
        'Colusa', 'Contra Costa', 'Del Norte', 'El Dorado',
        'Fresno', 'Glenn', 'Humboldt', 'Imperial',
        'Inyo', 'Kern', 'Kings', 'Lake', 'Lassen', 'Los Angeles',
        'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced',
        'Modoc', 'Mono', 'Monterey', 'Napa', 'Nevada', 'Orange',
        'Placer', 'Plumas', 'Riverside', 'Sacramento', 'San Benito',
        'San Bernardino', 'San Diego', 'San Francisco', 'San Joaquin', 
        'San Luis Obispo', 'San Mateo', 'Santa Barbara', 'Santa Clara', 'Santa Cruz',
        'Shasta', 'Sierra', 'Siskiyou', 'Solano', 'Sonoma',
        'Stanislaus', 'Sutter', 'Tehama', 'Trinity',
        'Tulare', 'Tuolumne', 'Ventura', 'Yolo', 'Yuba'
        ]

def get_counties_with_mpos():

    mpo_map = get_mpo_map()

    counties = []

    for mpo, info in mpo_map.items():
        for county in info['counties']:
            if county not in counties:
                counties.append(county)

    return counties




def get_mpo_map():
    return {
        'MTC_and_AMBAG' : {
            'counties' : [
                'Monterey',
                'San Benito',
                'Santa Cruz',
                'Napa',
                'Alameda',
                'Contra Costa',
                'Marin',
                'San Francisco',
                'San Mateo',
                'Santa Clara',
                'Sonoma',
                'Solano',
            ],
            'gdp_files' : [
                'MAGDP2_CA_Salinas_2001_2017.csv',
                'MAGDP2_CA_San-Jose-Sunnyvale-Santa-Clara_2001_2017.csv',
                'MAGDP2_CA_Santa-Cruz-Watsonville_2001_2017.csv',
                'MAGDP2_CA_Napa_2001_2017.csv',
                'MAGDP2_CA_San-Francisco-Oakland-Hayward_2001_2017.csv',
                'MAGDP2_CA_Santa-Rosa_2001_2017.csv',
                'MAGDP2_CA_Vallejo-Fairfield_2001_2017.csv',
            ]
        },
        'BCAG' : {
            'counties' : ['Butte',],
            'gdp_files' : ['MAGDP2_CA_Chico_2001_2017.csv',]
        },
        'COFCG' : { # was COFCG, set to COFCG to align with EMFAC2017
            'counties' : ['Fresno',],
            'gdp_files' : ['MAGDP2_CA_Fresno_2001_2017.csv',]
        },
        'KCAG' : {
            'counties' : ['Kings',],
            'gdp_files' : ['MAGDP2_CA_Hanford-Corcoran_2001_2017.csv',]
        },
        'KCOG' : {
            'counties' : ['Kern',],
            'gdp_files' : ['MAGDP2_CA_Bakersfield_2001_2017.csv',]
        },
        'MCAG' : {
            'counties' : ['Merced',],
            'gdp_files' : ['MAGDP2_CA_Merced_2001_2017.csv',]
        },
        'MCTC' : {
            'counties' : ['Madera',],
            'gdp_files' : ['MAGDP2_CA_Madera_2001_2017.csv',]
        },
        'SACOG_and_TMPO' : {
            'counties' : [
                'Sacramento',
                'Yolo',
                'Sutter',
                'Yuba',
                'El Dorado',
                'Placer',
            ],
            'gdp_files' : [
                'MAGDP2_CA_Sacramento--Roseville--Arden-Arcade_2001_2017.csv',
                'MAGDP2_CA_Yuba-City_2001_2017.csv',
            ]
        },
        'SANDAG' : {
            'counties' : ['San Diego',],
            'gdp_files' : ['MAGDP2_CA_San-Diego-Carlsbad_2001_2017.csv',]
        },
        'SBCAG' : {
            'counties' : ['Santa Barbara',],
            'gdp_files' : ['MAGDP2_CA_Santa-Maria-Santa-Barbara_2001_2017.csv',]
        },
        'SCAG' : {
            'counties' : [
                'Imperial',
                'Los Angeles',
                'Orange',
                'Ventura',
                'Riverside',
                'San Bernardino'
            ],
            'gdp_files' : [
                'MAGDP2_CA_El-Centro_2001_2017.csv',
                'MAGDP2_CA_Los-Angeles-Long-Beach-Anaheim_2001_2017.csv',
                'MAGDP2_CA_Oxnard-Thousand-Oaks-Ventura_2001_2017.csv',
                'MAGDP2_CA_Riverside-San-Bernardino-Ontario_2001_2017.csv'
            ]
        },
        'SCRTPA' : {
            'counties' : ['Shasta',],
            'gdp_files' : ['MAGDP2_CA_Redding_2001_2017.csv',]
        },
        'SJCOG' : {
            'counties' : ['San Joaquin',],
            'gdp_files' : ['MAGDP2_CA_Stockton-Lodi_2001_2017.csv',]
        },
        'SLOCOG' : {
            'counties' : ['San Luis Obispo',],
            'gdp_files' : ['MAGDP2_CA_San-Luis-Obispo-Paso-Robles-Arroyo-Grande_2001_2017.csv',]
        },
        'StanCOG' : {
            'counties' : ['Stanislaus',],
            'gdp_files' : ['MAGDP2_CA_Modesto_2001_2017.csv',]
        },
        'TCAG' : {
            'counties' : ['Tulare',],
            'gdp_files' : ['MAGDP2_CA_Visalia-Porterville_2001_2017.csv',]
        }
    }
