# Myanmar Food Image Web Scraper

This project scrapes images of 20 popular Myanmar food types from Google Images using Selenium and saves them into organized folders.

## Features

- Scrapes images for 20 Myanmar food types (or a single food type of your choice)
- Each food type is saved in its own folder under `Myanmar_Food_Images`
- Configurable number of images per food type
- Headless mode support for background scraping

## Requirements

- Python 3.7+
- Google Chrome browser installed
- ChromeDriver (automatically managed)
- See `requirements.txt` for Python dependencies

## Installation

1. **Clone this repository or copy the files to your machine.**

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper with:

```bash
python myanmar_food_scraper.py
```

You will be prompted to:
- Scrape all 20 Myanmar food types, or
- Scrape a specific food type (by name or number)

Images will be saved in the `Myanmar_Food_Images` directory, with a subfolder for each food.

## Configuration

- To change the number of images per food or enable headless mode, edit the `HEADLESS_MODE` and `IMAGES_PER_FOOD` variables at the top of `myanmar_food_scraper.py`.

## Notes

- Scraping many images may take several minutes.
- Google Images may block or throttle requests if you scrape too quickly.
- For best results, do not run multiple scrapes in parallel.

## Troubleshooting

- **No images downloaded?**  
  Try increasing the scroll count or check your internet connection. Google may also change its HTML structure, requiring code updates.
- **WebDriver errors?**  
  Make sure you have Google Chrome installed and up to date.

## License

For educational and research use only.
