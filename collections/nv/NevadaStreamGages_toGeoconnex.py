import arcpy

# Set the workspace environment
arcpy.env.workspace = r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb"


arcpy.conversion.ExportFeatures(
    in_features="Monitoring_Sites_Surfacewater",
    out_features=r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb\NV_gages_final",
    where_clause="",
    use_field_alias_as_name="NOT_USE_ALIAS",
    field_mapping='AutoID "AutoID" true true false 4 Long 0 0,First,#,Monitoring_Sites_Surfacewater,AutoID,-1,-1;Site_Name "Site_Name" true true false 25 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Site_Name,0,25;Status "Status" true true false 1 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Status,0,1;Location_Name "Location_Name" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Location_Name,0,50;Source_Description "Source_Description" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Source_Description,0,50;Source_Name "Source_Name" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Source_Name,0,50;Basin "Basin" true true false 4 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Basin,0,4;app "app" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,app,0,50;Site_Type "Site_Type" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Site_Type,0,50;Elev "Elev" true true false 4 Long 0 0,First,#,Monitoring_Sites_Surfacewater,Elev,-1,-1;Data_Source "Data_Source" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Data_Source,0,50;Remarks "Remarks" true true false 1073741822 Text 0 0,First,#,Monitoring_Sites_Surfacewater,Remarks,0,1073741822;County "County" true true false 50 Text 0 0,First,#,Monitoring_Sites_Surfacewater,County,0,50;Lat_DD_NAD83 "Lat_DD_NAD83" true true false 8 Double 0 0,First,#,Monitoring_Sites_Surfacewater,Lat_DD_NAD83,-1,-1;Lon_DD_NAD83 "Lon_DD_NAD83" true true false 8 Double 0 0,First,#,Monitoring_Sites_Surfacewater,Lon_DD_NAD83,-1,-1;GlobalID "GlobalID" false false true 38 GlobalID 0 0,First,#,Monitoring_Sites_Surfacewater,GlobalID,-1,-1',
    sort_field=None
)


# reassign variable name
NV_gage = "NV_gages_final"

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
    arcpy.AddField_management(NV_gage, field_name, field_type)

# Confirm the field addition
field_names = [field.name for field in arcpy.ListFields(NV_gage)]
print("Fields in the layer after addition:", field_names)

# Remove USGS Gages by selecting them

NV_gage = "NV_gages_final"

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=NV_gage,
    selection_type="NEW_SELECTION",
    where_clause="Data_Source = 'USGS'",
    invert_where_clause=None
)
# Delete the selected rows
arcpy.management.DeleteRows(NV_gage)

# Clear the selection
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=NV_gage,
    selection_type="CLEAR_SELECTION"
)

print("Removed USGS gages")

## Get unique ID, which comes from Site_Name

# Create an update cursor to iterate through the rows
with arcpy.da.UpdateCursor(NV_gage, ['Site_Name', 'id']) as cursor:
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
arcpy.management.CalculateField(NV_gage, "name", expression, "PYTHON3")

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
with arcpy.da.UpdateCursor(NV_gage, field_name) as cursor:
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

arcpy.CalculateField_management(NV_gage, "provider_name", "'Nevada Division of Water Resources'")
arcpy.CalculateField_management(NV_gage, "provider_url", '"https://data-ndwr.hub.arcgis.com/datasets/NDWR::surface-water-monitoring-sites/explore?location=39.027307%2C-116.979050%2C8.30"', "PYTHON3")
arcpy.CalculateField_management(NV_gage, "provider_id", '"{}"'.format('"!id!"'), "PYTHON3")
arcpy.CalculateField_management(NV_gage, "provider_code", "'ndwr'")

print("Fields calculated")

#create url
codeblock = """
def url_join(*parts: list) -> str:
    return '/'.join([str(p).strip().strip('/') for p in parts])
"""
##geoconnex.us/ndwr/gages/id

expression = """url_join("https://geoconnex.us/ndwr/gages", !id!)"""
arcpy.management.CalculateField(NV_gage, "uri", expression, "PYTHON3", codeblock)
print("uri calculated")



import pandas as pd

# Path to the CSV file
csv_file_path = r"C:\Users\ewiggans\Desktop\GeoConnexMap\NevadaGage\Surface_Water_Monitoring_Sites_and_Measures.csv"
pd.set_option('display.width', 1000)

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file_path)

# Display the first few rows of the data frame to verify the data
print(df.head())
df.columns = df.columns.str.replace(' ', '_')
print(df.columns)


#Ensure 'Site_name' is a string (object) data type in the DataFrame
df['Site_name'] = df['Site_name'].astype(str)

