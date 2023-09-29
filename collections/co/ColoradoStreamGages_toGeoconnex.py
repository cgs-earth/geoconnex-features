import arcpy

# Set the workspace environment
arcpy.env.workspace = r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb"

#read in table and create feature class.

# Define the paths to the Excel file and the geodatabase
excel_file = r"C:\Users\ewiggans\Desktop\GeoConnexMap\ColoradoGage\CDSS_SearchResults_SurfaceWaterStations_202309261305.xlsx"
geodatabase = r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb"

# Define the name for the feature class
feature_class_name = "CO_gages"

# Define the Excel sheet name (modify as needed)
excel_sheet_name = "CDSS_SearchResults_SurfaceWater"

# Create a path to the output feature class
output_feature_class = arcpy.ValidateTableName(feature_class_name, geodatabase)


# Import the Excel table into ArcGIS Pro as a table
arcpy.ExcelToTable_conversion(excel_file, output_feature_class) #field_names_range)

# # Convert the table to a feature class
arcpy.management.XYTableToPoint(
    in_table="CO_gages",
    out_feature_class=r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb\CO_gages_XYTableToPoint",
    x_field="Longitude",
    y_field="Latitude",
    z_field=None,
    coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
)

print(f"Imported '{excel_sheet_name}' from '{excel_file}' to '{geodatabase}\\{output_feature_class}'")

arcpy.conversion.ExportFeatures(
    in_features="CO_gages_XYTableToPoint",
    out_features=r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb\CO_gages_final",
    where_clause="",
    use_field_alias_as_name="NOT_USE_ALIAS",
    field_mapping='Abbrev "Abbrev" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,Abbrev,0,255;Station_Name "Station Name" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,Station_Name,0,255;Station_Status "Station Status" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,Station_Status,0,255;Data_Source "Data Source" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,Data_Source,0,255;USGS_ID "USGS ID" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,USGS_ID,0,255;WDID "WDID" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,WDID,0,255;Water_Source "Water Source" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,Water_Source,0,255;GNIS_ID "GNIS ID" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,GNIS_ID,0,255;Stream_Mile "Stream Mile" true true false 8 Double 0 0,First,#,CO_gages_XYTableToPoint,Stream_Mile,-1,-1;POR_Start "POR Start" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,POR_Start,0,255;POR_End "POR End" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,POR_End,0,255;Div "Div" true true false 4 Long 0 0,First,#,CO_gages_XYTableToPoint,Div,-1,-1;WD "WD" true true false 4 Long 0 0,First,#,CO_gages_XYTableToPoint,WD,-1,-1;County "County" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,County,0,255;State "State" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,State,0,255;HUC10 "HUC10" true true false 4 Long 0 0,First,#,CO_gages_XYTableToPoint,HUC10,-1,-1;UTM_X "UTM X" true true false 8 Double 0 0,First,#,CO_gages_XYTableToPoint,UTM_X,-1,-1;UTM_Y "UTM Y" true true false 8 Double 0 0,First,#,CO_gages_XYTableToPoint,UTM_Y,-1,-1;Latitude "Latitude" true true false 8 Double 0 0,First,#,CO_gages_XYTableToPoint,Latitude,-1,-1;Longitude "Longitude" true true false 8 Double 0 0,First,#,CO_gages_XYTableToPoint,Longitude,-1,-1;Location_Accuracy "Location Accuracy" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,Location_Accuracy,0,255;Modified "Modified" true true false 8 Date 0 0,First,#,CO_gages_XYTableToPoint,Modified,-1,-1;More_Information "More Information" true true false 255 Text 0 0,First,#,CO_gages_XYTableToPoint,More_Information,0,255',
    sort_field=None
)
# reassign variable name
CO_gage = "CO_gages_final"

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
    arcpy.AddField_management(CO_gage, field_name, field_type)

# Confirm the field addition
field_names = [field.name for field in arcpy.ListFields(CO_gage)]
print("Fields in the layer after addition:", field_names)

# Remove USGS Gages by selecting them

