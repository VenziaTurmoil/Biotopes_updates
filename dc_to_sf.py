import geopandas as gpd
import pandas as pd
import numpy as np

SF_COLUMNS = [
    'Objectid',
    'Gemeinde',
    'Geocode',
    'SF_Aufnanr',
    'SF_Btyp',
    'SF_Subtyp',
    'SF_Bew_Inv',
    'SF_Bew_Str',
    'SF_Bew_Bee',
    'SF_Bew_Ges',
    'SF_Kartiere',
    'Link',
    'SF_Milieu',
    'SF_Origin',
    'Debut',
    'geometry'
]


"""
A partir d'une documentation du changement, réalise la version finale

@params dc: DataFrame
@return DataFrame
"""
def dc_to_sf(dc):

    # INITIALISATION

    # Trie la documentation du changement par date de modification
    dc['_date'] = dc['E_Jahr']
    dc['_date'].update(dc['M1_Jahr'])
    # Et par les types de modifications, dans le bon sens
    dc['M1_Ver'] = pd.Categorical(dc['M1_Ver'], ['N', 'W', 'R', 'A', 'D', '0', 'M', 'X', 'E'])
    dc = dc.sort_values(by='M1_Ver')
    dc = dc.sort_values(by=['_date', 'Geocode', 'M1_Geocode'])

    sf = gpd.GeoDataFrame(columns=SF_COLUMNS, geometry='geometry', crs=dc.crs)

    # RECURENCE
    # DISCLAIMER: We iterate over DataFrames rows even though it is not recommended for a reason:
        # We need the result of the previous rows before computing the next -> Sequential Processing
        # Please refer to https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    for index, changement in dc.iterrows():
        sf = traitement_changement(changement, sf)

    return sf






"""
Traite un changement d'un biotope en général
Concrètement, trie les types de changement et redirige vers le traitement appropprié

@params changement: GeoDataFrame
@params sf: GeoDataFrame
@return: GeoDataFrame
"""
def traitement_changement(changement, sf):

    if changement.isna()['M1_Ver'].squeeze():
        result = traitement_etat_initial(changement, sf)

    elif changement['M1_Ver'] == 'X'.squeeze():
        result = traitement_extension(changement, sf)

    elif changement['M1_Ver'] == 'R'.squeeze():
        result = traitement_reduction(changement, sf)

    elif changement['M1_Ver'] == 'W'.squeeze():
        result = traitement_suppression(changement, sf)

    elif changement['M1_Ver'] == 'N'.squeeze():
        result = traitement_nouveau(changement, sf)

    elif changement['M1_Ver'].isin(['A', 'D', '0', 'M'].squeeze()):
        result = traitement_modification(changement, sf)

    elif changement['M1_Ver'] == 'E'.squeeze():
        result = traitement_echo(changement, sf)

    else:
        raise Exception('Type de M1_Ver non supporté')

    return result



"""
Traite l'état initlal du biotope

@params changement: GeoDataFrame
@params sf: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_etat_initial(changement, sf):
    # Construction de la nouvelle feature selon les champs en entree
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['Geocode'],
            'SF_Aufnanr':changement['E_Aufnanr'],
            'SF_Btyp':changement['E_Btyp1_co'],
            'SF_Subtyp':changement['E_Subtyp'],
            'SF_Bew_Inv':changement['E_Bew_Inv1'],
            'SF_Bew_Str':changement['E_Bew_Str1'],
            'SF_Bew_Bee':changement['E_Bew_Bee1'],
            'SF_Bew_Ges':changement['E_Bewert_1'],
            'SF_Kartiere':changement['E_Kartiere'],
            'Link':changement['Link'],
            'SF_Milieu':changement['E_Milieu'],
            'SF_Origin':changement['E_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')
    return sf.append(new_result, ignore_index=True)


"""
Traite le changement de modification du biotope

@params changement: GeoDataFrame
@params sf: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_modification(changement, sf):

    # Construction de la novelle entrée
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['M1_Geocode'],
            'SF_Aufnanr':changement['M1_Aufnanr'],
            'SF_Btyp':changement['M1_Btyp'],
            'SF_Subtyp':changement['M1_Subtyp'],
            'SF_Bew_Inv':changement['M1_Bew_Inv'],
            'SF_Bew_Str':changement['M1_Bew_Str'],
            'SF_Bew_Bee':changement['M1_Bew_Bee'],
            'SF_Bew_Ges':changement['M1_Bew_Ges'],
            'SF_Kartiere':changement['M1_Kartier'],
            'Link':changement['Link'],
            'SF_Milieu':changement['M1_Milieu'],
            'SF_Origin':changement['M1_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')

    # Mise en place des effets de bords
    new_sf = sf.copy()
    state = sf[sf['Geocode'] == changement['M1_Geocode']].tail(1) # Dernier changement avant celui la
    if not state.empty:
        # Fusion des geométries
        if not new_result['geometry'].is_empty().squeeze(): # Condition pour s'assurer des cas polygon -> point
            new_result['geometry'] = new_result.union(state)
        # Date de fin sur l'ancien changement
        new_sf['Fin'].loc[state.index] = new_result['Debut']

    return new_sf.append(new_result, ignore_index=True)


