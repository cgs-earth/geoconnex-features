import arcpy

# Set the workspace environment
arcpy.env.workspace = r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb"

# reassign variable name
MT_gage = "MT_gages"

# Define a list of field names and their types
field_list = [
    ("uri", "TEXT"),
    ("name", "TEXT"),
    ("id", "TEXT"),
    ("provider_name", "TEXT"),
    ("provider_id", "TEXT"),
    ("provider_url", "TEXT"),
    ("provider_code", "TEXT"),
    ("mainstem_uri", "TEXT"),
    ("comid", "TEXT")
]

# Add the new fields using a loop
for field_name, field_type in field_list:
    arcpy.AddField_management(MT_gage, field_name, field_type)

# Confirm the field addition
field_names = [field.name for field in arcpy.ListFields(MT_gage)]
print("Fields in the layer after addition:", field_names)

## Get unique ID, which comes from Site_Name

# Create an update cursor to iterate through the rows
with arcpy.da.UpdateCursor(MT_gage, ['LocationCode', 'id']) as cursor:
    for row in cursor:
        # Get the Site_Name value
        site_name = row[0]

        # Remove spaces and assign the result to the 'id' field
        row[1] = site_name.replace(" ", "")

        # Update the row
        cursor.updateRow(row)

# Clean up the cursor
del cursor

# Set name = id
# Define the expression for the field calculation
expression = "!id!"  # Set the 'name' field equal to the 'id' field

# Perform the field calculation
arcpy.management.CalculateField(MT_gage, "name", expression, "PYTHON3")

print("id and name fields populated")

# Confirm unique ID in identifier field
# Field to check for uniqueness
field_name = "id"

# Use a set to keep track of unique values encountered in the field
unique_values = set()

# Initialize a counter to keep track of the total number of rows
total_rows = 0

# Initialize a flag to check for spaces
has_spaces = False

# Start a search cursor to iterate through the rows and check for unique values and spaces
with arcpy.da.UpdateCursor(MT_gage, field_name) as cursor:
    for row in cursor:
        total_rows += 1
        value = row[0]
        if value in unique_values:
            print(f"Non-unique value found: {value}")
        else:
            unique_values.add(value)

        if " " in value:
            has_spaces = True
            # Replace spaces with "-"
            row[0] = value.replace(" ", "-")
            cursor.updateRow(row)

# Check if the number of unique values is the same as the total number of rows
if len(unique_values) == total_rows:
    print("All values in the 'Identifier' field are unique.")
else:
    print("There are duplicate values in the 'Identifier' field.")

# Check if there are any spaces in the 'Identifier' field
if has_spaces:
    print("There were spaces in the 'Identifier' field. They have been replaced with '-'.")
else:
    print("No spaces found in the 'Identifier' field.")


#Update Fields

arcpy.CalculateField_management(MT_gage, "provider_name", "'Montana Department of Natural Resources and Conservation'")
#Updated to Montana
arcpy.CalculateField_management(MT_gage, "provider_url", '"https://gis.dnrc.mt.gov/apps/stage/"', "PYTHON3")
arcpy.CalculateField_management(MT_gage, "provider_id", '"{}"'.format('"!id!"'), "PYTHON3")
arcpy.CalculateField_management(MT_gage, "provider_code", "'mtdnrc'")

print("Fields calculated")

#create url
codeblock = """
def url_join(*parts: list) -> str:
    return '/'.join([str(p).strip().strip('/') for p in parts])
"""
##geoconnex.us/ndwr/gages/id

expression = """url_join("https://geoconnex.us/mtdnrc/gages", !id!)"""
arcpy.management.CalculateField(MT_gage, "uri", expression, "PYTHON3", codeblock)
print("uri calculated")



import requests
import pandas as pd
# Define the URL of the REST API endpoint
url = "https://gis.dnrc.mt.gov/arcgis/rest/services/WRD/WMB_StAGE/MapServer/3/query"
# Define the parameters for your request
params = {
    "where": "1=1",  # This is a simple query to get all records
    "outFields": "*",  # This will include all fields in the response
    "f": "json",  # You can request data in JSON format
}
# Make a GET request to the API
response = requests.get(url, params=params)
# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Extract the features from the response
    features = [v['attributes'] for v in data['features']]

    df = pd.json_normalize(features)
        
    # Specify the full path for saving the CSV file
    save_path = r'C:\Users\ewiggans\Desktop\GeoConnexMap\MontanaGage\MT_stations_data.csv'
      
    # Save the DataFrame to the specified CSV file
    df.to_csv(save_path, index=False)
    print(f"Data downloaded and saved as '{save_path}'")
