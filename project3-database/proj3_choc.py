import sqlite3
import csv
import json

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from CSV and JSON into a new database called choc.db
DBNAME = 'choc.db'
BARSCSV = 'flavors_of_cacao_cleaned.csv'
COUNTRIESJSON = 'countries.json'

def create_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print('error while creating the database')
        return None
    cur.execute("DROP TABLE IF EXISTS 'Bars';")
    cur.execute("DROP TABLE IF EXISTS 'Countries';")
    statement = '''
        CREATE TABLE 'Countries' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'Alpha2' TEXT NOT NULL,
            'Alpha3' TEXT NOT NULL,
            'EnglishName' TEXT NOT NULL,
            'Region' TEXT NOT NULL,
            'Subregion' TEXT NOT NULL,
            'Population' INTEGER NOT NULL,
            'Area' REAL
        );
    '''
    cur.execute(statement)
    statement = '''
        CREATE TABLE 'Bars' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'Company' TEXT NOT NULL,
            'SpecificBeanBarName' TEXT NOT NULL,
            'REF' TEXT NOT NULL,
            'ReviewDate' TEXT NOT NULL,
            'CocoaPercent' REAL NOT NULL,
            'CompanyLocationId' INTEGER,
            'Rating' REAL NOT NULL,
            'BeanType' TEXT,
            'BroadBeanOriginId' INTEGER,
            FOREIGN KEY(CompanyLocationId) REFERENCES Countries(Id),
            FOREIGN KEY(BroadBeanOriginId) REFERENCES Countries(Id)
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()



def populate_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

    except:
        print('error while populating the database')
        return None

    with open(COUNTRIESJSON, 'r') as f:
        json_reader = json.load(f)
        for country in json_reader:
            cur.execute("INSERT INTO 'Countries' (Alpha2, Alpha3, EnglishName, Region, Subregion, Population, Area) VALUES (?, ?, ?, ?, ?, ?, ?);", (country["alpha2Code"], country["alpha3Code"], country["name"], country["region"], country["subregion"], country["population"], country["area"]))
    conn.commit()
    with open(BARSCSV, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0] == 'Company':
                continue
            try:
                location_id = cur.execute("SELECT Id FROM 'Countries' WHERE EnglishName = ?;", (row[5],)).fetchone()[0]
            except:
                location_id = None
            try:
                origin_id = cur.execute("SELECT Id FROM 'Countries' WHERE EnglishName = ?;", (row[8],)).fetchone()[0]
            except:
                origin_id = None
            cocoa_percent = float(row[4][:-1])/100
            cur.execute("INSERT INTO 'Bars' (Company, SpecificBeanBarName, REF, ReviewDate, CocoaPercent, CompanyLocationId, Rating, BeanType, BroadBeanOriginId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (row[0], row[1], row[2], row[3], cocoa_percent, location_id, row[6], row[7], origin_id))
    conn.commit()
    conn.close()

# Part 2: Implement logic to process user commands
def process_command(command):
    if command == "":
        return None
    command_word = command.split()[0]
    if command_word not in ['bars', 'companies', 'countries', 'regions']:
        print("Command not recognized:", command)
        return None
    allowed_search_key = {
        'bars': ['sellcountry', 'sourcecountry', 'sellregion', 'sourceregion'],
        'companies': ['country', 'region'],
        'countries': ['region'],
        'regions': []
    }
    search_key = 0
    search_value = 0
    allowed_region_def = {
        'bars': [],
        'companies': [],
        'countries': ['sellers', 'sources'],
        'regions': ['sellers', 'sources'],
    }
    region_def = 'sellers'
    allowed_sorting = {
        'bars': ['ratings', 'cocoa'],
        'companies': ['ratings', 'cocoa', 'bars_sold'],
        'countries': ['ratings', 'cocoa', 'bars_sold'],
        'regions': ['ratings', 'cocoa', 'bars_sold']
    }
    sorting = 'ratings'
    limit = 10
    for argument in command.split()[1:]:
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
            else:
                print("Command not recognized:", command)
                print("Please input a valid parameter other than", key)
                return None

        elif (argument in allowed_region_def[command_word]):
            region_def = argument
        elif (argument in allowed_sorting[command_word]):
            sorting = argument
        else:
            print("Command not recognized:", command)
            print("Please input a valid parameter other than", argument)
            return None

    link_search_key = {
        'sellcountry': 'C1.Alpha2',
        'sourcecountry': 'C2.Alpha2',
        'sellregion': 'C1.Region',
        'sourceregion': 'C2.Region',
        'country': 'C1.Alpha2',
        'region': 'Region',
        0: 0
    } # C1 -> Sellers, C2 -> Sources
    link_region_ref = {
        'sellers': 'C1',
        'sources': 'C2'
    }
    link_agg = {
        'cocoa': 'Avg(B.CocoaPercent) AS AvgCocoa',
        'ratings': 'Avg(B.Rating) AS AvgRating',
        'bars_sold': 'Count(*) AS CountBars'
    }
    link_sorting = {
        'cocoa': 'AvgCocoa',
        'ratings': 'AvgRating',
        'bars_sold': 'CountBars'
    }
    if (search_key == 'region') and (command_word == 'countries'):
        search_key = link_region_ref[region_def] + '.' + link_search_key[search_key]
    else:
        search_key = link_search_key[search_key]

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    if command_word == 'bars':
        link_sorting = {
            'cocoa': 'B.CocoaPercent',
            'ratings': 'B.Rating'
        } # special sorting names
        statement = """SELECT B.SpecificBeanBarName, B.Company, C1.EnglishName, B.Rating, B.CocoaPercent, C2.EnglishName
                       FROM Bars AS B
                       LEFT JOIN Countries AS C1 ON B.CompanyLocationId = C1.Id
                       LEFT JOIN Countries AS C2 ON B.BroadBeanOriginId = C2.Id
                       WHERE {} = ?
                       ORDER BY {} {}
                       LIMIT ?""".format(search_key, link_sorting[sorting], 'DESC' * int (limit > 0))
        cur.execute(statement, (search_value, abs(limit)))

    elif command_word == 'companies':
        statement = """SELECT DISTINCT B.Company, C1.EnglishName, {}
                       FROM Bars AS B
                       LEFT JOIN Countries AS C1 ON B.CompanyLocationId = C1.Id
                       WHERE {} = ?
                       GROUP BY B.Company
                       HAVING count(B.Company) > 4
                       ORDER BY {} {}
                       LIMIT ?""".format(link_agg[sorting], search_key, link_sorting[sorting], 'DESC' * int (limit > 0))
        cur.execute(statement, (search_value, abs(limit)))

    elif command_word == 'countries':
        statement = """SELECT DISTINCT {0}.EnglishName, {0}.Region, {1}
                       FROM Bars AS B
                       LEFT JOIN Countries AS C1 ON B.CompanyLocationId = C1.Id
                       LEFT JOIN Countries AS C2 ON B.BroadBeanOriginId = C2.Id
                       WHERE {2} = ?
                       GROUP BY {0}.EnglishName
                       HAVING count({0}.Id) > 4
                       ORDER BY {3} {4}
                       LIMIT ?""".format(link_region_ref[region_def], link_agg[sorting], search_key, link_sorting[sorting], 'DESC' * int (limit > 0))
        cur.execute(statement, (search_value, abs(limit)))

    elif command_word == 'regions':
        statement = """SELECT {0}.Region, {1}
                       FROM Bars AS B
                       LEFT JOIN Countries AS C1 ON B.CompanyLocationId = C1.Id
                       LEFT JOIN Countries AS C2 ON B.BroadBeanOriginId = C2.Id
                       WHERE {2} = ?
                       GROUP BY {0}.Region
                       HAVING count({0}.Id) > 4
                       ORDER BY {3} {4}
                       LIMIT ?""".format(link_region_ref[region_def], link_agg[sorting], search_key, link_sorting[sorting], 'DESC' * int (limit > 0))
        cur.execute(statement, (search_value, abs(limit)))

    raw_data = [row for row in cur]
    conn.close()
    return raw_data

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def pretty_print(rows, response):
    max_len = [ 0 for x in rows[0] ]
    for row in rows:
        for i in range(len(row)):
            if type(row) == type(.0):
                max_len[i] = 5
                continue
            if len(str(row[i])) > max_len[i]:
                max_len[i] = len(str(row[i]))
    for i in range(len(max_len)):
        if max_len[i] > 15:
            max_len[i] = 15
    for row in rows:
        st = ""
        for i in range(len(row)):
            if row[i] == None:
                st += "{text: <{fill}}  ".format(text = 'Unknown', fill = max_len[i])
                continue
            if (type(row[i]) == type(.0)) and (row[i] > 1):
                st += "{text: <{fill}}  ".format(text = "{:.1f}".format(row[i]), fill = max_len[i])
            elif (type(row[i]) == type(.0)) and (row[i] <= 1):
                st += "{text: <{fill}}  ".format(text = "{:.0%}".format(row[i]), fill = max_len[i])
            elif len(str(row[i])) > max_len[i]:
                st += "{text: <{fill}}...  ".format(text = str(row[i][:12]), fill = max_len[i] - 3)
            else:
                st += "{text: <{fill}}  ".format(text = str(row[i]), fill = max_len[i])
        print(st)


# Part 3: Implement interactive prompt. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    while True:
        response = input('\nEnter a command: ')
        if response == 'exit':
            print('bye')
            break
        if response == 'help':
            print(help_text)
            continue
        raw_data = process_command(response)
        if raw_data != None:
            pretty_print(raw_data, response)

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
    create_db()
    populate_db()
    interactive_prompt()
