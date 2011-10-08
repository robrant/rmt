import pymongo

'''
1. Match against Fairfield
2. Details of agent from URL
3. Agent address
4. Property type details
5. Bedrooms
6. Property address
7. Long text property details.
8. Price Qualifier
9. Price
10. Property ID
'''



import datetime

class prop():
    
    def __init__(self):
        '''Makes all the necessary attributes available.    '''
        
        self.prop_id            = ''
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
     
     