"""
Traite une extension du biotope

@params changement: GeoDataFrame
@params sf: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_extension(changement, sf):

    # Construction de la novelle entrée
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['M1_Geocode'],
            'SF_Aufnanr':changement['M1_Aufnanr'],
            'SF_Btyp':changement['M1_Btyp'],
            'SF_Subtyp':changement['M1_Subtyp'],
            'SF_Bew_Inv':changement['M1_Bew_Inv'],
            'SF_Bew_Str':changement['M1_Bew_Str'],
            'SF_Bew_Bee':changement['M1_Bew_Bee'],
            'SF_Bew_Ges':changement['M1_Bew_Ges'],
            'SF_Kartiere':changement['M1_Kartier'],
            'Link':changement['Link'],
            'SF_Milieu':changement['M1_Milieu'],
            'SF_Origin':changement['M1_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')

    # Mise en place des effets de bords
    new_sf = sf.copy()
    state = sf[sf['Geocode'] == changement['M1_Geo_Par']].tail(1) # Différence avec traitement_modification
    if not state.empty:
        # Fusion des geométries
        new_result['geometry'] = new_result.union(state)
        new_sf['Fin'].loc[state.index] = new_result['Debut']

    return new_sf.append(new_result, ignore_index=True)



"""
Traite une réduction du biotope

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_reduction(changement, sf):

    # Construction de la novelle entrée
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['Geocode'],
            'SF_Aufnanr':changement['E_Aufnanr'],
            'SF_Btyp':changement['E_Btyp1_co'],
            'SF_Subtyp':changement['E_Subtyp'],
            'SF_Bew_Inv':changement['E_Bew_Inv1'],
            'SF_Bew_Str':changement['E_Bew_Str1'],
            'SF_Bew_Bee':changement['E_Bew_Bee1'],
            'SF_Bew_Ges':changement['E_Bewert_1'],
            'SF_Kartiere':changement['E_Kartiere'],
            'Link':changement['Link'],
            'SF_Milieu':changement['E_Milieu'],
            'SF_Origin':changement['E_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')

    # Mise en place des effets de bords
    new_sf = sf.copy()
    state = sf[sf['Geocode'] == changement['Geocode']].tail(1) # Dernier changement avant celui la
    if not state.empty:
        # Fusion des geométries
        new_result['geometry'] = new_result.difference(state)
        if state['Debut'] == new_result['Debut']:
            # Fusion de multiples modifications la même année
            new_sf = sf.drop(state.index)
        else:
            # Date de fin sur l'ancien changement
            new_sf['Fin'].loc[state.index] = new_result['Debut']

    return new_sf.append(new_result, ignore_index=True)


"""
Traite la suppression du biotope i

@params changement: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_suppression(changement, sf):


    # Mise en place des effets de bords
    new_sf = sf.copy()
    state = sf[sf['Geocode'] == changement['Geocode']].tail(1) # Dernier changement avant celui la
    if not state.empty:

        # Date de fin sur l'ancien changement
        new_sf['Fin'].loc[state.index] = changement['Debut']

    return new_sf


"""
Traite l'ajout d'un nouveau biotope

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_nouveau(changement, sf):
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['M1_Geocode'],
            'SF_Aufnanr':changement['M1_Aufnanr'],
            'SF_Btyp':changement['M1_Btyp'],
            'SF_Subtyp':changement['M1_Subtyp'],
            'SF_Bew_Inv':changement['M1_Bew_Inv'],
            'SF_Bew_Str':changement['M1_Bew_Str'],
            'SF_Bew_Bee':changement['M1_Bew_Bee'],
            'SF_Bew_Ges':changement['M1_Bew_Ges'],
            'SF_Kartiere':changement['M1_Kartiere'],
            'Link':changement['Link'],
            'SF_Milieu':changement['M1_Milieu'],
            'SF_Origin':changement['M1_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')

    return sf.append(new_result, ignore_index=True)


"""
Traite le changement de géométrie du biotope, du à de l'écho

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_echo(changement, sf):

    new_sf = sf.copy()
    state = sf[sf['Geocode'] == changement['M1_Geocode']].tail(1)

    new_result = gpd.GeoDataFrame({
            'Objectid':state['Objectid'],
            'Gemeinde':state['Gemeinde'],
            'Geocode':state['Geocode'],
            'SF_Aufnanr':state['SF_Aufnanr'],
            'SF_Btyp':state['SF_Btyp'],
            'SF_Subtyp':state['SF_Subtyp'],
            'SF_Bew_Inv':state['SF_Bew_Inv'],
            'SF_Bew_Str':state['SF_Bew_Str'],
            'SF_Bew_Bee':state['SF_Bew_Bee'],
            'SF_Bew_Ges':state['SF_Bew_Ges'],
            'SF_Kartiere':state['SF_Kartiere'],
            'Link':state['Link'],
            'SF_Milieu':state['SF_Milieu'],
            'SF_Origin':state['SF_Origin'],
            'Debut':state['_date'],
            'geometry':changement['geometry'] # Seul champ changé
        }, geometry='geometry', crs='EPSG:2169')

    if not state.empty:
            # Date de fin sur l'ancien changement
            new_sf['Fin'].loc[state.index] = new_result['Debut']

    return new_sf.append(new_result, ignore_index=True)
