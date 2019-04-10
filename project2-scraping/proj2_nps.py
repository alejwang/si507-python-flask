## proj_nps.py
## Skeleton for Project 2, Fall 2018
## ~~~ modify this file, but don't rename it ~~~
from secrets import google_places_key
import requests
import json
from bs4 import BeautifulSoup
import plotly.plotly as py

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NationalSite():
    def __init__(self, type, name = None, desc = None, url = None, address_street = None, address_city = None, address_state = None, address_zip = None, lat = "unknown", lng = "unknown"):
        self.type = type
        self.name = name
        self.description = desc
        self.url = url
        self.address_street = address_street
        if (address_street != None):
            self.address_street = address_street.strip()
            while '\n' in self.address_street:
                self.address_street = self.address_street.replace('\n', ' ')
        self.address_city = address_city
        if (address_city != None):
            self.address_city = address_city.strip()
        self.address_state = address_state
        if (address_state != None):
            self.address_state = address_state.strip()
        self.address_zip = address_zip
        if (address_zip != None):
            self.address_zip = address_zip.strip()
        self.lat = lat
        self.lng = lng

    def get_location(self):
        if (self.lat != 'unknown') and (self.lng != 'unknown'):
            return None
        field_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        field_params = {'input': self.name + ' ' + self.type, 'inputtype': 'textquery', 'fields': 'geometry', 'key': google_places_key}
        field_json_string = get_page(field_url, field_params)
        field_json = json.loads(field_json_string)
        try:
            self.lat = field_json['candidates'][0]['geometry']['location']['lat']
            self.lng = field_json['candidates'][0]['geometry']['location']['lng']
        except:
            pass

    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state, self.address_zip)
## you can, and should add to and modify this class any way you see fit
## you can add attributes and modify the __init__ parameters,
##   as long as tests still pass
##
## the starter code is here just to make the tests run (and fail)
class NearbyPlace():
    def __init__(self, name, lat = 'unknown', lng = 'unknown'):
        self.name = name
        self.lat = lat
        self.lng = lng

## Must return the list of NationalSites for the specified state
## param: the 2-letter state abbreviation, lowercase
##        (OK to make it work for uppercase too)
## returns: all of the NationalSites
##        (e.g., National Parks, National Heritage Sites, etc.) that are listed
##        for the state at nps.gov

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}={}".format(k, params[k]))
    return baseurl + '?' + "&".join(res)

def get_page(url, params = {}):
    unique_ident = params_unique_combination(url, params)
    if unique_ident in CACHE_DICTION:
        # print("* Getting cached data for url", unique_ident, "...")
        return CACHE_DICTION[unique_ident]
    # print("* Making a request to get new data from url", unique_ident, "...")
    html = requests.get(url, params = params).text
    CACHE_DICTION[unique_ident] = html
    dumped_json_cache = json.dumps(CACHE_DICTION, indent = 2)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close()
    return html

def get_sites_for_state(state_abbr):
    url = "https://www.nps.gov/state/{}".format(state_abbr.lower())
    html = get_page(url)
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find("ul", {"id": "list_parks"}).find_all('li', {"class": "clearfix"})
    # print(lis)

    sites = []
    for li in lis:
        # print(li.text)
        left = li.find("div", {"class": "list_left"})
        type = left.find("h2").text
        name = left.find("a").text
        description = left.find("p").text
        link = "https://www.nps.gov" + left.find("a")['href']
        # print(type, name, description, link)
        detail_html = get_page(link)
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        # print(detail_soup)
        address = detail_soup.find('p', {'class': 'adr'})
        # print(address.text + '\n\n')
        try:
            address_street = address.find('span', {'itemprop': 'streetAddress'}).text
        except:
            address_street = None
        address_city = address.find('span', {'itemprop': 'addressLocality'}).text
        address_state = address.find('span', {'itemprop': 'addressRegion'}).text
        address_zip = address.find('span', {'itemprop': 'postalCode'}).text
        sites.append(NationalSite(type, name, description, link, address_street, address_city, address_state, address_zip))

    return sites

## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##          if the site is not found by a Google Places search, this should
##          return an empty list
def get_nearby_places_for_site(national_site):
    national_site.get_location()
    if (national_site.lat == 'unknown') or (national_site.lng == 'unknown'):
        print('* No GPS data for ' + site_object.name)
        return []

    nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    nearby_params = {'location': str(national_site.lat)+','+str(national_site.lng) ,'radius': '10000', 'key': google_places_key}
    nearby_json_string = get_page(nearby_url, nearby_params)
    nearby_json = json.loads(nearby_json_string)

    places = []
    for place in nearby_json['results']:
        if 'name' in place:
            places.append(NearbyPlace(place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng']))
            # print(place['name'])
    return places

## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_sites_for_state(state_abbr):
    sites = get_sites_for_state(state_abbr)
    lat_vals = []
    lon_vals = []
    text_vals = []
    for site in sites:
        site.get_location()
        if (site.lng != 'unknown') and (site.lat != 'unknown'):
            lat_vals.append(site.lat)
            lon_vals.append(site.lng)
            text_vals.append(site.name)
    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 8,
                symbol = 'star',
            ))]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000
    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v
    lat_axis = [min_lat - 0.8, max_lat + 0.8]
    lon_axis = [min_lon - 0.8, max_lon + 0.8]
    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    layout = dict(
            title = 'National Sites in ' + state_abbr.upper(),
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
                countrywidth = 5,
                subunitwidth = 3
            ),
        )

    fig = dict(data = data, layout = layout )
    py.plot(fig, validate = False, filename = 'nationalsites1')


## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):
    places = get_nearby_places_for_site(site_object)
    if (site_object.lng == 'unknown') or (site_object.lat == 'unknown'):
        print('* No GPS data for ' + site_object.name)
        return None

    lat_vals = []
    lon_vals = []
    text_vals = []
    color_vals = []
    symbol_vals = []
    for place in places:
        if (place.lng != 'unknown') and (place.lat != 'unknown') and (place.name.lower() != site_object.name.lower()) and (place.name.lower() != site_object.name.lower() + ' national park'):
            lat_vals.append(place.lat)
            lon_vals.append(place.lng)
            text_vals.append(place.name)
            color_vals.append('blue')
            symbol_vals.append('circle')
    lat_vals.append(site_object.lat)
    lon_vals.append(site_object.lng)
    text_vals.append(site_object.name)
    color_vals.append('red')
    symbol_vals.append('star')
    data = [ dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = lon_vals,
            lat = lat_vals,
            text = text_vals,
            mode = 'markers',
            marker = dict(
                size = 9,
                color = color_vals,
                symbol = symbol_vals
            ))]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000
    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v
    lat_axis = [min_lat - 0.05, max_lat + 0.05]
    lon_axis = [min_lon - 0.05, max_lon + 0.05]
    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    layout = dict(
            title = 'Nearby Places Near ' + site_object.name,
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center= {'lat': center_lat, 'lon': center_lon },
                countrywidth = 5,
                subunitwidth = 3
            ),
        )

    fig = dict(data = data, layout = layout )
    py.plot(fig, validate = False, filename = 'nationalsites2')

if __name__ == "__main__":
    command = "\nEnter command('or 'help' for options):"
    sites = []
    recent_command = ''
    while True:
        inp = input(command)
        inp = inp.strip()
        if inp == 'help':
            print("""
                list <stateabbr>
                    available anytime
                    lists all National Sites in a state
                    valid inputs: a two-letter state abbreviation
                nearby <result_number>
                    available only if there is an active result set lists all Places nearby a given result
                    valid inputs: an integer 1-len(result_set_size)
                map
                    available only if there is an active result set
                    displays the current results on a map
                exit
                    exits the program
                help
                    lists available commands (these instructions)""")
        elif inp[:5] == 'list ':
            state_abbr = inp[5:]
            try:
                sites = get_sites_for_state(state_abbr)
                for i in range(len(sites)):
                    print(i+1, sites[i])
                recent_command = 'list'
            except:
                print('Please input a valid state abbr')
        elif (inp[:7] == 'nearby ') and (inp[7:].isdigit()):
            if sites == []:
                print('Please use list command first')
            else:
                try:
                    no = int(inp[7:])
                    national_site = sites[no - 1]
                    print('Places near', national_site.name, '\n')
                    places = get_nearby_places_for_site(national_site)
                    for i in range(len(places)):
                        print(i+1, places[i].name)
                    recent_command = 'nearby'
                except:
                    print('Please input a valid nearby number')
        elif inp == 'map':
            if recent_command == 'list':
                plot_sites_for_state(state_abbr)
            elif recent_command == 'nearby':
                plot_nearby_for_site(national_site)
            else:
                print('Please use list or nearby command first')
        elif inp == 'exit':
            print('Bye')
            break
        else:
            print('Please use a valid command')
