import json
import requests
import webbrowser

class Media:
    def __init__(self, title = "No Title", author = "No Author", release_year = "Unknown", json = None):
        self.title = title
        self.author = author
        self.release_year = str(release_year)
        if json:
            if 'trackName' in json:
                self.title = json['trackName']
            if 'artistName' in json:
                self.author = json['artistName']
            if 'releaseDate' in json:
                self.release_year = json['releaseDate'][:4]
            if 'collectionViewUrl' in json:
                self.previewUrl = json['collectionViewUrl']

    def __str__(self):
        return "{title} by {author} ({release_year})".format(
            title = self.title, author = self.author, release_year = self.release_year
        )

## Other classes, functions, etc. should go here
class Song(Media):
    def __init__(self, title = "No Title", author = "No Author", release_year = "Unknown", album = "No Album", genre = "Unknown", track_length = 0, json = None):
        super().__init__(title, author, release_year, json = json)
        self.album = album
        self.genre = genre
        self.track_length = track_length
        if json:
            if 'collectionName' in json:
                self.album = json['collectionName']
            if 'primaryGenreName' in json:
                self.genre = json['primaryGenreName']
            if 'trackTimeMillis' in json:
                self.track_length = int(json['trackTimeMillis'])

    def __str__(self):
        return super().__str__() + ' [{genre}]'.format(genre = self.genre)
    def __len__(self):
        return self.track_length // 1000 # in secs

class Movie(Media):
    def __init__(self, title = "No Title", author = "No Author", release_year = "Unknown", rating = "Unrated", movie_length = 0, json = None):
        super().__init__(title, author, release_year, json = json)
        self.rating = rating
        self.movie_length = movie_length
        if json:
            if 'contentAdvisoryRating' in json:
                self.rating = json['contentAdvisoryRating']
            if 'trackTimeMillis' in json:
                self.movie_length = json['trackTimeMillis']

    def __str__(self):
        return super().__str__() + ' [{rating}]'.format(rating = self.rating)
    def __len__(self):
        return self.movie_length // 60000 # in mins



def makeMediaList(keyword, type = None):
    baseurl = "https://itunes.apple.com/search"
    params = {}
    params['term'] = keyword
    params['limit'] = 50
    if type:
        params['entity'] = type

    try:
        resp = requests.get(baseurl, params=params)
        resp_text_dict = json.loads(resp.text)
    except:
        print("* error: Can't connect to API. Please check your network.")
        return None

    medias = []
    for each in resp_text_dict["results"]:
        # print(asong)
        if 'kind' not in each:
            medias.append(Media(json = each))
        elif each['kind'] == 'song':
            medias.append(Song(json = each))
        elif each['kind'] == 'feature-movie':
            medias.append(Movie(json = each))
        else:
            medias.append(Media(json = each))
    return medias



if __name__ == "__main__":
    # your control code for Part 4 (interactive search) should go here
    command = '\nEnter a search term, or “exit” to quit: '
    while True:
        inp = input(command)
        if inp == 'exit':
            break
        if inp.isdigit():
            inp = int(inp)
            if inp >= len(sorted_medias):
                print('Number not valid!')
                continue
            try:
                print("Launching {} in web browser...".format(sorted_medias[inp].previewUrl))
                webbrowser.open(sorted_medias[inp].previewUrl)
            except:
                print("Can't preview for now")
            continue
        medias = makeMediaList(inp)
        sorted_medias = [""]

        print('\nSONGS')
        song_count = 0
        for each in medias:
            if type(each) == Song:
                song_count += 1
                sorted_medias.append(each)
                print(song_count, each)
        if song_count == 0:
            print('No songs')

        print('\nMOVIES')
        movie_count = song_count
        for each in medias:
            if type(each) == Movie:
                movie_count += 1
                sorted_medias.append(each)
                print(movie_count, each)
        if song_count == movie_count:
            print('No movies')

        print('\nOTHER MEDIA')
        other_count = movie_count
        for each in medias:
            if (type(each) != Song) and (type(each) != Movie):
                other_count += 1
                sorted_medias.append(each)
                print(other_count, each)
        if movie_count == other_count:
            print('No other medias')

        command = '\nEnter a number for more info, or another search term, or exit: '
