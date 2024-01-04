import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)

GREEN = '\033[92m'
RESET = '\033[0m'

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

# Loop through each map option, extract data-value, and click on it
for map_option in map_options[1:]:  # Start from the second map
    data_value = map_option.get_attribute("data-value")

    print(f"{GREEN}Clicking on map with data-value: {data_value}{RESET}")

    # Scroll the element into view
    driver.execute_script("arguments[0].scrollIntoView();", map_option)

    try:
        # Wait for the element to be clickable
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"a[data-value='{data_value}']")
            )
        )

        # Click on the map option
        element.click()

    except ElementClickInterceptedException:
        print("Element click intercepted. Trying to click using JavaScript.")
        # If the normal click fails, try clicking using JavaScript
        driver.execute_script("arguments[0].click();", map_option)

    # Check if the lineups_grid is present
    try:
        # Wait for the lineups_grid to be present
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#lineups_grid .lineup-box")))

    except TimeoutException:
        print(f"No lineups found for map: {data_value}")
        continue

    # Get the total number of results from the h2 tag if it exists
    try:
        h2_tag = wait.until(EC.presence_of_element_located(
            (By.ID, "lineups_grid_title")))
        total_results_text = h2_tag.text
        # Extracting the number from "Top Results (315 results)"
        total_results_str = total_results_text.split(" ")[-2]
        total_results = int(
            total_results_str) if total_results_str.isdigit() else 0

        SCROLL_PAUSE_TIME = 5

        # Get scroll height
        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        while True:

            # Calculate the target scroll position (e.g., 90% from the top)
            target_scroll_position = int(driver.execute_script(
                "return (document.body.scrollHeight * 0.9);"))

            # Scroll to the calculated position
            driver.execute_script(
                f"window.scrollTo(0, {target_scroll_position});")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    except NoSuchElementException:
        print("No 'Top Results' found for map:", data_value)

    time.sleep(5)

    # Find all elements with the class 'lineup-box' within the lineups_grid
    lineup_boxes = driver.find_elements(
        By.CSS_SELECTOR, "#lineups_grid .lineup-box")

    # Loop through each lineup box
    for lineup_box in lineup_boxes:
        try:
            # Extract lineup box title
            lineup_box_title = lineup_box.find_element(
                By.CLASS_NAME, "lineup-box-title").text
            print(f"Lineup box title: {lineup_box_title}")

        except StaleElementReferenceException:
            # Handle StaleElementReferenceException by finding the element again
            lineup_boxes = driver.find_elements(
                By.CSS_SELECTOR, "#lineups_grid .lineup-box")
            break
