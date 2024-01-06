import argparse
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

GREEN = '\033[92m'
RED = '\033[91m'
ORANGE = '\033[93m'
RESET = '\033[0m'


def scrape_lineups(start_map=None, start_side=None):
    options = Options()
    options.add_experimental_option("detach", True)

    # Create a ChromeService instance
    chrome_service = ChromeService(ChromeDriverManager().install())

    # Pass the ChromeService instance to the webdriver.Chrome() constructor
    driver = webdriver.Chrome(service=chrome_service, options=options)

    # Navigate to the website
    driver.maximize_window()

    driver.get("https://lineupsvalorant.com/")

    time.sleep(2)

    # Wait for the page to load
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body")))

    try:
        map_selector_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "map_selector")))

        # Find all the <a> tags within the map selector div
        map_links = map_selector_div.find_elements(By.TAG_NAME, 'a')

        # Determine the starting index based on the provided start_map
        start_index = 1
        if start_map:
            start_index = next((i for i, link in enumerate(
                map_links) if link.get_attribute('data-value') == start_map), None)
            if start_index is None:
                print(f"{ORANGE}Map {
                      start_map} not found. Starting from the beginning.{RESET}")
                start_index = 1
            else:
                print(f"{ORANGE}Starting from Map: {start_map}{RESET}")

        for link in map_links[start_index:]:
            data_value = link.get_attribute('data-value')
            class_name = link.get_attribute('class')
            href = link.get_attribute('href')

            retry_count = 0
            max_retries = 2

            while retry_count < max_retries:
                try:
                    # Move the mouse to the map link
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", link)
                    driver.execute_script("arguments[0].click();", link)

                    time.sleep(2)

                    print(f"{GREEN}Clicked on map: Data Value: {
                          data_value}, Class: {class_name}, Href: {href}{RESET}")

                    # Check if lineup-box elements are present
                    try:
                        # Use a different timeout for the second attempt
                        WebDriverWait(driver, 60 if retry_count == 1 else 30).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "lineup-box")))
                    except TimeoutException:
                        # If lineup-box elements are not present, retry
                        retry_count += 1
                        print(f"{RED}Lineup box elements not found, retrying... (Attempt {
                              retry_count}){RESET}")
                        continue

                    # Find and click on the side buttons
                    side_buttons = driver.find_elements(
                        By.CSS_SELECTOR, '#side_selector_parent .search_toggles button')

                    scroll_percentage = 10
                    driver.execute_script(f"window.scrollBy(0, window.innerHeight * {scroll_percentage / 100});")
                    
                    # Determine the starting index based on the provided start_side
                    start_side_index = 0
                    if start_side:
                        start_side_lower = start_side.lower()
                        start_side_index = next((i for i, side_button in enumerate(side_buttons) if
                                                side_button.get_attribute('data-value') == start_side_lower), None)
                        if start_side_index is None:
                            print(f"{ORANGE}Side {
                                  start_side} not found. Starting from the beginning.{RESET}")
                            start_side_index = 0
                        else:
                            print(f"{ORANGE}Starting from Side: {
                                  start_side}{RESET}")

                    for side_button in side_buttons[start_side_index:]:
                        side_data_value = side_button.get_attribute(
                            'data-value')
                        side_text = side_button.text

                        print(f"Clicking on side: Data Value: {
                              side_data_value}, Side: {side_text}")

                        driver.execute_script(
                            "arguments[0].scrollIntoView();", side_button)
                        driver.execute_script(
                            "arguments[0].click();", side_button)

                        time.sleep(2)

                        SCROLL_PAUSE_TIME = 5
                        last_height = driver.execute_script(
                            "return document.body.scrollHeight")

                        while True:
                            target_scroll_position = int(driver.execute_script(
                                "return (document.body.scrollHeight * 0.95);"))
                            driver.execute_script(
                                f"window.scrollTo(0, {target_scroll_position});")
                            time.sleep(SCROLL_PAUSE_TIME)
                            new_height = driver.execute_script(
                                "return document.body.scrollHeight")
                            if new_height == last_height:
                                break
                            last_height = new_height

                        # Find all the lineup-box elements
                        lineup_boxes = driver.find_elements(
                            By.CSS_SELECTOR, "#lineups_grid .lineup-box")

                        print(f"{GREEN}Found {len(lineup_boxes)} lineup boxes for {
                              side_text} side{RESET}")

                        # Scraped data Array
                        scraped_data = []

                        # Iterate through each lineup box
                        for lineup_box in lineup_boxes:
                            # Extract title and data-id
                            title = lineup_box.find_element(
                                By.CLASS_NAME, 'lineup-box-title').text
                            data_id = lineup_box.get_attribute('data-id')

                            # Click on the lineup box to open the modal
                            driver.execute_script(
                                "arguments[0].scrollIntoView();", lineup_box)
                            driver.execute_script(
                                "arguments[0].click();", lineup_box)
                            time.sleep(5)

                            # Wait for viewer_max_image to be populated
                            max_image_element_wait = WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.ID, "viewer_max_image"), ""))
                            max_image_element = driver.find_element(By.ID,  "viewer_max_image")
                            max_image_number_text = max_image_element.text
                            
                            # Wait for viewer_description_text to be populated
                            description_text_element_wait = WebDriverWait(driver, 40).until(
                                EC.text_to_be_present_in_element((By.ID, "viewer_description_text"), ""))
                            description_text_element = driver.find_element(By.ID, "viewer_description_text")

                            # Wait for viewer_description_abilities to have at least one element
                            abilities_element = WebDriverWait(driver, 40).until(
                                EC.presence_of_element_located((By.ID, "viewer_description_abilities")))

                            # Get the required values
                            max_image_number = 3 if not max_image_number_text or not max_image_number_text.isdigit() else int(max_image_number_text)
                            description_text = description_text_element.text.replace('<br>', ' ')

                            # Get all the image elements in viewer_description_abilities
                            abilities_images = abilities_element.find_elements(By.TAG_NAME, 'img')

                            agent_names = []
                            ability_names = []

                            for img in abilities_images:
                                src = img.get_attribute('src')
                                name = src.split('/')[-1].split('.')[0]  # Extracts the name without extension

                                if 'agents' in src:
                                    agent_names.append(name)
                                elif 'abilities' in src:
                                    name = name.replace('%20', ' ')
                                    ability_names.append(name)

                            # Extract image URLs for the lineup
                            image_base_url = f"https://lineupsvalorant.com/static/lineup_images/{data_id}/"
                            image_urls = [f"{image_base_url}{i}.webp" for i in range(1, max_image_number + 1)]

                            # Save the data in the specified format
                            lineup_data = {
                                'title': title,
                                'data_id': data_id,
                                'image_urls': image_urls,
                                'description_text': description_text,
                                'agent': agent_names,
                                'ability': ability_names
                            }

                            # Append the dictionary to the list
                            scraped_data.append(lineup_data)

                            # Save to JSON file
                            map_name_lower = link.get_attribute('data-value').lower()
                            side_lower = side_text.lower()
                            filename = f"scraped_data_{map_name_lower}_{side_lower}.json"

                            with open(filename, 'w', encoding='utf-8') as json_file:
                                json.dump(scraped_data, json_file,
                                      ensure_ascii=False, indent=4)

                            print(f"Scraped data for {filename}")

                    break

                except TimeoutException:
                    retry_count += 1
                    print(f"{RED}Timeout exception, retrying...{RESET}")

    finally:
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Valorant lineups from lineupsvalorant.com")
    parser.add_argument("--map", help="Specify the starting map")
    parser.add_argument("--side", help="Specify the starting side")

    args = parser.parse_args()

    scrape_lineups(start_map=args.map, start_side=args.side)
