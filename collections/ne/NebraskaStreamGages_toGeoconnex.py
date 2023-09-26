import arcpy

# Set the workspace environment
arcpy.env.workspace = r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb"

# Define the input layer
NE_gage = "NE_gages"

# Export to modify
arcpy.conversion.ExportFeatures(
    in_features="NE_gages",
    out_features=r"C:\Users\ewiggans\Desktop\GeoconnexNPDES\GeoconnexNPDES\GeoconnexNPDES.gdb\NE_gages_final",
    where_clause="",
    use_field_alias_as_name="NOT_USE_ALIAS",
    field_mapping='StatnNm "StatnNm" true true false 80 Text 0 0,First,#,NE_gages,StatnNm,0,80;SourcNm "SourcNm" true true false 80 Text 0 0,First,#,NE_gages,SourcNm,0,80;SttnNmb "SttnNmb" true true false 80 Text 0 0,First,#,NE_gages,SttnNmb,0,80;RivrBsn "RivrBsn" true true false 80 Text 0 0,First,#,NE_gages,RivrBsn,0,80;FldOffc "FldOffc" true true false 80 Text 0 0,First,#,NE_gages,FldOffc,0,80;SttnTyD "SttnTyD" true true false 80 Text 0 0,First,#,NE_gages,SttnTyD,0,80;Dwnstrm "Dwnstrm" true true false 4 Long 0 0,First,#,NE_gages,Dwnstrm,-1,-1;TimeZon "TimeZon" true true false 80 Text 0 0,First,#,NE_gages,TimeZon,0,80;Elevatn "Elevatn" true true false 8 Double 0 0,First,#,NE_gages,Elevatn,-1,-1;ElvtnUn "ElvtnUn" true true false 80 Text 0 0,First,#,NE_gages,ElvtnUn,0,80;IsActiv "IsActiv" true true false 4 Long 0 0,First,#,NE_gages,IsActiv,-1,-1;uri "uri" true true false 254 Text 0 0,First,#,NE_gages,uri,0,254;name "name" true true false 254 Text 0 0,First,#,NE_gages,name,0,254;id "id" true true false 254 Text 0 0,First,#,NE_gages,id,0,254',
    sort_field=None
)

# reassign variable name
NE_gage = "NE_gages_final"

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
    arcpy.AddField_management(NE_gage, field_name, field_type)

# Confirm the field addition
field_names = [field.name for field in arcpy.ListFields(NE_gage)]
print("Fields in the layer after addition:", field_names)





# Confirm unique ID in identifier field
# Field to check for uniqueness
field_name = "SttnNmb"

# Use a set to keep track of unique values encountered in the field
unique_values = set()

# Initialize a counter to keep track of the total number of rows
total_rows = 0

# Initialize a flag to check for spaces
has_spaces = False

# Start a search cursor to iterate through the rows and check for unique values and spaces
with arcpy.da.UpdateCursor(NE_gage, field_name) as cursor:
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
field_name = "SttnNmb"

# Calculate the 'id' field and 'name' field using the 'Identifier' field
expression = "!" + field_name + "!"
codeblock = ""

# Use the CalculateField tool to perform the field calculation
arcpy.CalculateField_management(NE_gage, id_field, expression, "PYTHON3", codeblock)
arcpy.CalculateField_management(NE_gage, name_field, expression, "PYTHON3", codeblock)

#print("Updated 'id' and 'name' fields with values from the 'Identifier' field.")

arcpy.CalculateField_management(NE_gage, "provider_name", "'Nebraska Department of Natural Resources'")
arcpy.CalculateField_management(NE_gage, "provider_url", "'https://nednr.aquaticinformatics.net/Data'")
arcpy.CalculateField_management(NE_gage, "provider_id", "!" + field_name +"!")
arcpy.CalculateField_management(NE_gage, "provider_code", "'nednr'")


#thank you Ben, four for you Ben
codeblock = """
def url_join(*parts: list) -> str:
    return '/'.join([str(p).strip().strip('/') for p in parts])
"""
##geoconnex.us/iow/wyseo/gages/id

expression = """url_join("https://geoconnex.us/nednr/gages", !id!)"""
arcpy.management.CalculateField(NE_gage, "uri", expression, "PYTHON3", codeblock)
print("uri calculated")



##Read in the download table

import pandas as pd
pd.set_option('display.width', 1000)

# Path to the CSV file
csv_file_path = r"C:\Users\ewiggans\Desktop\GeoConnexMap\NebraskaGage\List-20230925203221.csv"


# Read the CSV file into a pandas DataFrame


df = pd.read_csv(csv_file_path, skiprows=[0])


# Display the first few rows of the data frame to verify the data
print(df.head())
df.columns = df.columns.str.replace(' ', '_')
print(df.columns)



# Perform the field calculations on the pandas DataFrame
df["location_id"] = df['Data_Set_Id'].str.replace(r".*@", "", regex=True)
df["about_url"] = "https://geoconnex.us/wyseo/gages/" + df["location_id"]
df["data_set_type"] = df["Data_Set_Id"].str.replace(r"@.*", "", regex=True)
df["data_set_path"] = df["data_set_type"].str.replace(".", "/", 1)

#update to format of Nebraska gages
df["url"] = "https://nednr.aquaticinformatics.net/Data/Location/Summary/Location/" + df["location_id"] + "/Interval/Latest"
df["provider_code"] = "nednr"
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
end_df.to_csv("C:\\Users\\ewiggans\\Desktop\\GeoConnexMap\\NebraskaGage\\NE_download_table.csv")
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
with arcpy.da.UpdateCursor(NE_gage, ["Shape", "comid"]) as cursor:
    for row in cursor:
        geom = row[0]
        comid = get_comid_intersect(geom)
        if comid is not None:
            print(comid, end='\r', flush=True)
            row[1] = comid
            cursor.updateRow(row)


print("comid calculated")

# Read in the CSV file as a geodatabase table
csv_table = r"C:\Users\ewiggans\Desktop\GeoConnexMap\NebraskaGage\nhdpv2_lookup.csv"
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
arcpy.AddJoin_management(NE_gage, "comid", csv_table_name, "comid_text", "KEEP_COMMON")

# Calculate the "mainstem_uri" field to be equal to the "uri" field in the CSV table
expression = "!{}.uri!".format(csv_table_name)
arcpy.CalculateField_management(NE_gage, "mainstem_uri", expression, "PYTHON3")

# Remove the join to the CSV table
arcpy.RemoveJoin_management(NE_gage, csv_table_name)


# Define the output GeoJSON file path
output_geojson_file = r"C:\Users\ewiggans\Desktop\GeoConnexMap\NebraskaGage\NE_gage_export.geojson"

#set projection to wgs84
arcpy.management.DefineProjection(
    in_dataset="NE_gages_final",
    coor_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
)


# Export the feature class to GeoJSON
arcpy.FeaturesToJSON_conversion(in_features = NE_gage, 
                                out_json_file = output_geojson_file,
                                geoJSON = "GEOJSON")


print(f"Exported {NE_gage} to {output_geojson_file} in GeoJSON format.")


