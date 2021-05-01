import re
import requests
from lxml import html
import time
import csv

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

suburb_dict = {
  "test": "9999"
}

def getSearchResults (url, pageNumber):
  # Load the search page and extract the search results
  return loadPage(url.findall('.//div[@class="tiered-results tiered-results--exact"]//article'))

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

def buildURLString(suburb, postcode, street, streetNum):
  pgNum = 1
  # https://www.onthehouse.com.au/property/qld/(suburb)-(postcode)/(street)?streetNumber=(number)
  url = 'https://www.onthehouse.com.au/property/qld/{}-{}/{}?streetNumber={}'
  url = url.format(
      suburb,
      postcode,
      street,
      streetNum)
  print(url)
  return url

def resolvePostcode(suburb):
  retVal = "DEADBEEF"
  if suburb.upper() in suburb_dict:
    print(suburb + " postal code is " + suburb_dict.get(suburb.upper()))
    retVal = suburb_dict.get(suburb.upper())
  return retVal

def loadSuburbDict():
  with open('queensland_postcodes.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
      if line_count == 0:
          print(f'Column names are {", ".join(row)}')
          line_count += 1
      # print(f'\t{row["SUBURB"]} has the postcode {row["POSTCODE"]}.')
      suburb_dict.update({row["SUBURB"]: row["POSTCODE"]})
      line_count += 1
  print(f'Processed {line_count} lines.')

def addressList():
  with open('addresses.txt', mode='r') as addressesFile:
    for address in addressesFile:
      yield address

def openOutputFile():
  timeStr = time.strftime("%Y%m%d-%H%M%S")
  # Create or load the output file
  # outputFile = open(outputFilename + "-" + timeStr + ".csv", 'w')
  csvfile = open(f"output-{timeStr}.csv", 'w+', newline='')
  outputFile = csv.writer(csvfile)
  outputFile.writerow(['Address', 'Year Built', 'Floor Size'])
  return outputFile

def urlFormatStr(text):
  text = text.lower()
  text = text.replace(" ", "-")
  return text

def splitAddress(streetAddress):
  street = re.match("(\d+[A-Za-z]?-?\d*) (\D+)$", streetAddress).group(2).replace(" ", "-").lower()
  num = re.match("(\d+[A-Za-z]?-?\d*) (\D+)$", streetAddress).group(1)
  return num, street


def initSelenium():
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('--no-sandbox')
  # chrome_options.add_argument('--headless')
  chrome_options.add_argument('--disable-dev-shm-usage')
  browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=chrome_options)
  return browser

def grabData(browser):
  xpath = "//*[contains(@class,'PropertyCardSearch__propertyCard')]"
  browser.find_element_by_xpath(xpath).click()
  time.sleep(3)
  
  try:
    yrBuilt = browser.find_element_by_xpath("/html/body/div[1]/div/div[2]/div[1]/div[3]/div[3]/div[1]/div[2]/div/div/div[4]").text
  except:
    print("Failed to get build date")
    yrBuilt = "0000"

  try:
    floorSize = browser.find_element_by_xpath("/html/body/div[1]/div/div[2]/div[1]/div[3]/div[3]/div[1]/div[2]/div/div/div[6]").text
  except:
    print("Failed to get floor size")
    floorSize = "0m2"

  return yrBuilt, floorSize


## Main

browser = initSelenium()
listOfAddresses=addressList()
loadSuburbDict()

outputFile = openOutputFile()

for address in listOfAddresses:
  time.sleep(5)
  print("\n\n" + address + "\n\n")
  addrPart = address.split(",")
  streetAddr = addrPart[0]
  suburb = addrPart[1].lstrip(" -").rstrip("\n")
  postcode = resolvePostcode(suburb)
  streetNum, streetName = splitAddress(streetAddr)
  suburb = urlFormatStr(suburb)
  url = buildURLString(suburb=suburb, postcode=postcode, street=streetName, streetNum=streetNum)
  browser.get(url)
  pageCode = browser.find_element_by_xpath("/html").get_attribute('innerHTML')
  try:
    with open('debug.html', mode='w+') as debugDump:
      debugDump.writelines(pageCode)
  except:
    pass
  yrBuilt, floorSize = grabData(browser)
  print(floorSize)
  print(yrBuilt)
  outputLine = [f"{streetNum} {streetName}, {suburb}", yrBuilt, floorSize]
  outputFile.writerow(outputLine)

