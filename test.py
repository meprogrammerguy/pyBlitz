#!/usr/bin/env python3

from selenium import webdriver
import time
import pdb
 
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.binary_location = "/usr/lib/chromium-browser/chromedriver"
driver = webdriver.Chrome(chrome_options=options)
driver.get('http://www.bornpowerindex.com/M_COL_FB_CLASS.shtml')
list_of_elements = driver.find_elements_by_xpath('//td')
list_of_text = [t.text for t in driver.find_elements_by_xpath('//td')] 
list_of_elements[15].click()
pdb.set_trace()

