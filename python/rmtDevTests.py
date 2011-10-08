'''
Created on Sep 25, 2011

@author: robrant
'''
import unittest
import rmtDev as rmt
from BeautifulSoup import BeautifulSoup
import re

class Test(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def testUrlBuilder(self):
        '''Test the correct URL gets built for a specific property: '''
        id = 3650810
        answer="http://www.rightmove.co.uk/property-for-sale/property-3650810.html"
        url=rmt.buildPropertyUrl(ref=id)
        self.assertEquals(url, answer)

    def testgetResultsPage(self):
        ''' Tests the return of data from website: ''' 
        
        url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE^3820481&minPrice=150000&maxPrice=400000&displayPropertyType=flats&oldDisplayPropertyType=flats&radius=5.0&includeSSTC=true&_includeSSTC=on"
        response = rmt.getResultsPage(url)
        page = response.read()

        openPage  = page.find('<html ')
        rMove     = page.find('RIGHTMOVE_REQUEST')
        closePage = page.find('</html>')
        self.assertTrue(openPage > 0)
        self.assertTrue(rMove > 1)
        self.assertTrue(closePage> 0)

    def testgetSoup(self):
        ''' Tests for ability to read html soup input.'''
    
        #Open a file of HTML
        input = open('/home/robrant/projects/rightMove/data/testOut.txt', 'r')
        soup = rmt.getSoup(input)
        input.close()
        
        # Check its a BS instance and has children
        self.assertTrue(isinstance(soup, BeautifulSoup))    
        children = soup.findChildren()
        self.assertTrue(len(children) > 0)
        

    def testgetPagesNumText(self):
        ''' Get the list of results page links'''
        
        input = open('/home/robrant/projects/rightMove/data/testOut.txt', 'r')
        data = BeautifulSoup(input)
        input.close()
        
        pages = rmt.getPagesNumText(data)
        self.assertNotEqual(pages, None)
        self.assertTrue(len(pages) > 0)

    def testgetPageCountGood(self):
        ''' Successfully get the integer # of pages.'''
        
        answer = 18
        pageText = "        page 1 of %s" %(answer)
        pages = rmt.getPageCount(pageText)
        self.assertNotEqual(pages, None)
        self.assertEquals(pages, answer)

    def testgetPageCountBad(self):
        ''' Fail to get the page count.'''
        
        pageText = "Nothing Found"
        pages = rmt.getPageCount(pageText)
        self.assertEquals(pages, None)

    def testbuildPageList(self):
        ''' Check pages url list was successful: '''
        
        numPages = 18
        url = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE^3820481&minPrice=150000&maxPrice=400000&displayPropertyType=flats&oldDisplayPropertyType=flats&radius=5.0&includeSSTC=true&_includeSSTC=on"
        ans = "http://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE^3820481&minPrice=150000&maxPrice=400000&displayPropertyType=flats&oldDisplayPropertyType=flats&radius=5.0&includeSSTC=true&_includeSSTC=on&index=110"
        pageList = rmt.buildPageList(url, numPages)
        self.assertEquals(len(pageList),numPages+1)
        self.assertEquals(pageList[11], ans)
    
    
    def testgetPropertyLinks(self):
        '''Check extraction of property IDs.'''
        
        # open a file
        input = open('/home/robrant/projects/rightMove/data/testOut.txt', 'r')
        soup = BeautifulSoup(input)
        input.close()
        ans = 34065812

        # Get the IDs on this results page
        propIds = rmt.getPropertyLinks(soup)
        self.assertEquals(int(propIds[0]), ans)
    
    def testPropertyIds(self):
        ''' Extract ID successfully'''
        
        idAttribute = 'summary34065812'
        ans = 34065812
        x = rmt.stripPropertyId(idAttribute)
        self.assertEquals(x, ans)

    def testgetPropertyAmount(self):
        '''Extract property details    '''
        
        input = open('/home/robrant/projects/rightMove/data/property-30895648.html')
        soup = BeautifulSoup(input)
        input.close()
        self.assertEquals(279950, rmt.getPropertyAmount(soup))

    def testgetPriceQualifier(self):
        ''' Extract a property qualifier '''

        input = open('/home/robrant/projects/rightMove/data/property-24994747.html')
        soup = BeautifulSoup(input)
        input.close()
        qualifier = rmt.getPriceQualifier(soup)
        self.assertEquals(qualifier, "offers in excess of")
        

    def testgetPropertyDetails(self):
        '''Extract property details    '''
        
        input = open('/home/robrant/projects/rightMove/data/property-30895648.html')
        soup = BeautifulSoup(input)
        input.close()
        x = rmt.getPropertyDetails(soup)
        self.assertTrue(len(x) > 100)

    def testgetPropertyAddress(self):
        '''Extract property address    '''
        
        input = open('/home/robrant/projects/rightMove/data/property-30895648.html')
        soup = BeautifulSoup(input)
        input.close()
        answer = 'east wing, fairfield hall, stotfold, beds'
        address = rmt.getPropertyAddress(soup)
        self.assertEquals(address, answer)
    
    def testgetPropertyType(self):
        '''Extract property type '''
        
        input = open('/home/robrant/projects/rightMove/data/property-30895648.html')
        soup = BeautifulSoup(input)
        input.close()
        answer = "2 bedroom flat for sale"
        
        propType, numBeds = rmt.getPropertyType(soup)
        self.assertEquals(propType, answer)
        self.assertEquals(numBeds, 2)

    
    def testgetAgentAddress(self):
        '''Extract property estate agent    '''
        
        input = open('/home/robrant/projects/rightMove/data/property-30895648.html')
        soup = BeautifulSoup(input)
        input.close()
        answer = "4 brand street,hitchin,sg5 1hx"
        addr = rmt.getAgentAddress(soup)
        self.assertEquals(addr, answer)

    def testgetTitleUrl(self):
        ''' Extract the title and the EA URL '''
        
        input = open('/home/robrant/projects/rightMove/data/property-30895648.html')
        soup = BeautifulSoup(input)
        input.close()
        answer = "stonegate-estates-hitchin-sales-15848"
        url = rmt.getTitleUrl(soup)
        self.assertEquals(url, answer)
    
    
    def testgetFairfield(self):
        ''' Dig out words associated with fairfield hall'''
        
        text = "South Wing FAIRFIELD HALL, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 3)
        text = "SouthWingFairfieldHALL, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 3)
        text = "South Wing Fairfield Hall, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 3)
        text = "Southwing Fairfield Hall, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 3)
        text = "South Wing Fairfield Park, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 2)
        text = "South Hall Wing Fairfield, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 3)
        text = "SouthWing Fairfield Park, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 2)
        text = "Fairfield Park, Kingsley Avenue, Bedfordshire"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 2)
        text = "Nothing to see here!"
        out = rmt.getFairfield(text) ; self.assertEquals(out, 0)
    
    def testgetPropertyWing(self):
        ''' Extract the wing from the property details'''

        text = 'southwing'
        self.assertEquals(rmt.getPropertyWing(text), 'south')
        text = 'south wing'
        self.assertEquals(rmt.getPropertyWing(text), 'south')
        text = 'South Wing'
        self.assertEquals(rmt.getPropertyWing(text), 'south')
        text = 'South-Wing'
        self.assertEquals(rmt.getPropertyWing(text), 'south')
        text = 'Wing'
        self.assertEquals(rmt.getPropertyWing(text), None)

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()