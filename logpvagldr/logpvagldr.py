from sentinelhub import SHConfig
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, DataCollection, bbox_to_dimensions

# In case you put the credentials into the configuration file you can leave this unchanged

CLIENT_ID = 'a39d9e89-f1a1-4d32-8533-9354f9dd8834'
CLIENT_SECRET = ')nW]ymsATEvf,!Y%n7,Ra^Hu#!T-(./S4(EV>lcL'


config = SHConfig()

if CLIENT_ID and CLIENT_SECRET:
    config.sh_client_id = CLIENT_ID
    config.sh_client_secret = CLIENT_SECRET

if config.sh_client_id == '' or config.sh_client_secret == '':
    print("Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret).")
   

coord_wgs84 = [72.85,22.38,73.06,22.53]

resolution = 10
coord_bbox = BBox(bbox=coord_wgs84, crs=CRS.WGS84)
coord_size = bbox_to_dimensions(coord_bbox, resolution=resolution)

print(f'Image shape at {resolution} m resolution: {coord_size} pixels')
request_all_bands = SentinelHubRequest(data_folder='Crop_data\RESI',
    evalscript=resi,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=('2020-04-01', '2020-04-10'),
            mosaicking_order='leastCC'
    )],
    responses=[
        SentinelHubRequest.output_response('default', MimeType.TIFF)
    ],
    bbox=coord_bbox,
    size=coord_size,
    config=config
)

request_all_bands.save_data()