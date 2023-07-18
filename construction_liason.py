import geopandas as gpd

"""
Réalise une jointure spatiale entre deux DataFrame et en résulte une table de
liaison.
Par exemple, la table résultante peut donner la concordance entre les anciens
et les nouveaux biotopes.

@params old_df: GeoDataFrame
@params new_df: GeoDataFrame
@returns: GeoDataFrame 
"""
def jointure(old_df, new_df):
    
    # # Jointure spatiale : Tous les attributs mais ligne par ligne
    # old_df_joined = old_df.sjoin(new_df, how='inner', lsuffix='old_', rsuffix='new_')
    # new_df_joined = new_df.sjoin(new_df, how='inner', lsuffix='new_', rsuffix='old_')
    
    # Intersection de toutes les géométries entre elles
    # indice df1, indice df2, geometries
    overlay_intersection = old_df.overlay(new_df, how='intersection')
    valid_overlay = remove_invalid_geoms(overlay_intersection, 1) # SEUIL D' UN METRE CARRÉ
    
    # Remplie la table des colonnes des deux DataFrames initiaux
    joined_temp = valid_overlay.join(old_df, on='old_df', rsuffix='old_')
    joined = joined_temp.join(new_df, on='new_df', rsuffix='new_')
    
    # Selection des colonnes qui nous interessent
    # geometry fait référence aux intersections
    res = joined[['old_Geocode', 'new_Geocode', 'geometry']]
    
    return res



"""
Retire les géométries invalides et celles qui ont une aire inférieure au seuil

@params df: GeoDataFame
@params seuil: float
"""
def remove_invalid_geoms(df, seuil):
    # Selectionne les geometries voulues
    geom = df.geometry
    valid_geom = geom[geom.is_valid()]
    big_geom = valid_geom[valid_geom.area > seuil]
    # Selection des lignes de la table ayant une geometrie valide
    res_df = df[big_geom.index]
    
    return res_df


