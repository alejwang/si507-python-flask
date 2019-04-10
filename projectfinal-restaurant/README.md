## Data Sources:

Eater.com - 100+ recommended restaurants, get from different pages
Yelp Fusion API
Google Place API

## Files:

My code is structured into one main python program and one unittest program.

### secrets.py:

- In order to use Yelp API and Plotly, you will need to download the secrets.py from my Canvas submission. The secret file contains the necessary API keys and you don't need to change anything.
- Use the requirements.txt to install all the dependencies.

### projfinal.py:

Description: projfinal.py first scrapes the EATER.com and gathers information about the best restaurants in mid-south California. Then it gathers recent reviews, ratings, price and popularity from Yelp API.

#### PROCESSING FUNCTIONS:

_refresh_data()_: This function scrapes 5 different pages of EATER.com. From each pages, it gathers Title, description, address, phone and website. After  passing this information into the Restaurant class, each instance will call Yelp API to gather more information including the reviews. All the information are written in CSV files and also the database. Note: if you want to update the most recent updates from EATER.com and YELP, you need to clean up the cache file.

_pretty_print()_, _format_data()_: These function are formatting the raw data into readable formats in columns. For example, transcode 'most expensive' to '$$$$$'.

_process_command()_, _search_keyword_in_db()_: These function are getting data from the database by a command input by users or for a task-oriented goal. It will also throw readable errors when the commands are not legid.

_set_favorite()_: This function is for updating the restaurant rows in the database when user chooses to add one into favorite. Note: updating the database will lost the favorite records.

_plot_places()_, _search_nearby()_: These function use the Google Place API and Plotly to search for either the recommended restaurants or the other restaurants near one recommended restaurant to show the results in the map.

#### CLASSES:

_Restaurant_: Inputs are either the raw data from the webpage or the tuple from the sql statement. The searh_on_yelp() method will pair on the YELP first and gather more data to the instances.
_Review_: Inputs are the API response json file from YELP. A basic structure to store the reviews.
_NearbyPlace_: A mini version of restaurant. Only store some basic attributes.

### projfinal_test.py:

Description: A unittests file to test the data scraping, database structure and the interface. Note: If you remove the cache file, you may not pass all the tests anymore.

#### CLASSES:

_class TestScraping(unittest.TestCase)_: Tests if the scraping is working

_class TestDatabase(unittest.TestCase)_: Tests if the database construction is working

_class TestInterface(unittest.TestCase)_: Tests if some basic queries are working
presentation.


## User Guide:

Commands available:

restaurants
	Description: Lists all the recommended restaurants in Mid and South California

	Options:
		* city=<name> | zipcode=<code>  [default: all]
		Description: Specifies a city or zipcode within which to limit the results.

		* order_by_phone | order_online | favorite [default: none]
		Description: Specifies whether the restaurants has phone or website to order
		food remotely, type favorite to get your favorite list.

		* ratings | popularity | price | name [default: ratings]
		Description: Specifies whether to sort by ratings, popularity, price or
		alphabetically.

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

reviews
	Description: Lists recently Yelp reviews for the recommended restaurants

	Options:
		* city=<name> | zipcode=<code>  [default: all]
		Description: Specifies a city or zipcode within which to limit the results.

		* timestamp | rating | length [default: timestamp]
		Description: Specifies whether to sort by timestamp, rating value, or
		the comment text length.

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

cities
	Description: Lists cities according to specified parameters.
	Only cities with more than 1 recommended restaurant with yelp reviews will be
	listed in results.

	Options:
		* avg_rating | avg_price | count [default: avg_ratings]
		Description: Specifies whether to sort by average rating, average price
		or the count.

		* top=<limit>|bottom=<limit> [default: top=10]
		Description: Specifies whether to list the top <limit> matches or the
		bottom <limit> matches.

detail <name|prefix>
	Description: Check the restaurant detail. You need to specify the restaurant
	name but you don't need to type the full name.

	After you run detail:
		You can use two need commands:
		- favorite: Add the restaurant to your favorite list, call 'restaurants
		favorite' to see the favorite list
		- nearby: Plot the nearby restaurants on the map by plot.ly.

map
	Description: Plot all the recommendations on the map by plot.ly.

update
	Description: Wipe the database and pull over the data from EATER.com and Yelp
	again. It may take several minutes without cache.
	Note: Run update command will reset all the data. Your favorites will be lost.
