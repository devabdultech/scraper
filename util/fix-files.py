import json


def fix_json_files(json_filenames):
    for filename in json_filenames:
        print(f"Fixing JSON file: {filename}")

        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Iterate through each entry in the JSON file and fix agent and ability images
        for entry in data:
            if 'agent_images' in entry:
                entry['agent_images'] = [url.strip().replace(
                    'https://lineupsvalorant.com', '', 1) for url in entry['agent_images']]
            if 'ability_images' in entry:
                entry['ability_images'] = [url.strip().replace(
                    'https://lineupsvalorant.com', '', 1) for url in entry['ability_images']]

        # Save the fixed data back to the JSON file
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print(f"Finished fixing: {filename}")


# Example usage:
# Provide a list of JSON filenames to fix
json_filenames_to_fix = ["../scraped_data_bind_attack.json"]
fix_json_files(json_filenames_to_fix)
