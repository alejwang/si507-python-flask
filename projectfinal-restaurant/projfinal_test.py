import unittest
from projfinal import *

class TestScraping(unittest.TestCase):

    def test_res_csv(self):
        with open('eater_recommendations.csv') as f:
            self.assertEqual(len(f.readlines()), 131)

    def test_res_csv(self):
        with open('yelp_reviews.csv') as f:
            self.assertTrue('https://www.yelp.com/biz/bonchon-convoy-san-diego' in f.read())


    def test_cache_json(self):
        with open('cache.json') as f:
            cache = f.read()
            self.assertTrue('api.yelp.com/v3/businesses/matches' in cache)
            self.assertTrue('maps.googleapis.com/maps/api/place/nearbysearch/json' in cache)


class TestDatabase(unittest.TestCase):

    def test_res_table(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Restaurants'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Majordomo',), result_list)
        self.assertEqual(len(result_list), 130)

        sql = '''
            SELECT Name, Rating, Count
            FROM Restaurants
            WHERE City = 'San Diego'
            ORDER BY Count ASC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 58)
        self.assertEqual(result_list[0][2], 2)
        conn.close()

    def test_rv_table(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        sql = '''
            SELECT Url
            FROM Reviews
            ORDER BY Timestamp
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('https://www.yelp.com/biz/uovo-santa-monica?hrid=0TCNN6GtV7yKd4GtcJ486w&adjust_creative=r7MUJQBTl9K6JVyS6S33Ug&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_reviews&utm_source=r7MUJQBTl9K6JVyS6S33Ug',), result_list)
        self.assertTrue(len(result_list) <= 130*3)

        sql = '''
            SELECT COUNT(*)
            FROM Reviews
            GROUP BY ResId
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count <= 6)
        conn.close()


class TestInterface(unittest.TestCase):

    def test_res_search(self):
        results = process_command('restaurants city=Los Angeles popularity bottom=20')
        self.assertEqual(results[0][0], 'Republique')
        self.assertEqual(results[3][1], 3.5)
        self.assertEqual(len(results), 20)

        results = process_command('restaurants')
        self.assertEqual(len(results), 10)
        self.assertEqual(results[0][0], 'Buona Forchetta ')
        self.assertGreater(results[3][2], 3)

    def test_rv_search(self):
        results = process_command('reviews city=La Jolla timestamp')
        self.assertEqual(results[0][1],4)

    def test_cities_search(self):
        results = process_command('cities avg_price top=5')
        self.assertEqual(results[0][0], 'Santa Monica')

        results = process_command('cities count top=5')
        self.assertEqual(results[0][0], 'San Diego')
        self.assertEqual(results[0][2], 58)

        results = search_keyword_in_db('Galaxy')
        self.assertEqual(results[0][1], 'Galaxy Taco')





unittest.main(verbosity = 2)
