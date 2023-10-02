# x <- jsonlite::fromJSON("https://nednr.nebraska.gov/IwipApi/api/v1/StreamGage/GetStationList")
# x <- x$Results
# x <- as.data.frame(x)
# x <- sf::st_as_sf(x,coords=c("Longitude","Latitude"))
# 
# sf::write_sf(x,"gages.geojson")

library(jsonlite)
library(sf)

# Fetch data from the API
api_url <- "https://nednr.nebraska.gov/IwipApi/api/v1/StreamGage/GetStationList"
gage_data <- jsonlite::fromJSON(api_url)

# Extract results
results <- gage_data$Results

# Convert to a data frame and then to an sf object
gage_sf <- sf::st_as_sf(results, coords = c("Longitude", "Latitude"))

# Specify the output directory
output_directory <- "C:/Users/ewiggans/Desktop/GeoConnexMap/NebraskaGage"

# Create the complete file paths
geojson_path <- file.path(output_directory, "gages.geojson")
shapefile_path <- file.path(output_directory, "gages.shp")

# Write to GeoJSON file
sf::write_sf(gage_sf, geojson_path, driver = "GeoJSON")

# Write to Shapefile
sf::st_write(gage_sf, shapefile_path)