# Create a new 'Site_name_con' column in the DataFrame by removing spaces
df['Site_name'] = df['Site_name'].str.replace(" ", "")

# Display the DataFrame to verify the new column
print(df)

import pandas as pd

# Assuming you have already loaded data into the DataFrame 'df'

# Perform the field calculations on the pandas DataFrame
df["location_id"] = df['Site_name'].str.replace(r".*@", "", regex=True)
df["about_url"] = "https://geoconnex.us/ndwr/gages/" + df['Site_name']
df["data_set_type"] = df["Site_name"].str.replace(r"@.*", "", regex=True)
df["data_set_path"] = df["data_set_type"].str.replace(".", "/", 1)

# Update format of Nevada gages using a lambda function
df["url"] = df["Site_name"].apply(lambda x: f"https://arcgis.water.nv.gov/arcgis/rest/services/NDWR/Monitoring_Sites_Surface_Water/FeatureServer/0/query?where=Site_Name+='{x.replace(' ', '+')}'")

df["provider_code"] = "ndwr"
df["parameter_name"] = df["data_set_type"]
df["parameter_group"] = "discharge"
df["parameter_id"] = df["provider_code"] + "-" + df["parameter_group"]
df["about_uri"] = df["about_url"]
df["name"] = df["Site_name"]

print("Complete")


df.head()

# Print the first five rows of the "data_set_url" column
pd.options.display.max_colwidth = 300
print(df["url"].head())

#Perform final field calculations on pandas DataFrame

end_df = df[["about_uri", "url", "name", "provider_code", "parameter_id", "parameter_name", "parameter_group"]]
end_df.head()
end_df.to_csv("C:\\Users\\ewiggans\\Desktop\\GeoConnexMap\\NevadaGage\\NV_download_table.csv")
#Export and write to new CSV


arcpy.management.Project(
    in_dataset="NV_gages_final",
    out_dataset=r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb\NV_gages_final_Project",
    out_coor_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]',
    transform_method="WGS_1984_(ITRF00)_To_NAD_1983",
    in_coor_system='PROJCS["NAD_1983_UTM_Zone_11N",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-117.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
    preserve_shape="NO_PRESERVE_SHAPE",
    max_deviation=None,
    vertical="NO_VERTICAL"
)

NV_gage = "NV_gages_final_Project"

import json
import requests
from shapely.geometry import shape, Point

#####################Project to WGS 84


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
with arcpy.da.UpdateCursor(NV_gage, ["Shape", "comid"]) as cursor:
    for row in cursor:
        geom = row[0]
        comid = get_comid_intersect(geom)
        if comid is not None:
            print(comid, end='\r', flush=True)
            row[1] = comid
            cursor.updateRow(row)


print("comid calculated")

# Read in the CSV file as a geodatabase table
csv_table = r"C:\Users\ewiggans\Desktop\GeoConnexMap\NevadaGage\nhdpv2_lookup.csv"
csv_table_name = "NHDPV2_Lookup"
arcpy.TableToTable_conversion(csv_table, arcpy.env.workspace, csv_table_name)

# Add a new field 'comid_text' to the CSV table with a data type of TEXT
arcpy.AddField_management(csv_table_name, "comid_text", "TEXT")

# Calculate the 'comid_text' field by copying the values from the 'comid' field
expression = "!comid!"
codeblock = ""
arcpy.CalculateField_management(csv_table_name, "comid_text", expression, "PYTHON3", codeblock)

print("Added 'comid_text' field and set its values equal to 'comid' as text.")



# Join the CSV table to the CO gage feature class based on the "comid" field
arcpy.AddJoin_management(NV_gage, "comid", csv_table_name, "comid_text", "KEEP_COMMON")

# Calculate the "mainstem_uri" field to be equal to the "uri" field in the CSV table
expression = "!{}.uri!".format(csv_table_name)
arcpy.CalculateField_management(NV_gage, "mainstem_uri", expression, "PYTHON3")

# Remove the join to the CSV table
arcpy.RemoveJoin_management(NV_gage, csv_table_name)


# Define the output GeoJSON file path
output_geojson_file = r"C:\Users\ewiggans\Desktop\GeoConnexMap\NevadaoGage\NV_gage_export.geojson"

# Export the feature class to GeoJSON
arcpy.FeaturesToJSON_conversion(in_features = NV_gage, 
                                out_json_file = output_geojson_file,
                                geoJSON = "GEOJSON")


print(f"Exported {NV_gage} to {output_geojson_file} in GeoJSON format.")


