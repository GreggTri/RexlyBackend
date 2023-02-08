import logging
import traceback
import os
from .walmartAPI import walmartAPI
import ast

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def bayesianAverage(rating, numReviews):
    #constant values that determine the weight of the average rating and the total number of ratings
    alpha = 20 #bias towards rating
    beta = .3 #bias towards number of ratings
    
    #compute the Bayesian average rating
    return (alpha * rating + beta * numReviews) / (alpha + beta)

async def searchRetailers(query):
    
    
    maxPrice = None
    color = None
    listOfColors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'brown', 'gray', 'black', 'white']
    listOfFillerWords = ['i', 'm' ,'looking', 'for', 'need', 'want', 'you', 'got', 'do', 'what', 'any', 'really', 'a', '\'m', 'around']

    #making the search query more potent
    for lColor in listOfColors:
        if lColor in query:
            query.remove(lColor)
            color = lColor.capitalize()
    
    for fWord in listOfFillerWords:
        if fWord in query:
            query.remove(fWord)
    
    for word in query:
        try:
            maxPrice = ast.literal_eval(word)
            query.remove(word)
        except:
            pass
        
    if len(query) == 0:
        return {
            "success": False,
            "error": "Query len is 0"
        }
        
    bestItems = []
    a = 1
    query = ' '.join(query)
    
    try:
        
        facetColor = ''
        if color is not None:
            facetColor = f"&facet.filter=color:{color}"
        
        while True:
            url = f"search?publisherId={os.getenv('PUBLISHER_ID')}&query={query}&start={a}&numItems=25&responseGroup=full&facet=on&facet.filter=availableOnline:true&facet.filter=stock:Available"
            response_WAL = await walmartAPI(f"{url}{facetColor}")
            
            if response_WAL == False:
                return {
                    "success": False,
                    "error": "Error from walmartAPI"
                }
            
            totalCount = response_WAL['totalResults']
            
            for i in range(len(response_WAL['items'])):   
                if response_WAL['items'][i].get('numReviews') is not None and (maxPrice is None or float(response_WAL['items'][i]['salePrice']) <= maxPrice):
                    
                    #add only the necessary fields
                    #for complete list of fields go here: https://walmart.io/docs/affiliate/search
                    item = {
                        "name": response_WAL['items'][i]['name'],
                        "salePrice": response_WAL['items'][i]['salePrice'],
                        "numReviews": response_WAL['items'][i]['numReviews'],
                        "customerRating": response_WAL['items'][i]['customerRating'],
                        "productTrackingUrl": response_WAL['items'][i]['productTrackingUrl']
                    }
                    
                    #probably some other command needs to be used
                    bestItems.append(item)
            
            #iterates to the next batch of products from walmart
            a += 25
            #condition to break out of while loop
            if len(bestItems) > 13 or  a > 150 or a > int(totalCount):
                break
        
        print(f"Searched Through a total of {a} items to find {len(bestItems)} Best Items")
        bestItems.sort(key=itemSort, reverse=True)
        
        return {
            "success": True,
            "data": bestItems[:3]
            }
        
    except Exception as e:

        logger.critical(f"{e}", exc_info=True)
        
        return {
            "success": False,
            "error": "Something went wrong when calling Walmart"
        }

def itemSort(item):
    return bayesianAverage(float(item['customerRating']), float(item['numReviews']))
