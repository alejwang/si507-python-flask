import unittest
import json
import requests
import proj1_f18 as proj1

class TestMedia(unittest.TestCase):

    def testMediaConstructor(self):
        m1 = proj1.Media()
        m2 = proj1.Media("1999", "Prince", "1999")

        self.assertEqual(m1.title, "No Title")
        self.assertEqual(m1.author, "No Author")
        self.assertEqual(m1.release_year, "Unknown")

        self.assertEqual(m2.title, "1999")
        self.assertEqual(m2.author, "Prince")

        self.assertEqual(str(m2), "1999 by Prince (1999)")

    def testSongConstructor(self):
        s1 = proj1.Song()
        s2 = proj1.Song("December", "Taylor Swift", "2008")
        s3 = proj1.Song("December", "Taylor Swift", "2008", "Red", "Pop", 431333)

        self.assertEqual(s1.title, "No Title")
        self.assertEqual(s1.author, "No Author")
        self.assertEqual(s1.release_year, "Unknown")
        self.assertEqual(s1.album, "No Album")
        self.assertEqual(s1.genre, "Unknown")
        self.assertEqual(s1.track_length, 0)

        self.assertEqual(s2.title, "December")
        self.assertEqual(s2.author, "Taylor Swift")
        self.assertEqual(s2.release_year, "2008")

        self.assertEqual(s3.album, "Red")
        self.assertEqual(s3.genre, "Pop")
        self.assertEqual(s3.track_length, 431333)

        self.assertEqual(str(s3), "December by Taylor Swift (2008) [Pop]")
        self.assertEqual(len(s3), 431)

    def testMovieConstructor(self):
        m1 = proj1.Movie()
        m2 = proj1.Movie("BBM", "Lee Ann", "2005")
        m3 = proj1.Movie("BBM", "Lee Ann", "2005", "PG", 8013333)

        self.assertEqual(m1.title, "No Title")
        self.assertEqual(m1.author, "No Author")
        self.assertEqual(m1.release_year, "Unknown")
        self.assertEqual(m1.rating, "Unrated")
        self.assertEqual(m1.movie_length, 0)

        self.assertEqual(m2.title, "BBM")
        self.assertEqual(m2.author, "Lee Ann")
        self.assertEqual(m2.release_year, "2005")

        self.assertEqual(m3.rating, "PG")
        self.assertEqual(m3.movie_length, 8013333)

        self.assertEqual(str(m3), "BBM by Lee Ann (2005) [PG]")
        self.assertEqual(len(m3), 133)


    def testJsonConstructor(self):
        text1 = """
                {"wrapperType": "track", "kind": "feature-movie", "collectionId": 949030693, "trackId": 526768967, "artistName": "Steven Spielberg", "collectionName": "Steven Spielberg 7-Movie Director\u2019s Collection", "trackName": "Jaws",
                "collectionCensoredName": "Steven Spielberg 7-Movie Director\u2019s Collection", "trackCensoredName": "Jaws", "collectionArtistId": 345353262,
                "collectionArtistViewUrl": "https://itunes.apple.com/us/artist/universal-studios-home-entertainment/345353262?uo=4", "collectionViewUrl": "https://itunes.apple.com/us/movie/jaws/id526768967?uo=4",
                "trackViewUrl": "https://itunes.apple.com/us/movie/jaws/id526768967?uo=4",
                "previewUrl": "http://video.itunes.apple.com/apple-assets-us-std-000001/Video127/v4/a5/4c/6d/a54c6d2c-7003-1ae7-f002-84b4444bc05b/mzvf_5104399247891878253.640x266.h264lc.U.p.m4v", "artworkUrl30": "http://is1.mzstatic.com/image/thumb/Video18/v4/3c/ce/31/3cce31a9-ff9e-bc6b-f17d-a20c55d50db0/source/30x30bb.jpg", "artworkUrl60": "http://is1.mzstatic.com/image/thumb/Video18/v4/3c/ce/31/3cce31a9-ff9e-bc6b-f17d-a20c55d50db0/source/60x60bb.jpg",
                "artworkUrl100": "http://is1.mzstatic.com/image/thumb/Video18/v4/3c/ce/31/3cce31a9-ff9e-bc6b-f17d-a20c55d50db0/source/100x100bb.jpg",
                "collectionPrice": 9.99, "trackPrice": 9.99, "trackRentalPrice": 3.99, "collectionHdPrice": 14.99, "trackHdPrice": 14.99, "trackHdRentalPrice": 3.99, "releaseDate": "1975-06-20T07:00:00Z",
                "collectionExplicitness": "notExplicit", "trackExplicitness": "notExplicit", "discCount": 1, "discNumber": 1, "trackCount": 7, "trackNumber": 4, "trackTimeMillis": 7451455, "country": "USA", "currency": "USD", "primaryGenreName": "Thriller",
                "contentAdvisoryRating": "PG",
                "longDescription": "Directed by Academy Award\u00ae winner Steven Spielberg, Jaws set the standard for edge-of-your seat suspense, quickly becoming a cultural phenomenon and forever changing the way audiences experience movies. When the seaside community of Amityfinds itself under attack by a dangerous great white shark, the town\u2019s chief of police (Roy Scheider), a young marine biologist (Richard Dreyfuss) and a grizzled shark hunter (Robert Shaw) embark on a desperate quest to destroy the beast before it strikes again. Featuring an unforgettable score that evokes pure terror, Jaws remains one of the most influential and gripping adventures in motion picture history."}
                """
        text2 = """
                {"wrapperType": "track", "kind": "song", "artistId": 136975, "collectionId": 400835735, "trackId": 400835962, "artistName": "The Beatles", "collectionName": "TheBeatles 1967-1970 (The Blue Album)", "trackName": "Hey Jude", "collectionCensoredName": "The Beatles 1967-1970 (The Blue Album)", "trackCensoredName": "Hey Jude", "artistViewUrl": "https://itunes.apple.com/us/artist/the-beatles/136975?uo=4", "collectionViewUrl": "https://itunes.apple.com/us/album/hey-jude/400835735?i=400835962&uo=4", "trackViewUrl": "https://itunes.apple.com/us/album/hey-jude/400835735?i=400835962&uo=4", "previewUrl": "https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/Music/v4/d5/c8/10/d5c81035-a242-c354-45cf-f634e4127f43/mzaf_1171292596660883824.plus.aac.p.m4a", "artworkUrl30": "http://is3.mzstatic.com/image/thumb/Music/v4/63/ac/ef/63acef5a-8b6a-b748-5d4c-e6a7e9c13c37/source/30x30bb.jpg", "artworkUrl60": "http://is3.mzstatic.com/image/thumb/Music/v4/63/ac/ef/63acef5a-8b6a-b748-5d4c-e6a7e9c13c37/source/60x60bb.jpg", "artworkUrl100": "http://is3.mzstatic.com/image/thumb/Music/v4/63/ac/ef/63acef5a-8b6a-b748-5d4c-e6a7e9c13c37/source/100x100bb.jpg", "collectionPrice": 19.99, "trackPrice": 1.29, "releaseDate": "1968-08-26T07:00:00Z", "collectionExplicitness": "notExplicit", "trackExplicitness": "notExplicit", "discCount": 2, "discNumber": 1, "trackCount": 14, "trackNumber": 13, "trackTimeMillis": 431333, "country": "USA", "currency": "USD", "primaryGenreName": "Rock", "isStreamable": true}
                """
        text3 = """
                {"wrapperType": "audiobook", "artistId": 2082069, "collectionId": 516799841, "artistName": "Helen Fielding", "collectionName": "Bridget Jones's Diary (Unabridged)", "collectionCensoredName": "Bridget Jones's Diary (Unabridged)", "artistViewUrl": "https://itunes.apple.com/us/author/helen-fielding/id2082069?mt=11&uo=4", "collectionViewUrl": "https://itunes.apple.com/us/audiobook/bridget-joness-diary-unabridged/id516799841?uo=4", "artworkUrl60": "http://is4.mzstatic.com/image/thumb/Music/v4/23/5f/08/235f0893-fe39-452a-0b2e-f1fb173fa82a/source/60x60bb.jpg", "artworkUrl100": "http://is4.mzstatic.com/image/thumb/Music/v4/23/5f/08/235f0893-fe39-452a-0b2e-f1fb173fa82a/source/100x100bb.jpg", "collectionPrice": 20.95, "collectionExplicitness": "notExplicit", "trackCount": 1, "copyright": "\u2117 \u00a9 2012 Recorded Books", "country": "USA", "currency": "USD", "releaseDate": "2012-04-03T07:00:00Z", "primaryGenreName": "Fiction", "previewUrl": "https://audio-ssl.itunes.apple.com/apple-assets-us-std-000001/Music7/v4/d4/bc/c8/d4bcc89b-d66e-e015-2c3e-3f6432ccffa0/mzaf_51579112983128144.plus.aac.p.m4a"}
                """

        movie = proj1.Movie(json = json.loads(text1))
        song = proj1.Song(json = json.loads(text2))
        audiobook = proj1.Media(json = json.loads(text3))

        self.assertEqual(str(movie), "Jaws by Steven Spielberg (1975) [PG]")
        self.assertEqual(len(movie), 124)
        self.assertEqual(movie.title, "Jaws")
        self.assertEqual(movie.author, "Steven Spielberg")
        self.assertEqual(movie.release_year, "1975")
        self.assertEqual(movie.rating, "PG")
        self.assertEqual(movie.movie_length, 7451455)

        self.assertEqual(str(song), "Hey Jude by The Beatles (1968) [Rock]")
        self.assertEqual(len(song), 431)
        self.assertEqual(song.title, "Hey Jude")
        self.assertEqual(song.author, "The Beatles")
        self.assertEqual(song.release_year, "1968")
        self.assertEqual(song.album, "TheBeatles 1967-1970 (The Blue Album)")
        self.assertEqual(song.genre, "Rock")
        self.assertEqual(song.track_length, 431333)

        self.assertEqual(str(audiobook), "No Title by Helen Fielding (2012)")
        self.assertEqual(audiobook.title, "No Title")
        self.assertEqual(audiobook.author, "Helen Fielding")
        self.assertEqual(audiobook.release_year, "2012")

    def testiTunesAPI(self):
        medias1 = proj1.makeMediaList('&@#!$', 'audiobook')
        medias2 = proj1.makeMediaList('moana', 'movie')
        medias3 = proj1.makeMediaList('helter skelter', 'song')
        medias4 = proj1.makeMediaList('love')

        self.assertTrue(len(medias1)<=50)
        self.assertTrue(len(medias2)<=50)
        self.assertTrue(len(medias3)<=50)
        self.assertTrue(len(medias4)<=50)

        for each in medias1:
            self.assertIsInstance(each, proj1.Media)
        for each in medias2:
            self.assertIsInstance(each, proj1.Movie)
        for each in medias3:
            self.assertIsInstance(each, proj1.Song)
        for each in medias4:
            self.assertIsInstance(each, proj1.Media)



unittest.main(verbosity=2)
