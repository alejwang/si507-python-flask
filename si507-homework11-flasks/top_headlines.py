from flask import Flask, render_template
from secrets_example import api_key
import requests
import json
import datetime

try:
    cache_file = open('nyt_cache.json', 'r')
    cache_contents = cache_file.read()
    cache_diction = json.loads(cache_contents)
    cache_file.close()
except:
    cache_diction = {}

def params_unique_combination(baseurl, params_d, private_keys=["api-key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}={}".format(k, params_d[k]))
    return baseurl + '?' + "&".join(res)

def get_from_nyt_caching(category):
    baseurl = "https://api.nytimes.com/svc/topstories/v2/{}.json".format(category)
    params_diction = {}
    params_diction["api-key"] = api_key
    unique_ident = params_unique_combination(baseurl,params_diction)

    if unique_ident in cache_diction:
        print ("getting data from cache file...")
        return cache_diction[unique_ident]
    else:
        print ("making new API call...")
        resp = requests.get(baseurl, params_diction)
        cache_diction[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(cache_diction, indent=4)
        fw = open('nyt_cache.json',"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return cache_diction[unique_ident]

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Welcome!</h1>'


@app.route('/user/<name>')
@app.route('/user/<name>/<cat>')
def user_home_page(name, cat = 'technology'):
    now = datetime.datetime.now()
    print(now.minute)
    if (now.hour < 12) or (now.hour == 12 and now.minute == 0):
        greeting = 'Good morning'
    elif (now.hour < 16) or (now.hour == 16 and now.minute == 0):
        greeting = 'Good afternoon'
    elif (now.hour < 20) or (now.hour == 20 and now.minute == 0):
        greeting = 'Good evening'
    else:
        greeting = 'Good night'
    raw_data = get_from_nyt_caching(cat)
    headlines = [x['title'] + ' (' + x['url'] + ')' for x in raw_data['results'][:5]]
    return render_template('user.html', greeting=greeting, name=name, cat=cat, headlines=headlines)


if __name__ == '__main__':
    print('starting Flask app', app.name)
    app.run(debug=True)
