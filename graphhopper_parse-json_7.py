import requests
import urllib.parse
try:
    from geopy.distance import great_circle
except ModuleNotFoundError:
    print("\nERROR: geopy is missing.")
    print("Please run: pip3 install geopy\n")
    exit(1)

# Base URLs
geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"

# Replace with your Graphhopper API key
key = "8068d8ca-a8ab-404f-aade-bf6fe1beec3c"

def geocoding(location, key):
    while location == "":
        location = input("Enter location again: ")
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and "hits" in json_data and len(json_data["hits"]) > 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")
        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif country:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name
        print(f"Geocoding API URL for {new_loc} (Location Type: {json_data['hits'][0]['osm_value']})\n{url}")
        return json_status, lat, lng, new_loc
    else:
        return json_status, "null", "null", location

def airplane_route(orig, dest):
    if orig[1] == "null" or dest[1] == "null":
        print("Error: invalid coordinates.")
        return
    orig_coords = (orig[1], orig[2])
    dest_coords = (dest[1], dest[2])
    distance_km = great_circle(orig_coords, dest_coords).kilometers
    distance_miles = great_circle(orig_coords, dest_coords).miles
    flight_time_hours = distance_km / 900
    hr = int(flight_time_hours)
    min = int((flight_time_hours % 1) * 60)
    print("=================================================")
    print(f"Airplane Route from {orig[3]} to {dest[3]}")
    print("=================================================")
    print("Distance Traveled: {:.1f} miles / {:.1f} km".format(distance_miles, distance_km))
    print("Estimated Flight Duration: {:02d}:{:02d}".format(hr, min))
    print("=================================================")

# --- Run once ---
print("\n+++++++++++++++++++++++++++++++++++++++++++++")
print("Vehicle profiles available on Graphhopper:")
print("+++++++++++++++++++++++++++++++++++++++++++++")
print("car, bike, foot, airplane")
print("+++++++++++++++++++++++++++++++++++++++++++++")
profile = ["car", "bike", "foot", "airplane"]

vehicle = input("Enter a vehicle profile from the list above: ")
if vehicle not in profile:
    vehicle = "car"
    print("No valid vehicle profile was entered. Using the car profile.")

loc1 = input("Starting Location: ")
orig = geocoding(loc1, key)

loc2 = input("Destination: ")
dest = geocoding(loc2, key)

# Routing or airplane fallback
if vehicle == "airplane":
    airplane_route(orig, dest)
else:
    if orig[1] == "null" or dest[1] == "null":
        print("Error: One or both locations could not be geocoded.")
    else:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp

        replypaths = requests.get(paths_url)
        paths_data = replypaths.json()
        paths_status = replypaths.status_code

        print("=================================================")
        print("Routing API Status:", paths_status)
        print("Routing API URL:\n" + paths_url)
        print("=================================================")
        print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=================================================")

        if paths_status == 200 and "paths" in paths_data and paths_data["paths"]:
            miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
            km = (paths_data["paths"][0]["distance"]) / 1000
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)
            print("Distance Traveled: {0:.1f} miles / {1:.1f} km".format(miles, km))
            print("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print("=================================================")
            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                print("{0} ( {1:.1f} km / {2:.1f} miles )".format(
                    path, distance/1000, distance/1000/1.61))
            print("=================================================")
        else:
            print("No valid route found. Falling back to airplane mode...")
            airplane_route(orig, dest)
