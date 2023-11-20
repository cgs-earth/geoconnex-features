# geoconnex-features
This repository hosts code to download, process, and deploy provisional OGC-API features endpoints for persistently-identified features within prominent water data products for technology demonstration purposes for the [geoconnex harvester](https://github.com/internetofwater/harvest.geoconnex.us) and [knowledge graph](https://graph.geoconnex.us), as well as the [Network-Linked Data Index](https://waterdata.usgs.gov/blog/nldi-intro/) . These features are meant for experimental purposes, and will be retired in favor of authoritative versions published by the original provider organizations if and when they participate in the geoconnex system. 

Datasets are organized in the `collections` directory. 

The features are deployed as Geoconnex-compliant landing pages with JSON-LD embedded metadata at https://features.internetofwater.dev. The deployment configuration for these pages is in the `pygeoapi` directory. The data is hosted in [Hydroshare](https://www.hydroshare.org/resource/495b65e56e994289baaa5feeb401358e/).



## Targeted datasets

### NPDES
 - https://watersgeo.epa.gov/arcgis/rest/services/OWRAD_NP21
 
### State Streamgages

#### CA
 - https://cdec.water.ca.gov/queryTools.html

#### WY
 - https://seoflow.wyo.gov

#### CO
 - https://dwr.state.co.us/tools/stations?stations=all

#### NM

#### OR

#### WA

#### ID

 - https://watersgeo.epa.gov/arcgis/rest/services/OWRAD_NP21

### USGS
 - [https://labs.waterdata.usgs/sta/v1.1](https://labs.waterdata.usgs.gov/sta/v1.1)

### MS4
 -  https://catalog.data.gov/dataset/municipal-stormwater-permit-outfall-data
