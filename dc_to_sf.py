import geopandas as gpd
import pandas as pd
import numpy as np

"""
A partir d'une documentation du changement, réalise la version finale

@params dc: DataFrame
@return DataFrame
"""
def dc_to_sf(dc):

    # Liste les géocodes à traiter
    M1_Geocodes = dc['M1_Geocode'].rename('Geocode')
    E_Geocodes = dc['Geocode']

    geocodes = pd.concat([E_Geocodes, M1_Geocodes])
    geocodes = geocodes.drop_duplicates().dropna()

    # Traitement Principal
    for geocode in geocodes:

        # Toutes les lignes traitant ce geocode
        historique = dc[dc['M1_Geocode'] == geocode or (dc['Geocode'] == geocode and dc.notna()['M1_Jahr'])]

        # Triées par date
        historique['_date'] = historique['E_Jahr']
        historique.update(historique['M1_Jahr'].rename('_date'))
        historique = historique.sort_values(by=['_date'])

        # Initialisation du traitement

        traite = traitement_historique(historique, gpd.GeoDataFrame())


"""
Traite l'historique d'un biotope avec un algorithme récursif
En particulier, trie les types de changement et redirige vers le traitement appropprié

@params historique: GeoDataFrame
@params result: GeoDataFrame
@return: GeoDataFrame
"""
def traitement_historique(historique, result):

    # Condition d'arret
    if len(historique) == 0:
        return result

    # Param
    if len(historique) > 1:
        next_date = historique.iloc[1]['_date']
    else:
        next_date = np.nan

    # Traitement
    changement = historique.head(1)

    if changement.isna()['M1_Ver']:
        new_result = traitement_etat_initial(changement)

    elif changement['M1_Ver'] == 'X':
        new_result = traitement_extension(changement, result)

    elif changement['M1_Ver'] == 'R':
        new_result = traitement_reduction(changement, result)

    elif changement['M1_Ver'] == 'W':
        new_result = traitement_suppression(changement)

    elif changement['M1_Ver'] == 'N':
        new_result = traitement_nouveau(changement)

    elif changement['M1_Ver'].isin(['A', 'D', '0', 'M']):
        new_result = traitement_conservation(changement, result)

    elif changement['M1_Ver'] == 'E':
        new_result = traitement_echo(changement, result)

    else:
        raise Exception('Type de M1_Ver non supporté')

    new_result['Fin'] = next_date

    # Recursivité
    new_histo = historique.tail(-1)
    return traitement_historique(new_histo, new_result)



"""
Traite l'état initlal du biotope

@params changement: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_etat_initial(changement):
    # Construction de la nouvelle feature selon les champs en entree
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['Geocode'],
            'SF_Aufnanr':changement['E_Aufnanr'],
            'SF_Btyp1_co':changement['E_Btyp1_co'],
            'SF_Subtyp':changement['E_Subtyp'],
            'SF_Bew_Inv1':changement['E_Bew_Inv1'],
            'SF_Bew_Str1':changement['E_Bew_Str1'],
            'SF_Bew_Bee1':changement['E_Bew_Bee1'],
            'SF_Bewert_1':changement['E_Bewert_1'],
            'SF_Kartiere':changement['E_Kartiere'],
            'Link':changement['Link'],
            'SF_Milieu':changement['E_Milieu'],
            'SF_Origin':changement['E_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')
    return new_result

"""
Traite le changement de l'état du biotope

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_conservation(changement, result):
    new_result = gpd.GeoDataFrame({
            'Objectid':result['Objectid'],
            'Gemeinde':result['Gemeinde'],
            'Geocode':result['Geocode'],
            'SF_Aufnanr':changement['M1_Aufnanr'],
            'SF_Btyp1_co':changement['M1_Btyp1_co'],
            'SF_Subtyp':changement['M1_Subtyp'],
            'SF_Bew_Inv1':changement['M1_Bew_Inv1'],
            'SF_Bew_Str1':changement['M1_Bew_Str1'],
            'SF_Bew_Bee1':changement['M1_Bew_Bee1'],
            'SF_Bewert_1':changement['M1_Bewert_1'],
            'SF_Kartiere':changement['M1_Kartiere'],
            'Link':changement['Link'],
            'SF_Milieu':changement['M1_Milieu'],
            'SF_Origin':changement['M1_Origin'],
            'Debut':changement['_date'],
            'geometry':result['geometry']
        }, geometry='geometry', crs='EPSG:2169')
    return new_result

"""
Traite une extension du biotope

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_extension(changement, result):
    new_result = traitement_conservation(changement, result)
    new_result.geometry.union(changement.geometry)
    return new_result

"""
Traite une réduction du biotope

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_reduction(changement, result):
    new_result = traitement_conservation(changement, result)
    new_result.geometry.difference(changement.geometry)
    return new_result

"""
Traite la suppression du biotope

@params changement: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_suppression(changement):
    new_result = traitement_etat_initial(changement)
    new_result.geometry = np.nan
    return new_result

"""
Traite l'ajout d'un nouveau biotope

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_nouveau(changement):
    new_result = gpd.GeoDataFrame({
            'Objectid':changement['Objectid'],
            'Gemeinde':changement['Gemeinde'],
            'Geocode':changement['M1_Geocode'],
            'SF_Aufnanr':changement['M1_Aufnanr'],
            'SF_Btyp1_co':changement['M1_Btyp1_co'],
            'SF_Subtyp':changement['M1_Subtyp'],
            'SF_Bew_Inv1':changement['M1_Bew_Inv1'],
            'SF_Bew_Str1':changement['M1_Bew_Str1'],
            'SF_Bew_Bee1':changement['M1_Bew_Bee1'],
            'SF_Bewert_1':changement['M1_Bewert_1'],
            'SF_Kartiere':changement['M1_Kartiere'],
            'Link':changement['Link'],
            'SF_Milieu':changement['M1_Milieu'],
            'SF_Origin':changement['M1_Origin'],
            'Debut':changement['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')
    return new_result

"""
Traite le changement de géométrie du biotope, du à de l'écho

@params changement: GeoDataFrame
@params result: GeoDataFrame
@return: @GeoDataFrame
"""
def traitement_echo(changement, result):
    new_result = gpd.GeoDataFrame({
            'Objectid':result['Objectid'],
            'Gemeinde':result['Gemeinde'],
            'Geocode':result['Geocode'],
            'SF_Aufnanr':result['SF_Aufnanr'],
            'SF_Btyp1_co':result['SF_Btyp1_co'],
            'SF_Subtyp':result['SF_Subtyp'],
            'SF_Bew_Inv1':result['SF_Bew_Inv1'],
            'SF_Bew_Str1':result['SF_Bew_Str1'],
            'SF_Bew_Bee1':result['SF_Bew_Bee1'],
            'SF_Bewert_1':result['SF_Bewert_1'],
            'SF_Kartiere':result['SF_Kartiere'],
            'Link':result['Link'],
            'SF_Milieu':result['SF_Milieu'],
            'SF_Origin':result['SF_Origin'],
            'Debut':result['_date'],
            'geometry':changement['geometry']
        }, geometry='geometry', crs='EPSG:2169')
    return new_result
