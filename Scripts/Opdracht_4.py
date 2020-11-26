#Opdracht 4
#Ik zal een script maken waar we de weg kunnen opvragen van van een speciefieke locatie
#------------------------------------------------------------------------

#Sectie 1

#------------------------------------------------------------------------

#
import json
import requests

#
#requests.packages.urllib3.disable_warnings()
choice = input("wil je de hard-coded token gebruiken? j/n: ")
if choice == 'n' or choice == 'N' or choice == choice == 'nee' or choice == 'no':
    accessToken = input("Geef is je accesstoken in: ")
    accessToken = "Bearer " + accessToken
else:
    accessToken = "Bearer YWY0YTdhM2MtMDg4Ni00ZmUzLThhOTAtZThhNTY1YzBiZjk0MmVlNmM1NGEtYTk2_PF84_consumer" 
    
r = requests.get("https://webexapis.com/v1/rooms",
                  headers =  {"Authorization": accessToken}
                )

#
if not r.status_code == 200:
    raise Exception("Incorrecte antwoord van Webex Teams API. Status code: {}. Text: {}".format(r.status_code,r.text))
else:
    print(r.status_code)

print("Lijst van een rroms:")
rooms = r.json()["items"]
for room in rooms:
    print(#"Type:", room["type"],
          "Naam:", room["title"])

while True:
    roomNameToSearch = input("Welke room zou gecontroleerd moeten worden voor /location (bv. /Zavelaere) bericht?")

    roomIdToGetMessages = None
    for room in rooms:
        if(room["title"].find(roomNameToSearch) != -1):
            print("Rooms gevonden met het woord" + roomNameToSearch)
            print(room["title"])

            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Gevonden room : " + roomTitleToGetMessages)
            break
        if(roomIdToGetMessages == None):
            print("Sorry, ik kan geen room vinden " + roomNameToSearch + " in het.")
            print("Probeer het opnieuw...")
        else:
                break

