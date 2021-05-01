# Realestate.com.au sold search scraper

import re
import requests
from lxml import html
import time
import pprint

# ---


# Set scraper parameters here
scrapeDescriptions  = False
outputFilename      = 'scraper_output'
pagesToLoad         = 2
propertyType        = 'house'
includeSurrounding  = False
lotSize = 600
maxPrice = 600000
region = 'logan+city+-+region,+qld'
minBaths = 3

# ---

# Set headers to bypass user agent filtering 
headers = {
          # Insert your user agent 
          #'User-Agent': 'Mozilla/5.0',
          'authority': 'www.realestate.com.au',
          'cache-control': 'max-age=0',
          'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
          'sec-ch-ua-mobile': '?0',
          'dnt': '1',
          'upgrade-insecure-requests': '1',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
          'sec-fetch-site': 'same-origin',
          'sec-fetch-mode': 'navigate',
          'sec-fetch-user': '?1',
          'sec-fetch-dest': 'document',
          #'referer': 'realestate.com.au',
          #'origin': 'https://www.realestate.com.au',
          'accept-language': 'en-AU,en;q=0.9,it-IT;q=0.8,it;q=0.7,ja-JP;q=0.6,ja;q=0.5,en-GB;q=0.4,en-US;q=0.3',
          # Grab cookie from google chrome dev tools
          # 'cookie': 'QSI_HistorySession=https%3A%2F'
        }

def loadPage (url):
  print("Waiting 5 seconds before launching request to avoid getting banned...")
  time.sleep(5)
  print("Sending request...")
  req = requests.get(url, headers=headers)
  print(req.status_code)
  print(req.reason)
  # Send a request and parse the content
  return html.fromstring(req.content)

# ---

def getSearchResults (url, pageNumber):
  # Load the search page and extract the search results
  return loadPage(url.format(pageNumber)).findall('.//div[@class="tiered-results tiered-results--exact"]//article')

# ---

def buildURLString ():

  # Create a template for the URL, as well as for a search description string
  url = 'https://www.realestate.com.au/sold/property-house-size-{}-between-0-{}-in-{}'
  searchDescription = \
    'Searching for {}m2 minimum properties with a sell cost of $0 - ${}.  ' + \
    '{} bathrooms minimum.  ' + \
    'Location: {}'

    
  # Add the remaining parameters to the URL
  url = url + '/list-{}?numBaths={}&misc=ex-no-sale-price&activeSort=solddate&source=refinement'
  url = url.format(lotSize, maxPrice, region, '{}', minBaths)
  print(url)
  
  # Add the remaining parameters to the search description
  searchDescription = searchDescription.format(lotSize, maxPrice, minBaths, region)   
  
  # Print the search description
  print(searchDescription)
  
  # Return the complete URL
  return url

# ---

def parsePriceRange (listing):

  # Prices are listed in various different formats.
  # Here, we try to standardise the way they are displayed.
  # This works for most, but not all, cases
  
  price = listing['Price']
  price = price.replace(' - ', '-')
  price = price.replace(' to ', '-')
  price = price.replace('to', '-')
  price = price.replace('.00', '')
  price = '$' + re.sub('[^\d-]','', price)
  price = price.replace('-', ' - $')
  
  # Record the property price
  listing['Price'] = price

# ---

def parseSuburb (listing):

  # Record the property suburb
  suburb = listing['Link'][listing['Link'].find(propertyType) + len(propertyType) + 5:]
  suburb = suburb[:suburb.find('-')].title()
  suburb = suburb.replace('+', ' ')
  listing['Suburb'] = suburb

# ---

def parseType (listing):
  
  # Record the property type
  propertyType = listing['Link'][len('/property-'):]
  propertyType = propertyType[:propertyType.find('-')].title()
  # Hack / patch
  listing['Type'] = "House"

# ---

