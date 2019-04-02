import requests
import datetime
import json
import time
import uuid
import jwt

# Some constants used to build the base local JWT token
AUD_CONST = "SeLoger-Mobile-6.0"
APP_CONST = "63ee714d-a62a-4a27-9fbe-40b7a2c318e4"
ISS_CONST = "SeLoger-mobile"
JWT_CONST = "b845ec9ab0834b5fb4f3a876295542887f559c7920224906bf4bc715dd9e56bc"

class SeLogerAds():

    def __init__(self):
        self._base_headers = {
            'User-Agent': 'okhttp/3.11.0',
            'AppGuid': APP_CONST,
            'AppToken': None, 
            'Accept': 'Accept',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        self._token_ts = 0
        self.website = 'SeLoger'

    @staticmethod
    def _map_type(ad_type):
        if ad_type == 'sell':
            return 2
        elif ad_type == 'rent':
            return 1

    # Generate the headers for the REST calls
    @property
    def headers(self):
        now = int(time.time() - 1)
        # if token is too old, renew it
        if now - self._token_ts > 1800:
            # update the auth token
            self._update_authed_token()
            # update the timestamp of the last authentication
            self._token_ts = now
            return self._base_headers
        else:
            return self._base_headers
    
    # Generate the local token
    def _gen_local_token(self):
        encoded_jwt = jwt.encode(
                {
                    'iss': ISS_CONST,
                    'app': APP_CONST,
                    'iat': int(time.time() - 1),
                    'jit': str(uuid.uuid1()),
                    'aud': AUD_CONST,
                },
                JWT_CONST,
                algorithm='HS256',
                headers={"typ":"JWT","alg":"HS256"},)
        return encoded_jwt
    
    # Get the authenticated token.
    # For that, you generate the local token, do a call on "/security/authenticate" which give you back
    # the JWT token used for the rest of the REST calls.
    def _update_authed_token(self):
        local_token = self._gen_local_token()
        self._base_headers['AppToken'] = local_token
        auth_url = "https://api-seloger.svc.groupe-seloger.com/api/v1/security/authenticate"
        r = requests.get(auth_url, headers=self._base_headers)
        authed_token = r.text[1:-1]
        self._base_headers['AppToken'] = authed_token
    
    def get_ad_details(self, add_id):
        """Recover the details of an ad"""
        ret = None
        r = requests.get("https://api-seloger.svc.groupe-seloger.com/api/v1/listings/%s" % (add_id), headers=self.headers)
        try:
            data = r.json()
        except:
            print(r.status_code)
            print(r.text)

        ret = {
            'source': self.website,
            'id': add_id,
            'price': data['price'],
            'price_unit': data['priceUnit'],
            'room': data['rooms'],
            'surface': data['livingArea'],
            'surface_unit': data['livingAreaUnit'],
            'city': data['city'],
            'postal_code': data['zipCode'],
            'date': datetime.datetime.strptime(data['lastModified'], '%Y-%m-%dT%H:%M:%S'),
            'longitude': data['coordinates']['longitude'],
            'latitude': data['coordinates']['latitude'],
            'proximity': [],
            'description': data['description'],
            'link': data['permalink'],
            'raw': data,
        }
        for t in data['transportations'].get('available', []):
            ret['proximity'].append(t['name'])
        return ret
    
    def get_location(self, cp):
        """get the seloger location code from the postal code"""
        LOCATION_URL = "https://api-seloger.svc.groupe-seloger.com/api/v1/locations/search"
        
        LOCATION_PAYLOAD = {
            "latitude": 0.0,
            "limit": 50,
            "locationTypes": 30,
            "longitude": 0.0,
            "radius": 0,
            "searchTerm": cp,
            "type": 0
        }
        
        r = requests.post(LOCATION_URL, data=json.dumps(LOCATION_PAYLOAD), headers=self.headers)
        return r.json()[0]['id']
    
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
        _cp = []
        if type(cp) is list:
            for c in cp:
                _cp.append(self.get_location(c))
        else:
            _cp.append(get_location(cp))
    
        SEARCH_PAYLOAD = [
            {
                "includeNewConstructions": True,
                "inseeCodes": _cp,
                "maximumPrice": max_price,
                "minimumLivingArea": min_surf,
                "realtyTypes": 3,
                "rooms": range(nb_room_min, 5),
                "transactionType": self._map_type(ad_type)
            },
        ]
    
        COUNT_URL = "https://api-seloger.svc.groupe-seloger.com/api/v1/listings/count"
    
        r = requests.post(COUNT_URL, data=json.dumps(SEARCH_PAYLOAD), headers=self.headers)
        return r.json()[0]
    
    def search(self, cp, min_surf, max_price, ad_type, nb_room_min):
        """Recover the ads matching a given search
        arg 1: the postal code
        arg 2: the minimal surface
        arg 3: the maximum rent/price
        arg 4: type of the add (1 -> location, 2 -> sell) 
        arg 5: the owner_id of the search (the user making the search)
        arg 6: nb_room_min, minimum number of rooms
        """
        _cp = []
        if type(cp) is list:
            for c in cp:
                _cp.append(self.get_location(c))
        else:
            _cp.append(self.get_location(cp))
    
        SEARCH_PAYLOAD = {
            "pageIndex": 1,
            "pageSize": 50000,
            "query": {
                "bedrooms": [],
                "includeNewConstructions": True,
                "inseeCodes": _cp,
                "maximumPrice": max_price,
                "minimumLivingArea": min_surf,
                "realtyTypes": 3,
                "rooms": range(nb_room_min, 5),
                "sortBy": 0,
                "transactionType": self._map_type(ad_type)
            }
        }
    
        SEARCH_URL = "https://api-seloger.svc.groupe-seloger.com/api/v1/listings/search"
    
        r = requests.post(SEARCH_URL, data=json.dumps(SEARCH_PAYLOAD), headers=self.headers)
        data = r.json()
        ret = {
            'id': [],
            'raw': data,
            'source': self.website
        }
        for i in data['items']:
            ret['id'].append(i['id'])
        return ret
    
#from pprint import pprint
#
#seloger = SeLogerAds()
#
#r = seloger.get_location('75014')
#pprint(r)
#
#r = seloger.count(
#    cp=['75014', '75010', '75013', '75018'],
#    min_surf=25,
#    max_price=320000,
#    ad_type='sell',
#    nb_room_min=2
#)
#pprint(r)
#
#r = seloger.search(
#    cp=['75014', '75010', '75013', '75018'],
#    min_surf=25,
#    max_price=320000,
#    ad_type='sell',
#    nb_room_min=2
#)
#pprint(r)
#
#for id in r['id']:
#    pprint(seloger.get_ad_details(id))

