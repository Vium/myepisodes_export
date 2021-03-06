from myepisodes import MyEpisodes
from hashlib import sha1
import tvdb_api, urllib2, json

TRAKT_KEY = '##TRAKT_API_KEY##'
TRAKT_USER = '##TRAKT_USER##'
TRAKT_PASS = '##TRAKT_PASS##'
MYEP_USER = '##MYEP_USER##'
MYEP_PASS = '##MYEP_PASS##'

tvdb = tvdb_api.Tvdb()

trakt_pass_sha1 = sha1(TRAKT_PASS).hexdigest()

me = MyEpisodes(MYEP_USER, MYEP_PASS)
me.login()
me.get_show_list()

watchlist = []

for show in me.show_list:
    try:
        tvdb_data = tvdb[show['name']]
    except:
        print "FAIL - Could not get TVDB ID for %s" % (show['name'])
        continue

    watchlist.append({'tvdb_id': tvdb_data['id'], "title": tvdb_data['seriesname']})

    collection_episodes = me.get_collection_episodes(show["id"])

    trakt_data = {
        "username": TRAKT_USER,
        "password": trakt_pass_sha1,
        "tvdb_id": tvdb_data['id'],
        "title": tvdb_data['seriesname'],
        "episodes": collection_episodes
    }

    req = urllib2.Request('https://api.trakt.tv/show/episode/library/' + TRAKT_KEY, json.dumps(trakt_data), {'content-type': 'application/json'})
    f = urllib2.urlopen(req)
    status = json.loads(f.read())

    if(status['status'] == 'success'):
        print "OK - Updated catalogue of %s - %s" % (tvdb_data['seriesname'], status['message'])
    else:
        print "FAIL - Could not update catalogue of %s - %s" % (tvdb_data['seriesname'], status['message'])


    seen_episodes = me.get_seen_episodes(show["id"])

    trakt_data = {
        "username": TRAKT_USER,
        "password": trakt_pass_sha1,
        "tvdb_id": tvdb_data['id'],
        "title": tvdb_data['seriesname'],
        "episodes": seen_episodes
    }

    req = urllib2.Request('http://api.trakt.tv/show/episode/seen/' + TRAKT_KEY, json.dumps(trakt_data), {'content-type': 'application/json'})
    f = urllib2.urlopen(req)
    status = json.loads(f.read())

    if(status['status'] == 'success'):
        print "OK - Updated seen status of %s - %s" % (tvdb_data['seriesname'], status['message'])
    else:
        print "FAIL - Could not update seen status of %s - %s" % (tvdb_data['seriesname'], status['message'])

trakt_data = {
    "username": TRAKT_USER,
    "password": trakt_pass_sha1,
    "shows": watchlist
}

req = urllib2.Request('https://api.trakt.tv/show/watchlist/' + TRAKT_KEY, json.dumps(trakt_data), {'content-type': 'application/json'})
f = urllib2.urlopen(req)
status = json.loads(f.read())

if(status['status'] == 'success'):
    print "OK - Updated Watchlist"
else:
    print "FAIL - Could not update Watchlist"
