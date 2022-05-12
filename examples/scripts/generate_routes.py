import json
import random

import matplotlib.pyplot as plt
import requests

# Plot the routes on the Hamburg OSM map
map = plt.imread("assets/hamburg.png")
fig, ax = plt.subplots(figsize=(16.62, 11.84))

# Bounds for the Hamburg dataset
hamburg_min_latitude, hamburg_max_latitude = 53.3805229525385, 53.8621238364754
hamburg_min_longitude, hamburg_max_longitude = 9.601781731883774,10.74185060132706

ax.set_xlim(hamburg_min_longitude, hamburg_max_longitude)
ax.set_ylim(hamburg_min_latitude, hamburg_max_latitude)


# Create random point pairs within the bounds of the Hamburg dataset
def create_random_point_pair():
    random_latitude_from = random.uniform(hamburg_min_latitude, hamburg_max_latitude)
    random_longitude_from = random.uniform(hamburg_min_longitude, hamburg_max_longitude)
    random_latitude_to = random.uniform(hamburg_min_latitude, hamburg_max_latitude)
    random_longitude_to = random.uniform(hamburg_min_longitude, hamburg_max_longitude)
    return [random_longitude_from, random_latitude_from], [random_longitude_to, random_latitude_to]


graphhopper_routes = []

# Generate random routes with GraphHopper
while len(graphhopper_routes) < 1000:
    from_point, to_point = create_random_point_pair()
    # Send the points to the local GraphHopper API at port 8989
    response = requests.post("http://localhost:8989/route", json={
        "points": [from_point, to_point],
        "points_encoded": False, # Include coordinates in the response
        "elevation": True, # Include elevation in the response
        "vehicle": "bike2", # Use the bike2 profile
    })

    # Check if the response is successful
    # some points are not reachable, so we need to check for a 200 response
    if response.status_code == 200:
        print(f"Found route between {from_point} and {to_point}")
        graphhopper_routes.append(response.json())
    else:
        error_description = response.json().get("message")
        # Plot the points on the map in a red color, indicating
        # that the route is not reachable
        if "Cannot find point 0:" in error_description:
            ax.plot(from_point[0], from_point[1], "ro", color="red", markersize=1)
        elif "Cannot find point 1:" in error_description:
            ax.plot(to_point[0], to_point[1], "ro", color="red", markersize=1)
        else:
            print(f"Uncommon error during route calculation: {error_description}")


# Unwrap the coordinate based routes from the GraphHopper routes
unwrapped_routes = []
for graphhopper_route in graphhopper_routes:
    unwrapped_route = []
    for path in graphhopper_route["paths"]:
        for coodinate in path["points"]["coordinates"]:
            unwrapped_route.append({
                "lon": coodinate[0],
                "lat": coodinate[1],
                "alt": coodinate[2],
            })
    unwrapped_routes.append({
        "route": unwrapped_route
    })

# Write the routes to a JSON file
with open("../example_routes.json", "w") as routes_file:
    json_str = json.dumps(unwrapped_routes)
    routes_file.write(json_str)

for route_json in unwrapped_routes:
    route = route_json["route"]
    x = [point["lon"] for point in route]
    y = [point["lat"] for point in route]
    ax.plot(x, y)

ax.set_title("Randomly generated bike routes in Hamburg")
ax.imshow(
    map,
    extent=[hamburg_min_longitude, hamburg_max_longitude, hamburg_min_latitude, hamburg_max_latitude],
    interpolation='nearest', aspect='auto', alpha=0.5
)
plt.savefig('../example_routes.pdf', bbox_inches='tight')
