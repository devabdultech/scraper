import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

GREEN = '\033[92m'
RESET = '\033[0m'


def scrape_lineups(start_map=None, start_side=None):
    options = Options()
    options.add_experimental_option("detach", True)

    # Create a ChromeService instance
    chrome_service = ChromeService(ChromeDriverManager().install())

    # Pass the ChromeService instance to the webdriver.Chrome() constructor
    driver = webdriver.Chrome(service=chrome_service, options=options)

    # Navigate to the website
    driver.get("https://lineupsvalorant.com/")
    driver.maximize_window()

    # Find all the map options
    map_options = driver.find_elements(By.CLASS_NAME, "map_selector_option")

    skip_first_map = True
    # Loop through each map option, extract data-value, and click on it
    for map_option in map_options:
        data_value = map_option.get_attribute("data-value")

        if skip_first_map:
            skip_first_map = False
            continue

        # Extract the map name from the map option
        map_name = map_option.text.strip()

        # Skip if this map has already been scraped
        if start_map and map_name != start_map:
            print(f"Skipping map: {map_name}")
            continue

        print(f"{GREEN}Clicking on map: {
              map_name} with data-value: {data_value}{RESET}")

        try:
            # Close the viewer modal if it's open
            try:
                driver.execute_script(
                    "document.getElementById('viewer_close').click();")
            except NoSuchElementException:
                pass

            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView();", map_option)

            # Wait for the element to be clickable
            wait = WebDriverWait(driver, 10)
            element = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"a[data-value='{data_value}']")
                )
            )

            # Scroll to the element's location
            driver.execute_script("arguments[0].scrollIntoView();", element)

            # Click on the map option
            element.click()

            time.sleep(5)  # Wait for 5 seconds after clicking on the map

            # Define the sides and corresponding data-values
            side_values = {"All": "0", "Defense": "1", "Attack": "2"}

            # Loop through each side
            for side, data_value in side_values.items():
                # Skip if this side has already been scraped for the specified map
                if start_side and side != start_side:
                    print(f"Skipping side: {side}")
                    continue

                # Click on the side button using data-value
                side_button_xpath = f"//button[@data-value='{data_value}']"
                try:
                    side_button = driver.find_element(
                        By.XPATH, side_button_xpath)

                    # Scroll to the side button's location
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", side_button)

                    # Click on the side button
                    side_button.click()

                    # Wait for a short time after clicking on the side
                    time.sleep(2)

                except NoSuchElementException:
                    print(f"Side button not found for: {side}")

                # Scroll down to load more lineup boxes
                SCROLL_PAUSE_TIME = 6
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

                time.sleep(5)  # Wait for 5 seconds after scrolling

                # Find all elements with the class 'lineup-box' within the lineups_grid
                lineup_boxes = driver.find_elements(
                    By.CSS_SELECTOR, "#lineups_grid .lineup-box")

                print(f"{GREEN}Found {len(lineup_boxes)
                      } lineup boxes for {side} side{RESET}")

                scraped_data = []

                # Loop through each lineup box
                for lineup_box in lineup_boxes:
                    try:
                        # Extract lineup box title and data-id
                        lineup_box_title = lineup_box.find_element(
                            By.CLASS_NAME, "lineup-box-title").text
                        data_id = lineup_box.get_attribute("data-id")

                        # Click on the lineup box using JavaScript
                        driver.execute_script(
                            "arguments[0].click();", lineup_box)

                        time.sleep(5)

                        # Wait for the modal to be present
                        modal_wait = WebDriverWait(driver, 10)
                        modal = modal_wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "#viewer_background #viewer_container #viewer_full"))
                        )

                        # Extract max image number from #viewer_max_image span
                        max_image_element = wait.until(
                            EC.presence_of_element_located(
                                (By.ID, "viewer_max_image"))
                        )
                        max_image_element = driver.find_element(
                            By.CSS_SELECTOR, "#viewer_max_image")
                        max_image_number = int(
                            max_image_element.text) if max_image_element.text else 3

                        # Extract description text from viewer_description_text
                        viewer_description_text = driver.find_element(
                            By.ID, "viewer_description_text")

                        description_text = viewer_description_text.text.replace(
                            '<br>', '\n')

                        # Extract image URLs for the lineup
                        image_base_url = f"https://lineupsvalorant.com/static/lineup_images/{
                            data_id}/"
                        image_urls = [f"{image_base_url}{
                            i}.webp" for i in range(1, max_image_number + 1)]

                        # Extract agent and ability images from viewer_description_abilities
                        agent_images = []
                        ability_images = []
                        viewer_description_abilities = driver.find_element(
                            By.ID, "viewer_description_abilities")

                        if viewer_description_abilities:
                            images = viewer_description_abilities.find_elements(
                                By.TAG_NAME, 'img')
                            for img in images:
                                img_url = img.get_attribute("src")
                                if 'agents' in img_url:
                                    agent_images.append(img_url)
                                elif 'abilities' in img_url:
                                    ability_images.append(img_url)

                        # Store the scraped data in a dictionary
                        lineup_data = {
                            'title': lineup_box_title,
                            'data_id': data_id,
                            'image_urls': image_urls,
                            'description_text': description_text,
                            'agent_images': agent_images,
                            'ability_images': ability_images
                        }

                        # Append the dictionary to the list
                        scraped_data.append(lineup_data)

                        # Print and save the scraped data to a JSON file (in real-time)
                        output_filename = f"scraped_data_{map_name.lower()}_{side.lower()}.json"
                        with open(output_filename, 'w', encoding='utf-8') as json_file:
                            json.dump(scraped_data, json_file,
                                      ensure_ascii=False, indent=4)
                        print(
                            f"Scraped data for {side} side saved in {output_filename}")

                        # Close the modal using JavaScript
                        driver.execute_script(
                            "document.getElementById('viewer_close').click();")

                    except StaleElementReferenceException:
                        # Handle StaleElementReferenceException by finding the lineup_boxes again
                        lineup_boxes = driver.find_elements(
                            By.CSS_SELECTOR, "#lineups_grid .lineup-box")
                        break

        except StaleElementReferenceException:
            # Handle StaleElementReferenceException by finding the lineup_boxes again
            lineup_boxes = driver.find_elements(
                By.CSS_SELECTOR, "#lineups_grid .lineup-box")
            break

    # Close the browser
    driver.quit()


# Example usage:
# If you want to start scraping from a specific map and side:
scrape_lineups(start_map="Haven")
