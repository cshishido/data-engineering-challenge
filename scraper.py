import requests
import re
import json

class ApartmentlistScraper():

    api_domain = 'https://api.apartmentlist.com'
    auth_endpoint = api_domain + '/v4/users/ensure_user'
    listings_endpoint = api_domain + '/listings-search/listings'

    def __init__(self) -> None:
        self.session = requests.Session()

        self.headers = { # Mostly copied headers sent by browser
            'Host': 'api.apartmentlist.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.apartmentlist.com/',
            'Content-Type': 'application/json',
            'Authorization': 'Token token=3d68b77b52cc4ac7902b103e6c8834e4', 
            # This token appears to stay the same between between browers sessions, 
            # so for the purpose of this challenge it can remain hard-coded here.
            'Origin': 'https://www.apartmentlist.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            }

        self.get_auth_cookie()

    def get_auth_cookie(self) -> None:
        """
        Aquire the necessary authkey cookie for the session to make api requests
        """        
        # post to endpoint to get auth_token
        response = self.session.post(self.auth_endpoint, headers=self.headers)

        # Raise an error if request was unsuccessful. I'm considering more complex error handling outside the scope of the challenge.
        response.raise_for_status()

    def get_rental_ids(self):
        """
        Get rental_id's for Evanston, IL
        """

        # I need to get all id's in Evanston in order to get the listing data from the api.
        # To do this I am simply regex-ing every "rental_id" from the Evanston page on apartmentlist

        # This method makes the big assumption that every Evanston id will be in the html, which may not be the case.
        # I noticed that there were a few id's different between this page and 'https://www.apartmentlist.com/il/evanston/page-2', for exmple.
        # For the sake of scope, I'm not going down that rabbit hole, 
        # but when building a scraper for-real more investigation would be need to ensure we're not missing any ids.

        evanston_page1_url = 'http://www.apartmentlist.com/il/evanston'
        rental_id_pattern = r'"rental_id":"(.+?)"'
        rental_id_re = re.compile(rental_id_pattern)

        response = self.session.get(evanston_page1_url)
        response.raise_for_status()

        ids = rental_id_re.findall(response.text)

        return set(ids) # return id's as a sent since we only want unique values

    def get_listing_data(self, rental_ids):
        """
        Get listing data for all rentals in rental_ids set from listings api endpoint
        """
        properties_to_query = ['address',
                               'amenities',
                               'all_units', # getting all_units, not just available_units
                              ]
        payload = {'rental_ids': ','.join(rental_ids),
                   'only': ','.join(properties_to_query)}

        response = self.session.get(self.listings_endpoint, headers=self.headers, params=payload)
        response.raise_for_status()

        listing_data = json.loads(response.text)
        return listing_data

        
if __name__ == '__main__':
    scraper = ApartmentlistScraper()
    ids = scraper.get_rental_ids()
    data = scraper.get_listing_data(ids)
    print(data)