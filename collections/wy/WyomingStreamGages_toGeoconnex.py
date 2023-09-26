import arcpy

# Set the workspace environment
arcpy.env.workspace = r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb"

# Define the input layer
WY_gage = "WyomingStreamGage"

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
    arcpy.AddField_management(WY_gage, field_name, field_type)

# Create an update cursor to delete rows with NULL 'latitude' or 'longitude'
with arcpy.da.UpdateCursor(WY_gage, ['latitude', 'longitude']) as cursor:
    for row in cursor:
        latitude, longitude = row
        if latitude is None or longitude is None:
            cursor.deleteRow()

# Confirm the field addition
field_names = [field.name for field in arcpy.ListFields(WY_gage)]
print("Fields in the layer after addition:", field_names)





# Confirm unique ID in identifier field
# Field to check for uniqueness
field_name = "Identifier"

# Use a set to keep track of unique values encountered in the field
unique_values = set()

# Initialize a counter to keep track of the total number of rows
total_rows = 0

# Initialize a flag to check for spaces
has_spaces = False

# Start a search cursor to iterate through the rows and check for unique values and spaces
with arcpy.da.UpdateCursor(WY_gage, field_name) as cursor:
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



#set Identifier field to id and name
#fields to update
id_field = "id"
name_field = "name"
field_name = "Identifier"

# Calculate the 'id' field and 'name' field using the 'Identifier' field
expression = "!" + field_name + "!"
codeblock = ""

# Use the CalculateField tool to perform the field calculation
arcpy.CalculateField_management(WY_gage, id_field, expression, "PYTHON3", codeblock)
arcpy.CalculateField_management(WY_gage, name_field, expression, "PYTHON3", codeblock)

#print("Updated 'id' and 'name' fields with values from the 'Identifier' field.")

arcpy.CalculateField_management(WY_gage, "provider_name", "'Wyoming State Engineers Office'")
arcpy.CalculateField_management(WY_gage, "provider_url", "'https://seo.wyo.gov/'")
arcpy.CalculateField_management(WY_gage, "provider_id", "!" + field_name +"!")
arcpy.CalculateField_management(WY_gage, "provider_code", "'wyseo'")


#Calculate URI 
codeblock = """
def url_join(*parts: list) -> str:
    return '/'.join([str(p).strip().strip('/') for p in parts])
"""
## pattern for uri is: geoconnex.us/iow/wyseo/gages/id

expression = """url_join("https://geoconnex.us/wyseo/gages", !id!)"""
arcpy.management.CalculateField(WY_gage, "uri", expression, "PYTHON3", codeblock)
print("uri calculated")



##Read in the download table

import pandas as pd
pd.set_option('display.width', 1000)

# Path to the CSV file
csv_file_path = r"C:\Users\ewiggans\Desktop\GeoConnexMap\WyomingGage\List-20230801130904_WYgages.csv"


# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Display the first few rows of the data frame to verify the data
print(df.head())


#View column headers 
df.columns

# Perform the field calculations on the pandas DataFrame
df["location_id"] = df["Data_Set_Id"].str.replace(r".*@", "", regex=True)
df["about_url"] = "https://geoconnex.us/wyseo/gages/" + df["location_id"]
df["data_set_type"] = df["Data_Set_Id"].str.replace(r"@.*", "", regex=True)
df["data_set_path"] = df["data_set_type"].str.replace(".", "/", 1)
df["url"] = "https://seoflow.wyo.gov/Data/DataSet/Summary/Location/" + df["location_id"] + "/DataSet/" + df["data_set_path"]
df["provider_code"] = "wyseo"
df["parameter_name"] = df["data_set_type"]
df["parameter_group"] = "discharge"
df["parameter_id"] = df["provider_code"] + "-" + df["parameter_group"]
df["about_uri"] = df["about_url"]
df["name"] = df["Data_Set_Id"]



df.head()

# Print the first five rows of the "data_set_url" column
pd.options.display.max_colwidth = 300
print(df["url"].head())

#Perform final field calculations on pandas DataFrame

end_df = df[["about_uri", "url", "name", "provider_code", "parameter_id", "parameter_name", "parameter_group"]]
end_df.head()

#Export and write to new CSV

end_df.to_csv("C:\\Users\\ewiggans\\Desktop\\GeoConnexMap\\WyomingGage\\WY_download_table.csv")

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
with arcpy.da.UpdateCursor(WY_gage, ["Shape", "comid"]) as cursor:
    for row in cursor:
        geom = row[0]
        comid = get_comid_intersect(geom)
        if comid is not None:
            print(comid, end='\r', flush=True)
            row[1] = comid
            cursor.updateRow(row)

# Complete
print("comid calculated")

# Read in the CSV file as a geodatabase table
csv_table = r"C:\Users\ewiggans\Desktop\GeoConnexMap\WyomingGage\nhdpv2_lookup.csv"
csv_table_name = "NHDPV2_Lookup"
arcpy.TableToTable_conversion(csv_table, arcpy.env.workspace, csv_table_name)

# Add a new field 'comid_text' to the CSV table with a data type of TEXT
arcpy.AddField_management(csv_table_name, "comid_text", "TEXT")

# Calculate the 'comid_text' field by copying the values from the 'comid' field
expression = "!comid!"
codeblock = ""
arcpy.CalculateField_management(csv_table_name, "comid_text", expression, "PYTHON3", codeblock)

print("Added 'comid_text' field and set its values equal to 'comid' as text.")


# Join the CSV table to the "WyomingStreamGage" feature class based on the "comid" field
arcpy.AddJoin_management(WY_gage, "comid", csv_table_name, "comid_text", "KEEP_COMMON")

# Calculate the "mainstem_uri" field to be equal to the "uri" field in the CSV table
expression = "!{}.uri!".format(csv_table_name)
arcpy.CalculateField_management(WY_gage, "mainstem_uri", expression, "PYTHON3")

# Remove the join to the CSV table
arcpy.RemoveJoin_management(WY_gage, csv_table_name)


# Define the output GeoJSON file path
output_geojson_file = r"C:\Users\ewiggans\Desktop\GeoConnexMap\WyomingGage\WY_gage_export.geojson"

# Export the feature class to GeoJSON
arcpy.FeaturesToJSON_conversion(in_features = WY_gage, 
                                out_json_file = output_geojson_file,
                                geoJSON = "GEOJSON")


print(f"Exported {WY_gage} to {output_geojson_file} in GeoJSON format.")
