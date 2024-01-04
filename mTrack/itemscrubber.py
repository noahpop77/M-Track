import json

data = {}

with open('items.json', 'r') as file:
    data = json.load(file)

print(type(data))
#print(json_data)
# Now, json_data is a dictionary containing the content of your JSON file.
for key, value in data.items():
    print(f"{key}:{value}")