CO_gage = "CO_gages_final"

arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=CO_gage,
    selection_type="NEW_SELECTION",
    where_clause="Data_Source = 'U.S. Geological Survey'",
    invert_where_clause=None
)
# Delete the selected rows
arcpy.management.DeleteRows(CO_gage)

# Clear the selection
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=CO_gage,
    selection_type="CLEAR_SELECTION"
)

print("Removed USGS gages")

## Get unique ID, which comes from last text after / in url 

# Create an update cursor to iterate through the rows

with arcpy.da.UpdateCursor(CO_gage, ["More_Information", "id"]) as cursor:
    for row in cursor:
        more_info_url = row[0]
        parts = more_info_url.split('/')
        last_part = parts[-1]
        row[1] = last_part  # Set the 'id' field to the extracted value
        cursor.updateRow(row)
        print(row)

# Clean up the cursor
del cursor

# Set name = id
# Define the expression for the field calculation
expression = "!id!"  # Set the 'name' field equal to the 'id' field

# Perform the field calculation
arcpy.management.CalculateField(CO_gage, "name", expression, "PYTHON3")

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
with arcpy.da.UpdateCursor(CO_gage, field_name) as cursor:
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


# Select values from non unique idenfiers above 
values_to_select = ["6200561A", "CLFOFDCO", "MICDCPCO"]

# Create a SQL query for the 'name' field using the IN operator
# This will select features where the 'name' field matches any of the specified values
query = f"name IN {tuple(values_to_select)}"

# Select features based on the SQL query
arcpy.management.SelectLayerByAttribute(CO_gage, "NEW_SELECTION", query)
#noting there are 6 values, 2 duplicates of each above

print("Investigate the values to see which should be removed")




# Clear Selection
arcpy.management.SelectLayerByAttribute(CO_gage, "CLEAR_SELECTION")


# re select values to select for the first criteria
values_to_select_1 = ["6200561A", "CLFOFDCO", "MICDCPCO"]

# Create a SQL query for the 'name' field using the IN operator
query_1 = f"name IN {tuple(values_to_select_1)}"

# specify values to select for the second criteria
values_to_select_2 = ["JOE WRIGHT CREEK", "COW CREEK", "BASIN CREEK"]

# Create a SQL query for the 'Water_Source' field using the IN operator
query_2 = f"Water_Source IN {tuple(values_to_select_2)}"

# Combine the two queries using the AND operator
combined_query = f"({query_1}) AND ({query_2})"

# Select features based on the combined query
arcpy.management.SelectLayerByAttribute(CO_gage, "NEW_SELECTION", combined_query)


print("Selection should result in 3 rows")
print("STOP and confirm you want to move on and delete")


# Delete the selected features
arcpy.management.DeleteFeatures(CO_gage)

# Clear the selection
arcpy.management.SelectLayerByAttribute(CO_gage, "CLEAR_SELECTION")
print("Now duplicates are removed")

# Delete records with no lat/long
# SQL query to select features where Latitude and Longitude are both null
query = "Latitude IS NULL AND Longitude IS NULL"

# Select features based on the SQL query
arcpy.management.SelectLayerByAttribute(CO_gage, "NEW_SELECTION", query)

print("Selected rows with no lat and long values")


# Delete the selected rows
arcpy.management.DeleteRows(CO_gage)

# Clear the selection
arcpy.management.SelectLayerByAttribute(CO_gage, "CLEAR_SELECTION")
print("Rows with no lat/long deleted")

#Update Fields

arcpy.CalculateField_management(CO_gage, "provider_name", "'Colorado Decision Support System'")
arcpy.CalculateField_management(CO_gage, "provider_url", '"{}"'.format('"!More_Information!"'), "PYTHON3")
arcpy.CalculateField_management(CO_gage, "provider_id", '"{}"'.format('"!id!"'), "PYTHON3")
arcpy.CalculateField_management(CO_gage, "provider_code", "'cdss'")

print("Fields calculated")

