import json


def process_json_files(*file_paths):
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for item in data:
                if "description_text" in item:
                    item["description_text"] = item["description_text"].replace(
                        "\n", " ")
                if "agent_images" in item:
                    item["agent"] = item["agent_images"][0].split(
                        "/")[-1].split(".")[0].replace("%20", " ")
                    del item["agent_images"]
                if "ability_images" in item:
                    item["ability"] = [image.split(
                        "/")[-1].split(".")[0].replace("%20", " ") for image in item["ability_images"]]
                    del item["ability_images"]
            # Write the updated data back to the file
            with open(file_path, 'w') as outfile:
                json.dump(data, outfile, indent=2)


# Example usage:


cleaned_data = process_json_files("../scraped_data_bind_all.json", "../scraped_data_bind_defense.json", "../scraped_data_bind_attack.json", "../scraped_data_haven_all.json", "../scraped_data_haven_defense.json")
