import json

GREEN = '\033[92m'
RESET = '\033[0m'


def count_objects_in_json_file(json_file_path):
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as file:
        # Parse the JSON data
        json_data = json.load(file)

        # Determine the number of objects in the JSON data
        if isinstance(json_data, list):
            return len(json_data)
        elif isinstance(json_data, dict):
            return 1
        else:
            return 0  # JSON data is neither a list nor a dictionary


json_file_path = '../scraped_data_sunset_defense.json'
number_of_objects = count_objects_in_json_file(json_file_path)
print(f'{GREEN}Number of objects in the JSON file: {number_of_objects}{RESET}')