#tcreate url
codeblock = """
def url_join(*parts: list) -> str:
    return '/'.join([str(p).strip().strip('/') for p in parts])
"""
##geoconnex.us/cdss/gages/id

expression = """url_join("https://geoconnex.us/cdss/gages", !id!)"""
arcpy.management.CalculateField(CO_gage, "uri", expression, "PYTHON3", codeblock)
print("uri calculated")



import pandas as pd

#create fake table manually from this exported excel
arcpy.conversion.TableToExcel(CO_gage, r"C:\Users\ewiggans\Desktop\GeoConnexMap\ColoradoGage\CO_gage.xlsx")

#Created fake table 
# Path to the CSV file
csv_file_path = r"C:\Users\ewiggans\Desktop\GeoConnexMap\ColoradoGage\Temp_List.csv"
pd.set_option('display.width', 1000)


# Read the CSV file into a pandas DataFrame


df = pd.read_csv(csv_file_path, skiprows=[0])


# Display the first few rows of the data frame to verify the data
print(df.head())
df.columns = df.columns.str.replace(' ', '_')
print(df.columns)



# Perform the field calculations on the pandas DataFrame
df["location_id"] = df['Data_Set_Id'].str.replace(r".*@", "", regex=True)
df["about_url"] = "https://geoconnex.us/cdss/gages/" + df["ID"]
df["data_set_type"] = df["Data_Set_Id"].str.replace(r"@.*", "", regex=True)
df["data_set_path"] = df["data_set_type"].str.replace(".", "/", 1)

#update to format of Nebraska gages
df["url"] = "https://dwr.state.co.us/Tools/Stations/" + df["ID"]
df["provider_code"] = "cdss"
df["parameter_name"] = df["data_set_type"]
df["parameter_group"] = "discharge"
df["parameter_id"] = df["provider_code"] + "-" + df["parameter_group"]
df["about_uri"] = df["about_url"]
df["name"] = df["Data_Set_Id"]

print("Complete")

df.head()

# Print the first five rows of the "data_set_url" column
pd.options.display.max_colwidth = 300
print(df["url"].head())

#Perform final field calculations on pandas DataFrame

end_df = df[["about_uri", "url", "name", "provider_code", "parameter_id", "parameter_name", "parameter_group"]]
end_df.head()
end_df.to_csv("C:\\Users\\ewiggans\\Desktop\\GeoConnexMap\\ColoradoGage\\CO_download_table.csv")
#Export and write to new CSV


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
with arcpy.da.UpdateCursor(CO_gage, ["Shape", "comid"]) as cursor:
    for row in cursor:
        geom = row[0]
        comid = get_comid_intersect(geom)
        if comid is not None:
            print(comid, end='\r', flush=True)
            row[1] = comid
            cursor.updateRow(row)


print("comid calculated")

# Read in the CSV file as a geodatabase table
csv_table = r"C:\Users\ewiggans\Desktop\GeoConnexMap\ColoradoGage\nhdpv2_lookup.csv"
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
arcpy.AddJoin_management(CO_gage, "comid", csv_table_name, "comid_text", "KEEP_COMMON")

# Calculate the "mainstem_uri" field to be equal to the "uri" field in the CSV table
expression = "!{}.uri!".format(csv_table_name)
arcpy.CalculateField_management(CO_gage, "mainstem_uri", expression, "PYTHON3")

# Remove the join to the CSV table
arcpy.RemoveJoin_management(CO_gage, csv_table_name)


# Define the output GeoJSON file path
output_geojson_file = r"C:\Users\ewiggans\Desktop\GeoConnexMap\ColoradoGage\CO_gage_export.geojson"

# #set projection to wgs84
# arcpy.management.DefineProjection(
#     in_dataset="CO_gages_final",
#     coor_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
# )


# Export the feature class to GeoJSON
arcpy.FeaturesToJSON_conversion(in_features = CO_gage, 
                                out_json_file = output_geojson_file,
                                geoJSON = "GEOJSON")


print(f"Exported {CO_gage} to {output_geojson_file} in GeoJSON format.")


