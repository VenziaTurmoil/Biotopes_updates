import geopandas as gpd
import requests
from requests.auth import HTTPBasicAuth


# PARAMS
USERNAME = 'thierry'
PASSWORD = 'thierry'

url = 'https://gisdemo.anf.etat.lu/geoserver/carto/wfs'
layer_name = 'carto:version_intermediaire'

"""
Transforme une couche distante en WFS en GeoDataFrame
@params url: url du server WFS
@params layer_name: nom du layer
@return data: GeoDataFrame
"""
def WFS_to_DataFrame(url, layer_name):

    # Specify the parameters for fetching the data
    # Count: specificies amount of rows to return (e.g. 10000 or 100)
    # startIndex: specifies at which offset to start returning rows
    params = dict(service='WFS', version="2.0.0", request='GetFeature',
          typeName=layer_name, outputFormat='json')

    # Parse the URL with parameters
    wfs_request = requests.get(
                              url,
                              params=params,
                              auth=HTTPBasicAuth(USERNAME, PASSWORD),
                              verify=False)

    # Read data from URL
    data = gpd.GeoDataFrame.from_features(wfs_request.json()["features"])

    return data


"""
Transforme un GeoDataFrame en couche distante WFS
@params url: url du server WFS
@params layer_name: nom du layer
"""
def DataFrame_to_WFS(url, layer_name):

    # Empty temporary layer

    # Fill temporary layer

    # Save layer to GeoServer