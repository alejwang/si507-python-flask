 # -*- coding: utf-8 -*-
import json
import requests
import csv
# import webbrowser
import sqlite3
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from bs4 import BeautifulSoup
from secret import *


# Main Goal
# - Get names and reviews about recent popular restaurants in San Diego by scraping from a web page
# - Search for information and average ratings from Yelp API
# - Search for each restaurants location from Yelp API, allow users to search other nearby restaurants based on one restaurants location
# - Save the information in database and then show them on a map (Plotly)
# - Let user to sort them based on their price / popularity / rating
# Data Source
# - (4pts) Scraping from updating article from Eater.com https://sandiego.eater.com/maps/best-new-san-diego-restaurants-heatmap (Links to an external site.)Links to an external site.
# - (4pts) Using Yelp API: https://www.yelp.com/developers/documentation/v3/business_reviews
# - (4pts) Using Google Place API to search based on locations: https://developers.google.com/places/web-service/intro
# - All raw data are cached in JSON (Requests) and CSV (Restaurant & Reviews) files
# Presentation Options
# - Check a list of recent popular restaurants
# - Sort them in a particular way: Name, Ratings...
# - Select one to show the detail
# - Select one to add to favorite
# - Select one to search other restaurants nearby
# - Show them on the map
# Data Presentation
# - Interactive command line


CACHE = 'cache.json'
DB = 'my_restaurants.db'
RECOMMENDATIONS_CSV = 'eater_recommendations.csv'
REVIEWS_CSV = 'yelp_reviews.csv'
plotly.tools.set_credentials_file(username='alejwang', api_key=PLOTLY_API_KEY)


try:
    with open(CACHE, 'r') as cache_file:
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}


class Restaurant():
    def __init__(self, name = None, address = None, phone = None, url = None, description = None, row = None):
        if row:
            self.name = row[1]
            self.zipcode = row[5]
            self.state = row[4]
            self.city = row[3]
            self.address = row[2]
            self.phone = row[6]
            self.url = row[7]
            self.description = row[8]
            self.yelp_id = row[12]
            self.rating = row[9]
            self.rate_count = row[10]
            self.price = row[11]
            self.lat = row[13]
            self.lng = row[14]
        else:
            self.name = name.split('. ')[-1]
            self.zipcode = address.split()[-1]
            self.state = address.split()[-2]
            self.city = address.split(', ')[-2]
            self.address = address.split(', ')[0]
            self.phone = phone
            self.url = url
            self.description = description
            self.yelp_id = None
            self.rating = None
            self.rate_count = None
            self.price = None
            self.lat = None
            self.lng = None

    # def get_location(self):
    #     if (self.lat != 'unknown') and (self.lng != 'unknown'):
    #         return None
    #     field_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    #     field_params = {'input': self.name + ' ' + self.type, 'inputtype': 'textquery', 'fields': 'geometry', 'key': google_places_key}
    #     field_json_string = get_page(field_url, field_params)
    #     field_json = json.loads(field_json_string)
    #     try:
    #         self.lat = field_json['candidates'][0]['geometry']['location']['lat']
    #         self.lng = field_json['candidates'][0]['geometry']['location']['lng']
    #     except:
    #         pass

    def searh_on_yelp(self):
        url = 'https://api.yelp.com/v3/businesses/matches'
        params = {'name': self.name, 'address1': self.address, 'city': self.city, 'state': self.state, 'country': 'US', 'match_type': 'lookup'}
        headers = {"Authorization":"Bearer " + YELP_API_KEY}

        try:
            self.yelp_id = get_page(url, params, headers)['businesses'][0]['id']
        except:
            return []

        url = 'https://api.yelp.com/v3/businesses/' + self.yelp_id
        businesses_resp = get_page(url, {}, headers)
        self.rating = businesses_resp['rating']
        if self.rating == "":
            self.rating = None
        self.rate_count = businesses_resp['review_count']
        if self.rate_count == "":
            self.rate_count = None
        try:
            self.price = businesses_resp['price']
            self.price = len(self.price)
        except:
            self.price = None
        # if self.price not in [1,2,3,4,5]:
        #     self.price = 0
        self.lat = businesses_resp['coordinates']['latitude']
        self.lng = businesses_resp['coordinates']['longitude']

        url = 'https://api.yelp.com/v3/businesses/' + self.yelp_id + '/reviews'
        review_resp = get_page(url, {}, headers)
        return review_resp['reviews']

    def print_detail(self):
        st = "\n{}\n{} {} {} {}\n{} {}\n---\n{}\n---\n".format(self.name, self.address, self.city, self.state, self.zipcode, self.phone, self.url, self.description)
        if self.rating not in [None, ""]:
            st += '★' * int(self.rating)
            if (self.rating) - int(self.rating) == 0.5:
                st += '☆'
        if self.rate_count not in [None, ""]:
            st += "    " + str(self.rate_count) + " reviews   "
        if self.price not in [None, ""]:
            st += '$' * int(self.price)
        st += '\n'
        print(st)

    def __str__(self):
        return "{} - {}, {}".format(self.name, self.address, self.phone)

    def csv_writer(self):
        return [self.name, self.address, self.city, self.state, self.zipcode, self.phone, self.url, self.description, self.rating, self.rate_count, self.price, self.yelp_id, self.lat, self.lng]


