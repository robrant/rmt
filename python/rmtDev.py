"""
What do I want to be able to do?

1. Take a given rightMove URL and hit it

2. Retrieve the HTML results
3. Parse the HTML results into discrete results (a table?)
4. Break out the details I'd want to keep. They are:
    a. RightMove.co.uk reference # (validation of property - probably doesn't account for changes by agent)
    b. Price (change in price detection)
    c. Address (validation of property)
    d. Agent details (change of agent detection)
    e. Description
    f. Source page (country props, etc) update date?
    
5. Store these parameters in the data store. Also store:
    a. The date of the  pull - the last date the code checked the site
    b. Subtle changes to the content - description, # of photos, update dtg of the source page.

    
6. Insert into Mongo - records collection.
    Do with a test case working from a textfile of sample data retrieved from the web:
    a. Create a collection
    b. Build a document
    c. Insert it into the collection
    d. Modify a field
    e. Check the date field
    f. Retrieve a document element
    g. Delete a document element
    
    
7. Look for changes.
    a. Does a property go off the market? If so, flag and add a field value for off market date.
    b. Does a property appear to change agents?
    c. Do any of the properties associated with the property change?
    d. Specifically, does the price of the property change? Flag it and record the new price.
       And the date at which it was last seen at the last price.
       





Breaking out the URL:
http://www.rightmove.co.uk/property-for-sale/find.html?

searchType=SALE&
locationIdentifier=REGION^643
&insId=1
&radius=5.0
&displayPropertyType=flats
&minBedrooms=1
&maxBedrooms=2
&minPrice=150000
&maxPrice=400000
&retirement=&
partBuyPartRent=&
maxDaysSinceAdded=1&
includeSSTC=true
&_includeSSTC=on&
sortByPriceDescending=&
primaryDisplayPropertyType=&
secondaryDisplayPropertyType=&
oldDisplayPropertyType=&
oldPrimaryDisplayPropertyType=&
newHome=&
auction=false



"""
import re
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
import string
import datetime
import time

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class prop():
    
    def __init__(self, id=None):
        '''Makes all the necessary attributes available.    '''
        
        self.prop_id            = id
        self.prop_address       = ''
        self.prop_type          = ''
        self.prop_wing          = ''
        self.prop_bedrooms      = 0
        self.prop_details       = ''
        self.prop_price         = 0
        self.prop_price_qualifier= ''
        self.ff_score           = 0
        self.agent_name         = ''
        self.agent_address      = ''
        self.observation_date   = datetime.datetime(2000,1,1,0,0)

    def buildDictionary(self):
        ''' Compiles all the attributes into a dictionary for inserting.   '''
        
        d = {'property_id':             self.prop_id,
             'property_address':        self.prop_address,
             'property_type':           self.prop_type,
             'property_wing':           self.prop_wing,
             'property_bedrooms':       self.prop_bedrooms,
             'property_details':        self.prop_details,
             'property_price':          self.prop_price,
             'property_price_qualifier':self.prop_price_qualifier,
             'fairfield_score':         self.ff_score,
             'agent_name':              self.agent_name,
             'agent_address':           self.agent_address,
             'observation_date':        self.observation_date
             }
     
        return d

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def getResultsPage(url):
    ''' Using the given URL returns the webpage full text.'''
    
    # Set some headers to look like a browser
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    textData = None
    req = urllib2.Request(url, textData, headers)
    response = urllib2.urlopen(req)
    return response

#------------------------------------------------------------------------------#    
def getSoup(response):
    ''' Uses BeautifulSoup to parse the page content.'''
    
    data = response.read()
    soup = BeautifulSoup(data)
    return soup

#------------------------------------------------------------------------------#    
    
def getPagesNumText(soup):
    ''' Get the html page number text from the page. '''
    
    pageText=None
    # Example: <span class="pagenavigation pagecount">page 11 of 18</span>
    span = soup.find('span', attrs={'class':'pagenavigation pagecount'})
    pageTxt = span.renderContents()    
    
    return pageTxt
    
#------------------------------------------------------------------------------#

def getPageCount(pageTxt):
    ''' Get the total number of pages as an integer '''
    
    pageCount=None
    if pageTxt==None:
        return None
    
    regEx = re.compile('\d+')
    res = regEx.findall(pageTxt)
    if res:
        nums = [int(x) for x in res]
        pageCount = max(nums)
        
    return pageCount

#------------------------------------------------------------------------------#

def buildPageList(url, pages):
    ''' Build a list of links to all of the pages.  '''
    
    resultsPages = []
    # Loop an integer range and build the links to the other results pages
    for x in range(pages+1):
        index = "index=%s0" %(x)
        pageUrl = "%s&%s" %(url, index)
        resultsPages.append(pageUrl)

    return resultsPages

