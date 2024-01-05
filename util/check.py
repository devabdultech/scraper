import json


def check_empty_description_text(*file_paths):
    empty_description_files = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for idx, item in enumerate(data, start=1):
                if "description_text" in item and (not item["description_text"] or item["description_text"] == ""):
                    empty_description_files.append({
                        "file_path": file_path,
                        "line_number": idx,
                        "data_id": item["data_id"]
                    })
    return empty_description_files


cleaned_data = check_empty_description_text("../scraped_data_bind_all.json", "../scraped_data_bind_defense.json", "../scraped_data_bind_attack.json",
                                            "../scraped_data_haven_all.json", "../scraped_data_haven_defense.json", "../scraped_data_haven_attack.json", "../scraped_data_sunset_all.json", "../scraped_data_sunset_defense.json")

# Print the results
for item in cleaned_data:
    print(f"File: {item['file_path']}, Line Number: {
          item['line_number']}, Data ID: {item['data_id']}")
