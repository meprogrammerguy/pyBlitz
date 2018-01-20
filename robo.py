#!/usr/bin/env python3

from robobrowser import RoboBrowser
import pdb

browser = RoboBrowser()
browser.open("http://www.bornpowerindex.com/M_COL_FB_CLASS.shtml")
form = browser.get_forms()[0]
browser.submit_form(form)
pdb.set_trace()
