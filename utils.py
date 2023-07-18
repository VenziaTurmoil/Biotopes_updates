import geopandas as gpd
import requests
from requests.auth import HTTPBasicAuth
import configparser
import os
from owslib.wfs import WebFeatureService
from owslib.util import Authentication
import certifi

"""
Reads config file
see https://stackoverflow.com/questions/19379120/how-to-read-a-config-file-using-python
"""
def read_config():
    config_parser = configparser.RawConfigParser()
    config_parser.read('./config.cfg')

    return dict(config_parser.items('CONFIGURATION'))

config = read_config()

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
                              auth=HTTPBasicAuth(config['username'], config['password']),
                              verify=False)

    # Read data from URL
    data = gpd.GeoDataFrame.from_features(wfs_request.json()["features"])

    return data


"""
Transforme un GeoDataFrame en couche distante WFS
@params url: url du server WFS
@params layer_name: nom du layer

NE FONCTIONNE PAS
"""
def DataFrame_to_WFS(df, url, layer_name):

    # Create the XML representation of the feature to be inserted
    xml = df.to_xml()

    data = """<wfs:Transaction
    xmlns:wfs="http://www.opengis.net/wfs"
    service="WFS"
    version="2.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.opengis.net/wfs
    http://schemas.opengis.net/wfs/2.0.0/WFS-transaction.xsd">
    <wfs:Insert>{xml}
    </wfs:Insert>
    </wfs:Transaction>""".format(xml=xml)

    data=data.encode() #will produce bytes object encoded with utf-8

    headers = {
    'Content-Type': 'application/xml'}

    # Insert the feature into the WFS server
    wfs_request = requests.post(
                              url,
                              headers=headers,
                              data=data,
                              auth=HTTPBasicAuth(config['username'], config['password']),
                              verify=False)





url = 'https://gisdemo.anf.etat.lu/geoserver/carto/wfs'
layer_name = 'carto:version_intermediaire'

df = gpd.read_file('H:/AfterMO/input/BTK_S_1.2.shp')
r = DataFrame_to_WFS(df, url, layer_name)
df2 = WFS_to_DataFrame(url, layer_name)