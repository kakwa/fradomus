# -*- coding: utf-8 -*-

import datetime

class BaseAds():

    def __init__(self):
        self.website = 'None'

    def get_ad_details(self, add_id):
        ret = {
            'source': self.website,
            'id': None,
            'price': None,
            'price_unit': None,
            'room': None,
            'surface': None,
            'surface_unit': None,
            'city': None,
            'postal_code': None,
            'date': datetime.datetime.fromtimestamp(0),
            'longitude': None, 
            'latitude':  None,
            'proximity': [],
            'description': None,
            'link': None,
            'raw': None,
        }
        return ret

    def get_location(self, cp):
        return None

    # Return the number of ads matching a search
    def count(self, cp, min_surf, max_price, ad_type, nb_room_min):
        """Return the number of ads matching a search
        arg 1: the postal code
        arg 2: the minimal surface
        arg 3: the maximum rent/price
        arg 4: type of the add ('rent' -> location, 'sell' -> sell)
        arg 5: the owner_id of the search (the user making the search)
        arg 6: nb_room_min, minimum number of rooms
        """
        return 0

    def search(self, cp, min_surf, max_price, ad_type, nb_room_min):
        """Recover the ads matching a given search
        arg 1: the postal code
        arg 2: the minimal surface
        arg 3: the maximum rent/price
        arg 4: type of the add ('rent' -> location, 'sell' -> sell)
        arg 5: the owner_id of the search (the user making the search)
        arg 6: nb_room_min, minimum number of rooms
        """
        ret = {
            'source': self.website,
            'id': [],
            'raw': None,
        }
        return ret
