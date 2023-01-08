import csv
import random
import re


def extract_number(string):
    # Use a regex pattern to match a number with a comma
    pattern = r'\d+,\d+'
    match = re.search(pattern, string)
    if match:
        # Return the matched number as an integer
        return int(match.group().replace(',', ''))
    else:
        return None


random.seed(7893)

locations = []

# read csv file as list of dictionaries
with open("Location.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        locations.append(row)

for i in range(len(locations)):
    capacity = extract_number(locations[i]["description"])
    if (capacity):
        locations[i]["capacity"] = capacity
    else:
        locations[i]["capacity"] = random.randint(5, 100) * 10
        
filename = "Locations_with_capacity.csv"
print("Writing results to file:", filename)

fields = ["id", "name", "description", "latitude", "longitude", "capacity"]

with open(filename, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    for data in locations:
        writer.writerow(data)

print("Successfully generated csv file!")
