#!/usr/bin/env python3
"""
Myanmar Food Image Scraper
Scrapes images for 20 popular Myanmar food types from Google Images
Each food type is saved in its own folder
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MyanmarFoodScraper:
    def __init__(self, headless=False, images_per_food=50):
        """
        Initialize the Myanmar Food Scraper
        
        Args:
            headless (bool): Run browser in headless mode
            images_per_food (int): Number of images to download per food type
        """
        self.headless = headless
        self.images_per_food = images_per_food
        self.base_folder = "Myanmar_Food_Images"
        
        # List of 20 popular Myanmar food types
        self.myanmar_foods = [
            "mohinga",           # Traditional fish noodle soup
            "laphet thoke",      # Tea leaf salad
            "shan noodles",      # Shan style noodles
            "mont hin gar",      # Fish soup with rice noodles
            "khow suey",         # Coconut noodle soup
            "nga htamin",        # Fish rice
            "mandalay mee shay", # Mandalay style noodles
            "ohn no khao swe",   # Coconut chicken noodles
            "kyet thar hin",     # Chicken curry
            "wet tha hin",       # Pork curry
            "nga baung doke",    # Fish wrapped in banana leaf
            "mont lone yay paw", # Round glutinous rice balls
            "shwe yin aye",      # Sweet dessert drink
            "faluda",            # Sweet drink with vermicelli
            "htamin thoke",      # Rice salad
            "thoke sone",        # Mixed salad
            "dan bauk",          # Biryani Myanmar style
            "meeshay",           # Rice noodles with sauce
            "nan gyi thoke",     # Thick rice noodle salad
            "mont ti"            # Sweet snack
        ]
        
        self.driver = None
    
    def setup_driver(self):
        """Set up Chrome WebDriver with options"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        # Additional options for better performance
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def create_folder(self, folder_name):
        """Create folder for storing images"""
        folder_path = os.path.join(self.base_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    
    def get_image_urls(self, query):
        """
        Scrape image URLs from Google Images
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of image URLs
        """
        # Construct Google Images search URL
        search_query = f"{query} Myanmar food"  # Add context for better results
        url = f"https://www.google.com/search?tbm=isch&q={search_query}"
        
        try:
            # Open Google Images
            self.driver.get(url)
            logger.info(f"Searching for: {search_query}")
            time.sleep(3)
            
            # Scroll to load more images
            scroll_count = 15  # Increased scroll count for more images
            for i in range(scroll_count):
                self.driver.execute_script("window.scrollBy(0,1000)")
                time.sleep(2)
                
                # Try to click "Show more results" button if it appears
                try:
                    show_more_button = self.driver.find_element(
                        By.XPATH, "//input[@value='Show more results']"
                    )
                    if show_more_button.is_displayed():
                        show_more_button.click()
                        time.sleep(3)
                except:
                    pass
            
            # Wait for images to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
            )
            
            # Collect image URLs
            image_elements = self.driver.find_elements(By.TAG_NAME, "img")
            
            # Filter and collect valid image URLs
            image_urls = []
            for img in image_elements:
                src = img.get_attribute("src")
                data_src = img.get_attribute("data-src")
                
                # Check both src and data-src attributes
                url_to_use = src or data_src
                
                if url_to_use and url_to_use.startswith("http"):
                    # Skip base64 encoded images and very small images
                    if not url_to_use.startswith("data:"):
                        image_urls.append(url_to_use)
            
            # Remove duplicates while preserving order
            image_urls = list(dict.fromkeys(image_urls))
            logger.info(f"Found {len(image_urls)} unique image URLs for {query}")
            
            return image_urls
            
        except Exception as e:
            logger.error(f"Error getting image URLs for {query}: {e}")
            return []
    
    def download_image(self, img_url, file_path):
        """
        Download single image
        
        Args:
            img_url (str): Image URL
            file_path (str): Path to save the image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(img_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check if the response contains image data
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                return False
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to download image from {img_url}: {e}")
            return False
    
    def scrape_food_images(self, food_name):
        """
        Scrape images for a specific food type
        
        Args:
            food_name (str): Name of the Myanmar food
        """
        logger.info(f"Starting to scrape images for: {food_name}")
        
        # Create folder for this food type
        folder_path = self.create_folder(food_name)
        
        # Get image URLs
        image_urls = self.get_image_urls(food_name)
        
        if not image_urls:
            logger.warning(f"No images found for {food_name}")
            return
        
        # Download images
        downloaded_count = 0
        for i, img_url in enumerate(image_urls[:self.images_per_food]):
            try:
                # Get file extension from URL
                parsed_url = urlparse(img_url)
                file_extension = os.path.splitext(parsed_url.path)[1]
                
                # Default to .jpg if no extension found
                if not file_extension or file_extension not in ['.jpg', '.jpeg', '.png', '.webp']:
                    file_extension = '.jpg'
                
                file_name = f"{food_name}_{i+1}{file_extension}"
                file_path = os.path.join(folder_path, file_name)
                
                if self.download_image(img_url, file_path):
                    downloaded_count += 1
                    if downloaded_count % 10 == 0:
                        logger.info(f"Downloaded {downloaded_count} images for {food_name}")
                
            except Exception as e:
                logger.warning(f"Error processing image {i+1} for {food_name}: {e}")
                continue
        
        logger.info(f"Completed {food_name}: Downloaded {downloaded_count} images")
    
    def scrape_all_foods(self):
        """Scrape images for all Myanmar food types"""
        logger.info("Starting Myanmar Food Image Scraping")
        logger.info(f"Will scrape {len(self.myanmar_foods)} food types")
        logger.info(f"Target: {self.images_per_food} images per food type")
        
        # Create base folder
        os.makedirs(self.base_folder, exist_ok=True)
        
        # Setup driver
        self.setup_driver()
        
        try:
            for i, food in enumerate(self.myanmar_foods, 1):
                logger.info(f"Processing {i}/{len(self.myanmar_foods)}: {food}")
                self.scrape_food_images(food)
                
                # Add delay between different food types to avoid being blocked
                if i < len(self.myanmar_foods):
                    time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
        
        logger.info("Myanmar Food Image Scraping completed!")
    
    def scrape_single_food(self, food_name):
        """
        Scrape images for a single food type
        
        Args:
            food_name (str): Name of the food to scrape
        """
        logger.info(f"Starting single food scraping for: {food_name}")
        
        # Create base folder
        os.makedirs(self.base_folder, exist_ok=True)
        
        # Setup driver
        self.setup_driver()
        
        try:
            self.scrape_food_images(food_name)
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")
        
        logger.info(f"Single food scraping completed for: {food_name}")


def main():
    """Main function to run the scraper"""
    print("Myanmar Food Image Scraper")
    print("=" * 50)
    
    # Configuration
    HEADLESS_MODE = False  # Set to True for headless browsing
    IMAGES_PER_FOOD = 30   # Number of images to download per food type
    
    # Create scraper instance
    scraper = MyanmarFoodScraper(headless=HEADLESS_MODE, images_per_food=IMAGES_PER_FOOD)
    
    print("Choose an option:")
    print("1. Scrape all 20 Myanmar food types")
    print("2. Scrape a specific food type")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\nStarting to scrape all Myanmar food types...")
        print("This may take a while. Please be patient.")
        scraper.scrape_all_foods()
        
    elif choice == "2":
        print("\nAvailable Myanmar food types:")
        for i, food in enumerate(scraper.myanmar_foods, 1):
            print(f"{i:2d}. {food}")
        
        food_choice = input("\nEnter the food name or number: ").strip()
        
        # Check if it's a number
        try:
            food_index = int(food_choice) - 1
            if 0 <= food_index < len(scraper.myanmar_foods):
                selected_food = scraper.myanmar_foods[food_index]
            else:
                print("Invalid number. Please try again.")
                return
        except ValueError:
            # It's a food name
            selected_food = food_choice.lower()
        
        print(f"\nStarting to scrape images for: {selected_food}")
        scraper.scrape_single_food(selected_food)
        
    else:
        print("Invalid choice. Please run the script again.")


if __name__ == "__main__":
    main()