else:
    print("Failed to retrieve data. Status code:", response.status_code)

df.head()

# Assuming you have already loaded data into the DataFrame 'df'

#get unique ids for the site name from location code, but remove spaces
df['Site_name'] = df['LocationCode']
# Remove spaces in the "Site_name" field
df['Site_name'] = df['Site_name'].str.replace(' ', '')# 
df["about_uri"] = "https://geoconnex.us/mtdnrc/gages/" + df['Site_name']

# # Update format of Montana gages using a lambda function
df["url"] = df["SensorCode"].apply(lambda x: f"https://gis.dnrc.mt.gov/arcgis/rest/services/WRD/WMB_StAGE/MapServer/3/query?where=SensorCode='{x.replace(' ', '+')}'")

#Calculate other fields 
df["provider_code"] = "mtdnrc"
df["name"] = df["SensorCode"]
df["parameter_id"] = df["provider_code"] + "-" + df["ParameterLabel"]
df["parameter_name"] = df['SensorCode'].str.split('@').str[0]
df["parameter_group"] = df["ParameterLabel"]

print("Complete")


df.head()

# Print the first five rows of the "data_set_url" column
pd.options.display.max_colwidth = 300
print(df["url"].head())

#Perform final field calculations on pandas DataFrame

end_df = df[["about_uri", "url", "name", "provider_code", "parameter_id", "parameter_name", "parameter_group"]]
end_df.head()
end_df.to_csv("C:\\Users\\ewiggans\\Desktop\\GeoConnexMap\\MontanaGage\\MT_download_table.csv")
#Export and write to new CSV
print("Exported to csv")

import json
import requests
from shapely.geometry import shape, Point


def get_comid_intersect(geom):
    # Convert the input geom to GeoJSON using Shapely
    point = Point(geom)

    # Convert the Point to GeoJSON
    geom_geojson = shape(point).__geo_interface__

    url = 'https://nhdpv2-census.internetofwater.app/collections/2020/items?filter-lang=cql-json'
    filter_ = {
        'intersects': [
            {'property': 'shape'},
            geom_geojson  # Use the Shapely-converted GeoJSON
        ]
    }
    headers = {
        'Content-Type': 'application/query-cql-json'
    }
    r = requests.post(url, headers=headers, json=filter_)
    fc = r.json()
    if 'features' in fc and len(fc['features']) > 0:
        feature = fc['features'][0]
        return feature['properties']['featureid']
    else:
        return None

# Update Cursor
with arcpy.da.UpdateCursor(MT_gage, ["Shape", "comid"]) as cursor:
    for row in cursor:
        geom = row[0]
        comid = get_comid_intersect(geom)
        if comid is not None:
            print(comid, end='\r', flush=True)
            row[1] = comid
            cursor.updateRow(row)


print("comid calculated")

# Read in the CSV file as a geodatabase table
csv_table = r"C:\\Users\\ewiggans\\Desktop\\GeoConnexMap\\MontanaGage\\nhdpv2_lookup.csv"
csv_table_name = "NHDPV2_Lookup"
arcpy.TableToTable_conversion(csv_table, arcpy.env.workspace, csv_table_name)

# Add a new field 'comid_text' to the CSV table with a data type of TEXT
arcpy.AddField_management(csv_table_name, "comid_text", "TEXT")

# Calculate the 'comid_text' field by copying the values from the 'comid' field
expression = "!comid!"
codeblock = ""
arcpy.CalculateField_management(csv_table_name, "comid_text", expression, "PYTHON3", codeblock)

print("Added 'comid_text' field and set its values equal to 'comid' as text.")



# Join the CSV table to the MT gage feature class based on the "comid" field
arcpy.AddJoin_management(MT_gage, "comid", csv_table_name, "comid_text", "KEEP_COMMON")

# Calculate the "mainstem_uri" field to be equal to the "uri" field in the CSV table
expression = "!{}.uri!".format(csv_table_name)
arcpy.CalculateField_management(MT_gage, "mainstem_uri", expression, "PYTHON3")

# Remove the join to the CSV table
arcpy.RemoveJoin_management(MT_gage, csv_table_name)
print("Complete")


# Define the output GeoJSON file path
output_geojson_file = r"C:\Users\ewiggans\Desktop\GeoConnexMap\MontanaGage\MT_gage_export.geojson"

# Export the feature class to GeoJSON
arcpy.FeaturesToJSON_conversion(in_features = MT_gage, 
                                out_json_file = output_geojson_file,
                                geoJSON = "GEOJSON")
print(f"Exported {MT_gage} to {output_geojson_file} in GeoJSON format.")