def parseListingDetails (article):
  
  # Scrape the data included in the preview article
  listing = {
    'Address'     : scrape(article, './/h2[@class="residential-card__address-heading"]//text()'),
    'Price'       : scrape(article, './/span[@class="property-price "]//text()'),
    'Link'        : scrape(article, './/a[@class="details-link residential-card__details-link"]//@href'),
    'Bedrooms'    : scrape(article, './/ul/li[1]/span'),
    'Bathrooms'   : scrape(article, './/ul/li[2]/span'),
    'Car Spaces'  : scrape(article, './/ul/li[3]/span'),
    'Description' : '',
    'Inspections' : '',
    'Lot Size'    : scrape(article, 'div[4]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]'),
    'Sold Date'   : scrape(article, 'div[4]/div[1]/span')
  }

  
  # Parse various additional details
  parsePriceRange(listing)
  parseSuburb(listing)
  parseType(listing)
  
  # Remove the suburb from the address
  # listing['Address'] = listing['Address'][:listing['Address'].find(',')]
  
  # Append the top-level domain to create a full link
  listing['Link'] = 'https://www.realestate.com.au' + listing['Link']   
  
  # Assume there are no car spaces if the field is empty
  if listing['Car Spaces'] == '':
    listing['Car Spaces'] = '0' 

  # Follow the link and scrape the property description
  if scrapeDescriptions:
    print("Sleeping for 5 to prevent getting banned for scraping...")
    time.sleep(5)
    page = loadPage(listing['Link'])
    listing['Description'] = parseDescription(page)

  listing['Sold Date'] = re.search('\d+.*', listing['Sold Date']).group()
  listing['Lot Size'] = re.search('(\d|,|.)+', listing['Lot Size']).group()
  listing['Lot Size'] = listing['Lot Size'].replace(",", "")

  # Return the listing details
  return listing
  
# ---

# Scrape a certain piece of data from the provided HTML snippet
def scrape (article, xpath):
  result = article.xpath(xpath)
  if len(result) > 0:
    # If the xpath matches an element/attribute, return the result as a string
    if type(result[0]) is html.HtmlElement:
      return result[0].text_content()
    else:
      return result[0]
  else:
    # If no data was found, return an empty string
    return ''
  

# --- Main

try:
  timeStr = time.strftime("%Y%m%d-%H%M%S")
  # Create or load the output file
  outputFile = open(outputFilename + "-" + timeStr + ".csv", 'w')

  # Construct the base URL
  searchURL = buildURLString()

  # Print the search parameters
  print('(' + ('Also' if scrapeDescriptions else 'Not' ) + ' scraping property descriptions)')
  print('\nOutputting to ' + outputFile.name + '.')

  # Record the number of pages and results returned
  totalResults = 0
  pageNumber   = 1
      
  # Create the column headers
  outputFile.write(
    'Link'        + ',' + \
    'Type'        + ',' + \
    'Address'     + ',' + \
    'Suburb'      + ',' + \
    'Price'       + ',' + \
    'Bedrooms'    + ',' + \
    'Bathrooms'   + ',' + \
    'Car Spaces'  + ',' + \
    'Description' + ',' + \
    'Lot Size'    + ',' + \
    'Sold Date'   + ',' + '\n'
  )

  # Begin requesting each page sequentially
  while pageNumber <= pagesToLoad:

    print("Printing page {} ...\n".format(pageNumber))

    # Send a request, parse the response and retrieve the search results
    print('\nRequesting page ' + str(pageNumber) + '...')
    searchResults = getSearchResults(searchURL, pageNumber)
    pageNumber += 1
    
    # Record the number of results returned
    print(str(len(searchResults)) + ' results returned')
    totalResults += len(searchResults)
    
    # If no results were returned, stop searching
    if len(searchResults) == 0:
      break
    
    # Iterate through the search results
    for article in searchResults:
    
      # Extract the listing details from the result article
      listing = parseListingDetails(article)
      
      # Write the full details to the output file
      outputFile.write(
        listing['Link']        + ',' + \
        listing['Type']        + ',' + \
        listing['Address']     + ',' + \
        # listing['Suburb']      + ',' + \
        listing['Price']       + ',' + \
        listing['Bedrooms']    + ',' + \
        listing['Bathrooms']   + ',' + \
        listing['Car Spaces']  + ',' + \
        listing['Description'] + ',' + \
        listing['Lot Size']  + ',' + \
        listing['Sold Date']   + ','  + '\n'
      )
      
      # Only print a partial address to the console
      maxLen  = 15
      address = listing['Address'].ljust(maxLen) if len(listing['Address']) <= maxLen else listing['Address'][:maxLen]
      
      # Print a trimmed version to the console
      print(
        address                         + '\t\t' + \
        # listing['Suburb'].ljust(maxLen) + '\t\t' + \
        listing['Price']                + '\t' + \
        listing['Bedrooms']             + '\t' + \
        listing['Bathrooms']
      )
    
  # Finally, display the total number of search results returned
  print('\nTotal results returned: ' + str(totalResults))
  
except KeyboardInterrupt:
  print('Search cancelled.')
except PermissionError:
  print('Couldn\'t write to output file (make sure you don\'t have the file open!)')
except requests.exceptions.ConnectionError:
  print('Couldn\'t connect.')