class Review():
    def __init__(self, res_id, id, rating = None, text = None, url = None, time = None):
        self.res_id = res_id
        self.id = id
        self.rating = rating
        self.text = text
        self.url = url
        self.time = time

    # def __str__(self):
    #     return "{} - {}, {}".format(self.name, self.address, self.phone)

    def csv_writer(self):
        return [self.res_id, self.id, self.rating, self.text, self.url, self.time]


class NearbyPlace():
    def __init__(self, name, lat = None, lng = None):
        self.name = name
        self.lat = lat
        self.lng = lng


def params_unique_combination(baseurl, params_d, private_keys=["apikey"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}={}".format(k, params_d[k]))
    return baseurl + "?" + "&".join(res)


# Making requests, returns the raw data (raw html or json format text)
def get_page(url, params = {}, headers = {}):
    unique_ident = params_unique_combination(url, params)
    if unique_ident in CACHE_DICTION:
        # print("* Getting cached data for url", unique_ident, "...")
        return CACHE_DICTION[unique_ident]
    # print("* Making a request to get new data from url", unique_ident, "...")
    html = requests.get(url, params = params, headers = headers).text
    if '<!DOCTYPE html>' not in html:
        html = json.loads(html)
    CACHE_DICTION[unique_ident] = html
    dumped_json_cache = json.dumps(CACHE_DICTION, indent = 2)
    with open(CACHE, 'w') as cache_file:
        cache_file.write(dumped_json_cache)
    return html


# refresh all saved data, from pulling the page to save into csv files and the database
def refresh_data():
    print('* Preparing the database...')
    recommendations = []
    webpage_list = ['https://sandiego.eater.com/maps/best-new-san-diego-restaurants-heatmap','https://sandiego.eater.com/maps/best-cocktail-bars-san-diego','https://sandiego.eater.com/maps/38-best-restaurants-in-san-diego','https://la.eater.com/maps/best-los-angeles-restaurants-eater-38-essential','https://la.eater.com/maps/best-new-restaurants-los-angeles-heatmap']

    for url in webpage_list:
        html = get_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        lis = soup.find("div", {"class": "c-mapstack__cards c-mapstack__cards--improved"}).find_all("section", {"class": "c-mapstack__card"})

        for li in lis:
            # print(li.text)
            if li['data-slug'] in ['newsletter', 'intro', 'related-links', 'comments']:
                continue
            name = li.find("h1").text
            address = li.find("div", {"class": "c-mapstack__address"}).get_text(", ")
            phone = li.find("div", {"class": "c-mapstack__phone desktop-only"})
            if phone:
                phone = phone.text
            description = li.find("div", {"class": "c-entry-content"}).find("p").text
            url = li.find("a", {"data-analytics-link": "link-icon"})
            if url:
                url = url['href']
            new_rec = Restaurant(name, address, phone, url, description)
            print('* searching for', new_rec, '...')
            recommendations.append(new_rec)

    print('* Getting the reviews from Yelp, this may take a while...')
    reviews = []
    for res in recommendations:
        # print('* Looking for', res.name, 'on Yelp!')
        for review in res.searh_on_yelp():
            reviews.append(Review(res.yelp_id, review['id'], review['rating'], review['text'], review['url'], review['time_created']))

    with open(RECOMMENDATIONS_CSV, 'w', newline='') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Name', 'Address', 'City', 'State', 'Zipcode', 'Phone', 'Url', 'Description', 'Rating', 'Rate Count', 'Price', 'YelpID', 'Lat', 'Lng'])
        for each in recommendations:
            spamwriter.writerow(each.csv_writer())

    with open(REVIEWS_CSV, 'w', newline='') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['ResID', 'ReviewID', 'Rating', 'Text', 'Url', 'Timestamp'])
        for each in reviews:
            spamwriter.writerow(each.csv_writer())

    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
    except:
        print('error while creating the database')
        return None

    cur.execute("DROP TABLE IF EXISTS 'Restaurants';")
    cur.execute("DROP TABLE IF EXISTS 'Reviews';")
    statement = '''
        CREATE TABLE 'Restaurants' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'Name' TEXT NOT NULL,
            'Address' TEXT NOT NULL,
            'City' TEXT NOT NULL,
            'State' TEXT NOT NULL,
            'Zipcode' TEXT NOT NULL,
            'Phone' TEXT,
            'Url' TEXT,
            'Description' TEXT,
            'Rating' REAL,
            'Count' INTEGER,
            'Price' INTEGER,
            'YelpID' TEXT,
            'Lat' REAL,
            'Lng' REAL,
            'Favorite' BOOLEAN
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Reviews' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'ResId' INTEGER,
            'Rating' INTEGER NOT NULL,
            'Text' TEXT,
            'Url' TEXT,
            'Timestamp' TEXT
        );
    '''
    cur.execute(statement)
    print('* wiping up the database...')

    with open(RECOMMENDATIONS_CSV, 'r') as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            if row[0] == 'Name':
                continue
            cur.execute("INSERT INTO 'Restaurants' (Name, Address, City, State, Zipcode, Phone, Url, Description, Rating, Count, Price, YelpID, Lat, Lng, Favorite) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], None))

    with open(REVIEWS_CSV, 'r') as f:
        csvreader = csv.reader(f)
        for row in csvreader:
            if row[0] == 'ResID':
                continue
            try:
                res_id = cur.execute("SELECT Id FROM 'Restaurant' WHERE YelpID = ?;", (row[0],)).fetchone()[0]
            except:
                res_id = None
            cur.execute("INSERT INTO 'Reviews' (ResId, Rating, Text, Url, Timestamp) VALUES (?, ?, ?, ?, ?);", (res_id, row[2], row[3], row[4], row[5]))
    conn.commit()
    conn.close()
    print('* creating the database...')


def pretty_print(rows, command_word):
    if command_word == 'reviews':
        for row in rows:
            print('{}\n{} {}\nFor: {}\n---\n'.format(row[0], row[1], row[2], row[3]))
        return None

    max_len = [ 0 for x in rows[0] ]
    for row in rows:
        for i in range(len(row)):
            if type(row) == type(.0):
                max_len[i] = 5
                continue
            if len(str(row[i])) > max_len[i]:
                max_len[i] = len(str(row[i]))
    for i in range(len(max_len)):
        if max_len[i] > 20:
            max_len[i] = 20
    for row in rows:
        st = ""
        for i in range(len(row)):
            if (command_word == 'detail') and (i == 1):
                continue
            if row[i] == None:
                st += "{text: <{fill}}  ".format(text = 'Unknown', fill = max_len[i])
                continue
            if (type(row[i]) == type(.0)) and (row[i] > 1):
                st += "{text: <{fill}}  ".format(text = "{:.1f}".format(row[i]), fill = max_len[i])
            elif (type(row[i]) == type(.0)) and (row[i] <= 1):
                st += "{text: <{fill}}  ".format(text = "{:.0%}".format(row[i]), fill = max_len[i])
            elif len(str(row[i])) > max_len[i]:
                st += "{text: <{fill}}...  ".format(text = str(row[i][:17]), fill = max_len[i] - 3)
            else:
                st += "{text: <{fill}}  ".format(text = str(row[i]), fill = max_len[i])
        print(st)


def format_data(raw_data, command_word):
    raw_data = [list(row) for row in raw_data]
    for row in raw_data:
        if row[1] in [1, 2, 3, 4, 5]:
            row[1] = '★' * int(row[1])
        elif row[1] == 0:
            row[1] = '?'
        else:
            row[1] = '★' * int(row[1]) + '☆'
        if command_word == 'restaurants':
            row[2] = str(row[2]) + ' reviews'
            if row[3] in [1, 2, 3, 4, 5]:
                row[3] = '$' * int(row[3])
            elif row[3] in [0, None, ""]:
                row[3] = '?'
            else:
                row[3] = '$' * int(row[3]) + '~' + '$' * int(row[3] + 1)
        elif command_word == 'cities':
            row[2] = str(row[2]) + ' restaurants'
            if row[3] in [1, 2, 3, 4, 5]:
                row[3] = '$' * int(row[3])
            elif row[3] == 0:
                row[3] = '?'
            else:
                row[3] = '$' * int(row[3]) + '~' + '$' * int(row[3] + 1)
    return raw_data


def load_help_text():
    with open('help.txt') as f:
        return f.read()


def process_command(command):
    allowed_search_key = {
        'restaurants': ['city', 'zipcode'],
        'reviews': ['city', 'zipcode'],
        'cities': []
    }
    search_key = 0
    search_value = 0
    allowed_filter = {
        'restaurants': ['order_by_phone', 'order_online', 'favorite'],
        'reviews': [],
        'cities': []
    }
    filter = 1
    allowed_sorting = {
        'restaurants': ['ratings', 'popularity', 'price', 'name'],
        'reviews': ['timestamp', 'ratings', 'length'],
        'cities': ['avg_rating', 'avg_price', 'count']
    }
    sorting = 'default'
    limit = 10
    city_name_overwhelm = False
    command_word = command.split()[0]
    for argument in command.split()[1:]:
        # print(argument)
        if city_name_overwhelm:
            city_name_overwhelm = False
            continue
        if '=' in argument:
            key = argument[: argument.find('=')]
            if key in ['top', 'bottom']:
                try:
                    limit = int(argument[argument.find('=')+1 :])
                    if key == 'bottom':
                        limit = 0-limit
                except:
                    print("Command not recognized:", command)
                    print("Please input a number for limit top")
                    return None
            elif key in allowed_search_key[command_word]:
                search_key = key
                search_value = argument[argument.find('=') + 1 :]
                if search_value in ['West', 'Sherman', 'Santa', 'San', 'Monterey', 'Los', 'La', 'El', 'Del', 'Culver', 'Beverly']:
                    city_name_overwhelm = True
                    search_value += ' ' + command.split()[command.split().index(argument) + 1]
            else:
                print("Command not recognized:", command)
                print("Please input a valid parameter other than", key)
                return None
        elif (argument in allowed_filter[command_word]):
            filter = argument
        elif (argument in allowed_sorting[command_word]):
            sorting = argument
        else:
            print("Command not recognized:", command)
            print("Please input a valid parameter other than", argument)
            return None

    link_search_key = {
        'city': 'R.City',
        'zipcode': 'R.Zipcode',
        0: 0
    }

    link_filter = {
        'order_by_phone': 'R.Phone',
        'order_online': 'R.Url',
        'favorite': 'R.Favorite',
        1: 1
    }

    link_agg = {
        'avg_rating': 'Avg(R.Rating)',
        'avg_price': 'Avg(R.Price)',
        'count': 'Count(*)'
    }

    link_sorting = {
        'ratings': 'R.Rating',
        'popularity': 'R.Count',
        'price': 'R.Price',
        'name': 'R.Name',
        'timestamp': 'V.Timestamp',
        'rating': 'V.Rating',
        'length': 'LENGTH(V.Text)'
    }

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if command_word == 'restaurants':
        if sorting == 'default':
            sorting = 'ratings'
        statement = """SELECT DISTINCT R.Name, R.Rating, R.Count, R.Price, R.Address, R.City
                       FROM Restaurants AS R
                       WHERE {0} = ? AND {1} IS NOT NULL AND {2} <> ""
                       ORDER BY {2} {3}
                       LIMIT ?""".format(link_search_key[search_key], link_filter[filter], link_sorting[sorting], 'DESC' * int (limit > 0))
        # print(statement, search_value, abs(limit) )
        cur.execute(statement, (search_value, abs(limit)))

    elif command_word == 'reviews':
        if sorting == 'default':
            sorting = 'timestamp'
        statement = """SELECT DISTINCT V.Text, V.Rating, V.Timestamp, R.Name
                       FROM Reviews AS V
                       LEFT JOIN Restaurants AS R ON V.ResId = R.Id
                       WHERE {} = ?
                       ORDER BY {} {}
                       LIMIT ?""".format(link_search_key[search_key], link_sorting[sorting], 'DESC' * int (limit > 0))
        # print(statement, search_value, abs(limit) )
        cur.execute(statement, (search_value, abs(limit)))

    elif command_word == 'cities':
        if sorting == 'default':
            sorting = 'count'
        statement = """SELECT DISTINCT R.City, Avg(R.Rating) AS AvgRating, Count(*) AS CountAll, Avg(R.Price) AS AvgPrice
                       FROM Restaurants AS R
                       GROUP BY R.City
                       HAVING count(R.YelpID) > 1
                       ORDER BY {} {}
                       LIMIT ?""".format(link_agg[sorting], 'DESC' * int (limit > 0))
        # print(statement, search_value, abs(limit) )
        cur.execute(statement, (abs(limit),))
    raw_data = [row for row in cur]
    conn.close()
    return raw_data


def search_keyword_in_db(search_value = None, id = None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if id == 'all':
        statement = """SELECT * FROM Restaurants AS R"""
        cur.execute(statement)
    elif id:
        statement = """SELECT *
                       FROM Restaurants AS R
                       WHERE R.Id = ?
                       ORDER BY R.Name"""
        cur.execute(statement, (id, ))
    else:
        statement = """SELECT DISTINCT R.Id, R.Name, R.Address, R.City
                       FROM Restaurants AS R
                       WHERE R.Name LIKE ?
                       ORDER BY R.Name"""
        # print(statement)
        cur.execute(statement, (search_value+'%', ))
    raw_data = [row for row in cur]
    conn.close()
    return raw_data


def set_favorite(id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    statement = """SELECT Favorite FROM Restaurants WHERE Id = ?"""
    current = cur.execute(statement, (id, )).fetchone()[0]
    statement = """UPDATE Restaurants SET Favorite = ? WHERE Id = ?"""
    if current:
        cur.execute(statement, (False, id, ))
    else:
        cur.execute(statement, (True, id, ))
    conn.commit()
    conn.close()
    print('Added to favorited')


def search_nearby(res):
    if (res.lat == None) or (res.lng == None):
        print('* No GPS data for ' + res.name)
        return []

    nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    nearby_params = {'location': str(res.lat)+','+str(res.lng) ,'radius': '10000', 'key': GOOGLE_PLACE_API_KEY, 'type': 'restaurant'}
    nearby_json = get_page(nearby_url, nearby_params)
    # print(nearby_json)
    places = []
    for place in nearby_json['results']:
        if 'name' in place:
            places.append(NearbyPlace(place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng']))
    # print('places', places)
    return places


def plot_places(sites, title):
    # for site in sites:
    #     print(site)
    lat_vals = []
    lon_vals = []
    text_vals = []
    for site in sites:
        if (site.lng not in [None, ""]) and (site.lat not in [None, ""]):
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
        # print('str_v', str_v)
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
    lat_axis = [min_lat - 0.2, max_lat + 0.2]
    lon_axis = [min_lon - 0.2, max_lon + 0.2]
    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    layout = dict(
            title = title,
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
    py.plot(fig, validate = False, filename = 'rec-res')


if __name__ == "__main__":
    help_text = load_help_text()
    current_id = None
    while True:
        command = input('\nEnter a command: ')
        if command == 'exit':
            print('Bye')
            break
        if command == 'help':
            print(help_text)
            continue
        if command == 'update':
            refresh_data()
            print('* OK')
            continue
        if command == "":
            print("Commands available: restaurants, reviews, cities, map, detail (favorite, nearby)")
            continue

        command_word = command.split()[0]
        if command_word not in ['restaurants', 'reviews', 'cities', 'detail', 'favorite', 'nearby', 'map']:
            print("Command not recognized:", command)
            print("Commands available: restaurants, reviews, cities, map, detail (favorite, nearby)")
            continue

        if command_word == 'map':
            raw_data = search_keyword_in_db(id="all")
            # print('raw_data', raw_data)
            all_res = []
            for row in raw_data:
                all_res.append(Restaurant(row = row))
            # print('all_res', all_res)
            plot_places(all_res, 'Recommended Restaurant in Mid-South CA')
            continue

        if command_word == 'detail':
            search_keyword = command[7:]
            search_result = search_keyword_in_db(search_keyword)
            if search_result in [None, []]:
                print("Unfortunately the restaurant with the name", search_keyword, 'not found in the database')
            elif len(search_result) > 1:
                print("Found several restaurants with the name", search_keyword)
                for i in range(len(search_result)):
                    search_result[i] = [str(i+1)+'.'] + list(search_result[i])
                pretty_print(search_result, command_word)
                while True:
                    user_choice = input('Please choose one by the number or input cancel: ')
                    if (user_choice == ""):
                        continue
                    if user_choice == 'cancel':
                        current_id = None
                        break
                    try:
                        if (int(user_choice)-1) in range(len(search_result)):
                            current_id = search_result[int(user_choice)-1][0]
                            break
                    except:
                        current_id = None
                        print("Number not recognized:", user_choice)
            elif len(search_result) == 1:
                current_id = search_result[0][0]
            if current_id:
                current_res = search_keyword_in_db(id = current_id)
                Restaurant(row = current_res[0]).print_detail()
                print('You can now use favorite and nearby command')
            continue

        if command_word in ['favorite', 'nearby']:
            if (current_id == None):
                print("Please use detail command first to call", command_word)
                continue

        if command_word == 'favorite':
            set_favorite(current_id)
            continue

        if command_word == 'nearby':
            search_result = search_keyword_in_db(id = current_id)
            current_res = Restaurant(row = current_res[0])
            print('* searching for nearby restaurants...')
            nearby_res = search_nearby(current_res)
            plot_places(nearby_res, 'Restaurant near ' + current_res.name)
            continue

        raw_data = process_command(command)
        # print(raw_data)
        if raw_data == []:
            print('No search results.')
        elif raw_data != None:
            formatted_data = format_data(raw_data, command_word)
            pretty_print(formatted_data, command_word)
