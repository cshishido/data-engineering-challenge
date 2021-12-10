import requests
import re
import os
import json
import psycopg2
from psycopg2.extras import execute_values

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

        return list(set(ids)) # cast id's as a sent since we only want unique values


    def get_listing_batch(self, rental_ids):
        """
        Get listing data for all rentals in rental_ids batch list from listings api endpoint
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


    def get_listing_data(self, rental_ids):
        """
        Get all listings in batches of 250 records
        """

        listings = []

        rental_ids_list = list(rental_ids)
        while rental_ids_list:
            # take the first 250 rental_ids, then remove them from the list 
            # (since api response appears to limited to 250 record)
            rental_ids_batch = rental_ids_list[:250]
            rental_ids_list = rental_ids_list[250:]

            listing_data = self.get_listing_batch(rental_ids_batch)

            listings += listing_data['listings']

        return listings


class ApartmentlistLoader():

    def __init__(self, dsn) -> None:
        self.conn = None
        self.units_records = None
        self.amenities_records = None
        self.dsn = dsn

    def connect_db(self, dsn):
        self.conn = psycopg2.connect(dsn)

    def parse_records(self, listings):
        """
        Flatten listings json to form units table and amenities table contents
        """
        # for the purposes of this challenge, omit all listing not in Evanston
        listings = [listing for listing in listings if listing['city'] == 'Evanston']

        #flatten units and amenities data
        self.amenities_records = self.flatten_amenities(listings)

        self.units_records = []
        # minor data type cleaning
        for unit in self.flatten_units(listings):
            if unit['sqft'] <= 0:
                unit['sqft'] = None # Null preferable to 0 in database for missing sqft
            self.units_records.append(unit)
        return self.units_records, self.amenities_records                

    @staticmethod
    def flatten_units(listings):
        units = []
        for listing in listings:
            zip_code = listing['zip']
            city = listing['city']
            for unit in listing['all_units']:
                unit_dict = {
                    'unit_id': unit['id'],
                    'zip': listing['zip'],
                    'city': listing['city'],
                    'bed': unit['bed'],
                    'sqft': unit['sqft'],
                }
                units.append(unit_dict)
        return units

    @staticmethod
    def flatten_amenities(listings):
        ameneties = []
        for listing in listings:
            for unit in listing['all_units']:
                unit_id = unit['id']
                for amenity in listing['community_amenities']:
                    ameneties.append({
                        'unit_id': unit_id,
                        'amenity': amenity['display_name'],
                        'amenity_type': 'property'
                                    })
                for amenity in listing['community_amenities']:
                    ameneties.append({
                        'unit_id': unit_id,
                        'amenity': amenity['display_name'],
                        'amenity_type': 'unit'
                                    })
        return ameneties
    
    def load_units(self):
        units_insert_query = 'INSERT INTO units (unit_id, zip, city, bed, sqft) VALUES %s'
        units_template = '(%(unit_id)s, %(zip)s, %(city)s, %(bed)s, %(sqft)s)'
        cursor = self.conn.cursor()
        execute_values(cursor, units_insert_query, self.units_records, template=units_template)

    def load_amenities(self):
        amenities_insert_query = 'INSERT INTO amenities (unit_id, amenity, amenity_type) VALUES %s'
        amenities_template = '(%(unit_id)s, %(amenity)s, %(amenity_type)s)'
        cursor = self.conn.cursor()
        execute_values(cursor, amenities_insert_query, self.amenities_records, template=amenities_template)

    def load_all(self):

        self.connect_db(self.dsn)
        self.load_units()
        self.load_amenities()
        self.conn.commit()
        self.conn.close()

# run the scraper as script
if __name__ == '__main__':
    scraper = ApartmentlistScraper()
    ids = scraper.get_rental_ids()
    data = scraper.get_listing_data(ids)
    
    dsn = os.environ['DEMO_DSN']
    loader = ApartmentlistLoader(dsn)
    loader.parse_records(data)
    loader.load_all()