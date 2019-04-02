import requests

# Generate the headers for the REST calls
class PAPAds():

    def __init__(self):
        self.website = 'PAP'

    @staticmethod
    def _map_type(ad_type):
        if ad_type == 'sell':
            return 'vente'
        elif ad_type == 'rent':
            return 'location'

    @property
    def headers(self):
        headers = {
            'X-Device-Gsf': 'unable_to_get_device_unique_id',
            'X-App-Version': '3.8.3',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.1; Anbox Build/N6F26Q)',
        }
        return headers
    
    def get_ad_details(self, add_id):
        """Recover the details of an ad"""
        ret = None
        r = requests.get("https://ws.pap.fr/immobilier/annonces/%s" % (add_id), headers=self.headers)
        try:
            ret = r.json()
        except:
            print(r.status_code)
            print(r.text)
        return ret
    
    def get_location(self, cp):
        """get the seloger location code from the postal code"""
        LOCATION_URL = "https://ws.pap.fr/gis/places?recherche[cible]=pap-recherche-ac&recherche[q]=%s&size=10&page=1" % cp
        
        r = requests.get(LOCATION_URL, headers=self.headers)
        return r.json()['_embedded']['place'][0]['id']

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
        r = self.search(cp, min_surf, max_price, ad_type, nb_room_min)
        return r['nb_items']

    def search(self, cp, min_surf, max_price, ad_type, nb_room_min):
        """Recover the ads matching a given search
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
            _cp.append(self.get_location(cp))
    
        SEARCH_PAYLOAD = {
                'recherche[produit]': self._map_type(ad_type),
                'recherche[prix][max]': max_price,
                'recherche[nb_pieces][min]': nb_room_min,
                'recherche[geo][ids][]': _cp,
                'size': 1000,
                'page': 1
        }
    
        SEARCH_URL = "https://ws.pap.fr/immobilier/annonces"

        # TODO handle pagination (if necessary, until now, result set is quite small)
        r = requests.get(SEARCH_URL, params=SEARCH_PAYLOAD, headers=self.headers)
        return r.json()


#from pprint import pprint
#
#pap = PAPAds()
#
#r = pap.get_location('75014')
#pprint(r)
#
#r = pap.count(
#    cp=['75014', '75010', '75013', '75018'],
#    min_surf=25,
#    max_price=320000,
#    ad_type='sell',
#    nb_room_min=2
#)
#pprint(r)

#r = pap.search(
#    cp=['75014', '75010', '75013', '75018'],
#    min_surf=25,
#    max_price=320000,
#    ad_type='sell',
#    nb_room_min=2
#)
#pprint(r)
#
#for ad in r['_embedded']['annonce']:
#    pprint(pap.get_ad_details(ad['id']))