#------------------------------------------------------------------------------#    
    
def buildPropertyUrl(ref):
    ''' Builds the url for the details page for each property. '''

    propertyUrl = "http://www.rightmove.co.uk/property-for-sale/property-%s.html" %(ref)
    return propertyUrl

#------------------------------------------------------------------------------#    
    
def getPropertyLinks(soup):
    ''' Retrieves the property ID from the search results page '''
    
    regExPattern = re.compile('summary\d*')
    
    # Get the ordered list of properties from the page
    resultSet = soup.find('ol', attrs={'id':'summaries'})
    results = resultSet.findAll('li', attrs={'id':regExPattern})

    ids = []
    for result in results:
        result = result['id'].lstrip('summary')
        ids.append(result)
        
    return ids

#------------------------------------------------------------------------------#

def stripPropertyId(idAttribute):
    ''' Strips out the property ID into an integer from the idAttribute'''
    
    propId = int(idAttribute.lstrip('summary'))
    return propId
    
#------------------------------------------------------------------------------#

def getPropertyAmount(page):
    ''' Get the property amount from the property page.    '''

    try:
        amount = page.find('div', attrs={'id':'amount'}).renderContents()
        amount = int(amount.split(';')[1].replace(',',''))
    except:
        print "Failed to extract the property sale amount."

    return amount
#------------------------------------------------------------------------------#

def getPriceQualifier(page):
    ''' Get the property price qualifier.    '''

    try:
        price = page.find('div', attrs={'id':'propertyprice'})
        qual  = price.find('div', attrs={'id':'pricequalifier'})
        qual = qual.renderContents().lower()
    except:
        return None
        #print "Failed to extract the property qualifier."

    return qual

#------------------------------------------------------------------------------#

def getPropertyDetails(page):
    ''' Get the property details shbeel from the property page.    '''

    try:
        propDetails = page.find('div', attrs={'class':'propertyDetailDescription'})
    except:
        print "Failed to get the property detailed description."
    try:
        propDetails = propDetails.renderContents().lower()
    except:
        print "Failed to get the detailed property description content."
    
    return propDetails

#------------------------------------------------------------------------------#

def getPropertyAddress(page):
    ''' Get the property amount from the property page.    '''

    try:
        address = page.find('div', attrs={'id':'addresscontainer'})
        address = address.find('h2').renderContents().lower()
    except:
        print "Failed to extract the property address."
    return address

#------------------------------------------------------------------------------#

def getPropertyWing(text):
    ''' Get which wing the property is in. '''

    wingExp = re.compile(r'(.*)(Wing)', re.IGNORECASE)
    wing = wingExp.search(text).groups()
    
    if len(wing) > 1:
        wing = wing[0].lower().strip()
        
        stripChars = ['-',':','_',' ',',',';']
        for char in stripChars:
            wing = wing.strip(char)
        if len(wing) == 0:
            return None
        return wing
    
    else:
        return None

#------------------------------------------------------------------------------#

def getPropertyType(page):
    ''' Get the property amount from the property page. Either returns # bedrooms
        or 0 for studio or -1 for not found.'''

    try:
        propType = page.find('h1', attrs={'id':'propertytype'})
        propType = propType.renderContents().lower()
        # Look for retirement and skip
        if propType.find('retirement') != -1:
            return "",-1
        
        # Look for bedrooms 
        regEx = re.compile(r'^(\d+) (\bbedroom\b)')
        res = regEx.search(propType).groups()
        if len(res)==2: 
            return propType, int(res[0])
        
        # Look for studio
        regEx = re.compile(r'^(\bstudio\b)')
        res = regEx.search(propType).groups()
        if len(res)!=0:
            return propType, 0
        
        # Not studio and not able to parse # bedrooms
        return "",-1
    except:
        print "Failed to run regular expression. Errored."
        return "",-1
    
#------------------------------------------------------------------------------#

def getAgentAddress(page):
    ''' Get the agent details from the property page.    '''

    try:
        agentDetails = page.find('div', attrs={'id':'agentdetails'})
    except:
        print "Failed to extract the agent details tag." 
    try:
        # Strip down and rebuild the string
        agentAdd = agentDetails.find('div', attrs={'id':'branchaddress'})
        agentAdd = agentAdd.renderContents().strip().lower()
        ad = string.join([i.strip() for i in agentAdd.split(',')], ',')
        return ad     
    except:
        print "Failed to extract the agent address and name."
    
#------------------------------------------------------------------------------#

