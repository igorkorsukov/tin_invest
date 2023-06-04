from dataclasses import dataclass

RATINGS_FILE = "ratings.csv"
CSV_SEP = '|'

RATING_TO_NUM = {
    'D': 0,
    'C-': 1,
    'C': 2,
    'C+': 3,
    'CC-': 4,
    'CC': 5,
    'CC+': 6,
    'CCC-': 7,
    'CCC': 8,
    'CCC+': 9,
    'B-': 10,
    'B': 11,
    'B+': 12,
    'BB-': 13,
    'BB': 14,
    'BB+': 15,
    'BBB-': 16,
    'BBB': 17,
    'BBB+': 18,
    'A-': 19,
    'A': 20,
    'A+': 21,
    'AA-': 22,
    'AA': 23,
    'AA+': 24,
    'AAA-': 25,
    'AAA': 26,
    'AAA+': 27,
    '-': 30
}

RATING_CONSOLIDATION = {
    'C': ['D', 'C-', 'C', 'C+', 'CC-', 'CC', 'CC+', 'CCC-', 'CCC', 'CCC+'],
    'B': ['B-', 'B', 'B+'],
    'BB': ['BB-', 'BB', 'BB+'],
    'BBB': ['BBB-', 'BBB', 'BBB+'],
    'A': ['A-', 'A', 'A+'],
    'AA': ['AA-', 'AA', 'AA+'],
    'AAA': ['AAA-', 'AAA', 'AAA+'],
    '-': ['-']
}

@dataclass
class Rating:    
    name: str = ""
    isin: str = ""
    rating: str = ""

def init(config):
    RATINGS_FILE = config.RATINGS_FILE    

def loadRatings():
    ratings = []
    with open(RATINGS_FILE) as file:
        for line in file:
            datas = line.rstrip().split(CSV_SEP)
            r = Rating()
            r.name = datas[0]
            r.isin = datas[1]
            r.rating = datas[2]
            ratings.append(r)
    return ratings 

def findRating(ratings, isin):
    for r in ratings:
        if r.isin == isin:
            return r.rating
    return "-"

def isRatingLess(r1, r2):
    return RATING_TO_NUM[r1] < RATING_TO_NUM[r2]      

def consolidate(r):
    for key, value in RATING_CONSOLIDATION.items():
        if r in value:
            return key
    return r
