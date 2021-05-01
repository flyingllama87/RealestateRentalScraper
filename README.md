# Real estate scrapers and scripts
- A scraper for recently sold properties listed on realestate.com.au that fits my specific criteria (stage 1).
- A 'house size' (not lot size) and 'year built' scraper for onthehouse.com.au (stage 2).
- A Google Sheets script to assign a 'score' to each property based on criteria such as cost, lot size, year built, house size, proximity to parks etc (stage 3).

This was for a once off project and thus each 'stage' needs its output data massaged into the format required by the next stage. Be warned, these scripts are quick and dirty.

### Legal notice (aka Scraping and you)

Bulk scraping or indexing of content from either website is against the ToS of the respective sites. I justify the use of scripts in that:
 - My criteria is highly specific (not bulk collection)
 - I only scrape 2 pages of content
 - I've looked at most of these ads & check the URIs for each anyway for other assessment criteria not contained in these scripts (e.g. build quality, proximity to parks etc)
 - Personal use only; data collected does not go to anyone else
 - I have a 5 second sleep between each request so as not to make excessive traffic demands

Please keep the ToS in mind when using these scripts.

The purpose of these scripts are to better inform my purchasing decisions in a structured manner AND for educational purposes. I could have compiled this information manually but where is the fun in that? :)

### realestate.com.au sold scraper (RealestateSoldScraper.py):

- Quick and dirty hack of [DPerrySvendsen's RealestateRentalScraper](https://github.com/DPerrySvendsen/RealestateRentalScraper). Thanks dude. I hope you found a sweet rental!
- Aggregates the data into a CSV file that can be viewed in any spreadsheet app (see `scraper_output-20210501-010101-example` for an example).
- Uses Python's request library. Needs you to grab a realestate.com.au cookie & UA from Chrome developer tools or something else. Maybe more appropriate to use selenium.

### onthehouse.com.au scraper (OnTheHouseScraper.py):

- Grabs the 'Year built' & 'house size' information from onthehouse.com.au for addresses listed in the addresses.txt file. This data is sometimes inaccurate but is mostly correct and looking up each property in my council's PD site takes too long. Ads on realestate.com.au often omit this information.
- Uses Selenium to avoid messing about with headers.
- Looks up the post codes for the suburbs listed in the addresses.txt file via the `queensland_postcodes.csv` file.
- See `output-20210428-010101-example.csv` for example output.

### Google Sheets Property Score Calculator (GoogleSheetsHouseScore.gs):

- Script for Google Sheets to assign a 'score' to each property based on my own specific criteria. See `GoogleSheets-example.csv` for example on how the sheet should be set up for the script to work.