def getTitleUrl(page):
    ''' Get the agent URL from the property page.    '''

    try:
        agentDetails = page.find('div', attrs={'id':'agentdetails'})
    except:
        print "Failed to extract the agent details tag." 
    try:
        agentA     = (agentDetails.find('h2')).find('a')
        #Strip off the .html, split it by / and take the last 2 elements for joining
        agentUrl   = string.join(agentA['href'].strip('.html').split('/')[-2:], '-').lower()
    except:
        print "Failed to extract the agent address and name."

    return agentUrl

#------------------------------------------------------------------------------#

def getFairfield(text):
    ''' Checks for the presence of the word Fairfield, Hall, kingsley, wing (broken and not)  '''

    matchScore = 0
    testStrings = [r"(fiarfield)",r"(fairfield)", r"(hall)", 
                   r"(wing)", r"(kingsley)"]

    for test in testStrings:
        if re.search(test, text.lower()) != None:
            matchScore += 1

    return matchScore

#------------------------------------------------------------------------------#

def main():
    ''' Holds it together '''

    # Establish the URL
    url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE^3820481&minPrice=150000&maxPrice=400000&displayPropertyType=flats&oldDisplayPropertyType=flats&radius=5.0&includeSSTC=true&_includeSSTC=on"

    #Get the search result - the first page returned from the query
    response = getResultsPage(url)
    splashSoup = getSoup(response)
    
    # Get the number of pages to be processed
    numPages = getPagesNumText(splashSoup)
    numPages = getPageCount(numPages)
    
    # Build the list of results pages to be processed
    pagesToBeProcessed = buildPageList(url, numPages)

    propertiesReady = []

    #Loop through the results pages
    for pageURL in pagesToBeProcessed:
        
        print "==================================================="
        print "==================================================="
        #time.sleep(random.randint(30-120))
        
        # Get the content of this results page (this includes the zero-th)
        try:
            response = getResultsPage(pageURL)
            soup = getSoup(response)
        except BeautifulSoup.HTMLParser.HTMLParseError, e:
            print e
        
        #Loop through the property links
        propertyIds = getPropertyLinks(soup)
        
        # For each property link - get the page
        for propId in propertyIds:
            
            print propId
            
            # Build a property object - using prop class.
            p = prop(id=propId)
    
            # Open the property page
            propURL = buildPropertyUrl(propId)
            response = getResultsPage(propURL)
            soup = getSoup(response)
    
            # Get the price
            p.prop_price = getPropertyAmount(soup)

            # Get the price qualifier 
            p.prop_price_qualifier = getPriceQualifier(soup)
            
            print p.prop_price, p.prop_price_qualifier
            
            """
            ******
            Also appears to be a problem souping some of the html. There is currently a catch
            in place, but that means it will miss some of the pages, which is a problem.
            
            Is there a way to validate the html?
            
            Then work your way down through each of the extra function calls and check they work.
            
            Then loop through the list or go straight to a pymongo function to do the insert.
            
            ******
            
            # Get the address
            p.prop_address = getPropertyAddress(soup)
            
            # Get the # bedrooms/prop type
            p.prop_type,p.prop_bedrooms = getPropertyType(soup)
            
            # Get the main details
            p.prop_details = getPropertyDetails(soup)
            
            # Get the property wing (try summary first)
            p.prop_wing = getPropertyWing(p.prop_address)
            
            # Go to main text if not in address
            if not p.prop_wing:
                p.prop_wing = getPropertyWing(p.prop_details)
            
            # Get the Fairfield matching score
            p.ff_score = getFairfield(p.prop_address)

            # If not able to get it from address, look in main text
            if not p.ff_score:
                p.ff_score = getFairfield(p.prop_details)
            
            # Get the agent name
            p.agent_name = getTitleUrl(soup)
            
            # Get the agent address
            p.agent_address = getAgentAddress(soup)
            
            # Populate the observation date
            p.observation_date = datetime.datetime.utcnow()
            
            # Build the dictionary
            propertyReady = p.buildDictionary()
            propertiesReady.append(propertyReady)

for prop in propertiesReady:

    db.... insert()

"""
'''
*** TESTS WORK. NEED TO WRITE SOMETHING TO TIE IT ALL TOGETHER FOR

- LOOPING RESULTS PAGES
- LOOPING PROPERTIES ON EACH OF THE PAGES
- EXTRACTING CONTENT FROM EACH OF THE PAGES.

Then:
Mongo inserting... and schema/linking?
Dealing with change of agent?
Last date on market?
First date of observation?
Change in price?
Categories under the mongo - #bedrooms, price, wing, address, features, 
aspect? windows? floor? 


'''

#main()














# open a file
"""
input = open('/home/robrant/projects/rightMove/data/testOut.txt', 'r')
soup = BeautifulSoup(input)
input.close()

summs = getPropertyLinks(soup)
for sum in summs:
    summaryIdx = sum['id']
    print stripPropertyId(summaryIdx)
"""

