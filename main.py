import json
import time
import csv
import requests
import os
from graphqlclient import GraphQLClient
dictionaryOfGamers = {}

tournamentSlugs = ["Add SLUGS Here"]

authToken = "YOUR AUTH TOKEN"

for slug in tournamentSlugs:

    print("Grabbing entrants from : " + slug)
    client = GraphQLClient('https://api.start.gg/gql/alpha')
    client.inject_token('Bearer ' + authToken)
    result = client.execute('''query TournamentAttendees($tournamentSlug: String!) {
      tournament(slug: $tournamentSlug) {
        name
        participants(query: {}) {
          nodes {
            gamerTag
            user{
              discriminator
            }
          }
        }
      }
    }''', {
        "tournamentSlug": slug
    })

    outData = json.loads(result)

    print(outData['data']['tournament']['name'])
    for participant in outData['data']['tournament']['participants']['nodes']:
        if participant['user'] is not None:
            if participant['user'] and participant['user']['discriminator'] not in dictionaryOfGamers:
                dictionaryOfGamers[participant['user']['discriminator']] = (participant['gamerTag'], 2)
            else:
                newAttendanceTotal = dictionaryOfGamers[participant['user']['discriminator']][1] + 1
                dictionaryOfGamers.update({participant['user']['discriminator']: (participant['gamerTag'], newAttendanceTotal)})
    print("Pausing execution to stay under required average request rate")
    time.sleep(1)


if os.path.exists("tournamentAttendance.csv"):
    os.remove("tournamentAttendance.csv")
with open("tournamentAttendance.csv", mode = 'w', newline = '') as file:
    writer = csv.writer((file))
    writer.writerow(("Start.gg Identifier", "Tag", "Tournaments Attended"))
    for gamer in dictionaryOfGamers:
        print("Identifier: " + gamer + " Tag: " + dictionaryOfGamers[gamer][0])
        writer.writerow((gamer, dictionaryOfGamers[gamer][0].encode("ascii", errors="ignore").decode(), dictionaryOfGamers[gamer][1]))
