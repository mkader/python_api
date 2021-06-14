import requests
class ApiError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)

def sc_404():
        #https://api.open-notify.org/astros.json
        #ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
	response = requests.get("https://api.plos.org/search1?q=title:india")
	print(response.status_code)
def sc_404_raise_error():
	response = requests.get("https://api.plos.org/search1?q=title:india")
	if response.status_code != 200:
	     #This means something went wrong.
    	    raise ApiError('GET /search1/ {}'.format(response.status_code))
def sc_200():
	response = requests.get("https://api.plos.org/search?q=title:india")
	print(response.status_code)
def sc_response():
	response = requests.get("https://api.plos.org/search?q=title:india")
	print(response.status_code)
	print(response.json())

import json
def jprint(obj):
        #create a formatted string of the Python JSON object
    	text = json.dumps(obj, sort_keys=True, indent=4)
    	print(text)
def sc_response_jumps():
	response = requests.get("https://api.plos.org/search?q=title:india")
	jprint(response.json())
def sc_querystring():
        parameters = {
          "q": "title:india",
          "start": 1,
          "rows":2
        }
        #https://api.plos.org/search?q=title:india&start=1&rows=2
        response = requests.get("https://api.plos.org/search", params=parameters)
        jprint(response.json())
def sc_response_parse():
	response = requests.get("https://api.plos.org/search?q=title:india&start=1&rows=2")
	docs = response.json()['response']
	jprint(docs)
def sc_response_parse_docs():
	response = requests.get("https://api.plos.org/search?q=title:india&start=1&rows=2")
	docs = response.json()['response']['docs']
	#jprint(docs)
	maxScores = []
	for d in docs:
		jprint(d)
		jprint(d['article_type'])

# public apis - https://github.com/public-apis/public-apis#animals
# POkeman API https://pokeapi.co/, https://pokeapi.co/api/v2/pokemon/squirtle
"""
{
    "response": {
        "docs": [
            {
                "abstract": ["Although "],
                "article_type": "Health in Action",
                "author_display": [
                    "Sanjit Bagchi"
                ],
                "eissn": "1549-1676",
                "id": "10.1371/journal.pmed.0030082",
                "journal": "PLoS Medicine",
                "publication_date": "2006-03-07T00:00:00Z",
                "score": 7.941781,
                "title_display": "Telemedicine in Rural India"
            },
            {
                "abstract": [],
                "article_type": "Research Article",
                "author_display": [
                    "Santwana Verma",
                    "Ghanshyam K. Verma",
                    "Gagandeep Singh",
                ],
                "eissn": "1935-2735",
                "id": "10.1371/journal.pntd.0001673",
                "journal": "PLoS Neglected Tropical Diseases",
                "publication_date": "2012-06-12T00:00:00Z",
                "score": 7.5583353,
                "title_display": "Sporotrichosis in Sub-Himalayan India"
            }
        ],
        "maxScore": 7.941781,
        "numFound": 1243,
        "start": 1
    }
}
"""
#sc_404()
#sc_404_raise_error()
#sc_200()
#sc_response()
#sc_response_jumps()
#sc_querystring()
#sc_response_parse()
sc_response_parse_docs()
