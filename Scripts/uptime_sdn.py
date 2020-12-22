# Deze script zorgt ervoor dat we met een bot de gegevens van de virtuele apparaten in APIC-EM in een tabel
# omzetten en versturen 
#------------------------------------------------------------------------------------
# Modules
#------------------------------------------------------------------------------------
# Modules zijn bestanden die python definties en statements bevatten.
# De volgende modules zullen gebruikt worden in deze script zoals json, time en requests.
import time
import json
import requests
import urllib3
# tabulte wordt gebruikt om tabellen te maken in python. Hiermee zullen de gegevens van APIC-EM
# omgezet worden in een tabel.
from tabulate import*

# Deze lijn schakelt waarschuwingen uit tegen ongeverieerde HTTPS requests.
requests.packages.urllib3.disable_warnings()
#-------------------------------------------------------------------------------------
# Ticket aanvragen
#-------------------------------------------------------------------------------------
# Deze functie zorgt ervoor dat we een ticket aanvragen en gebruiken om gegevens van APIC-EM
# op te vragen. We zullen deze functie later nog gebruiken in de script
def get_ticket():
    # De API waar we een ticken zullen aanvragen
    api_url = "https://devnetsbx-netacad-apicem-3.cisco.com/api/v1/ticket"
    # De media type zal een apllication zijn met een structuur van json
    headers = {
        "content-type": "application/json"  
        }
    # In de body hebben we de authenticatie gegevens van de devnetsbx-netacad-apicem-3 gezet.
    # Zo hebben we toegang in APIC-EM
    body_json = {
        "username": "devnetuser",
        "password": "Xj3BDqbU"
        }
    # Maakt de aanvraag naar de API.
    resp=requests.post(api_url, json.dumps(body_json),headers=headers,verify=False)
    # In de body hebben we de authenticatie gegevens van de devnetsbx-netacad-apicem-3 gezet.
    # Zo zullen toegang krijgen in print("Ticket request status: ", resp.status_code)
    # Inspecteert de retourneerde aanvraag om een serviceticket te krijgen.
    print("Ticket request status: ", resp.status_code)
    response_json = resp.json() 
    # Deze variabel zal onze ticket maken
    serviceTicket = response_json["response"]["serviceTicket"]
    print("The service ticket number is: ", serviceTicket)
    # Retouneertd de ticket.
    return serviceTicket

#------------------------------------------------------------------------------------
# Input accesstoken
#------------------------------------------------------------------------------------
# 

accessToken = input("Geef je accestoken in: ")
accessToken = "Bearer " + accessToken

r = requests.get(   "https://api.ciscospark.com/v1/rooms",
                headers = {"Authorization": accessToken}
            )
# Als de HTML status code niet 200(dat de request geslaagd is) is dan krijg je volgende melding met de huidige
# status code  
if not r.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

#------------------------------------------------------------------------------------
# Lijst van rooms tonen
#------------------------------------------------------------------------------------
# In dit stuk vragen we de lijst van rooms aan van de gebruiker.
print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print (room["title"])
#------------------------------------------------------------------------------------
# Room kiezen
#------------------------------------------------------------------------------------
# De gebruiker zal een room moeten kiezen door de naam van de room moeten te typpen.
# Als de gebruiker een typfout maakt of een naam geeft die buiten de lijst bevindt zal dit stuk geloopt worden
# tot dat er correcte naam gegeven wordt.
# Wat ook handig is is dat als we een de naam van de room half getypt wordt dan zal er gezoekt worden naar de execte room
# TIP!!! Stel dat je twee rooms hebt die beginnen met  de letter 'M' geeft een dan een ander letter erbij voor de
# input anders zal de loop kijken naar de eerste room met het beginnende letter.
while True:
    time.sleep(1)
    roomNameToSearch = input("Welke room moet gemonitoord worden for de volgende tabel? ")
    roomIdToGetMessages = None

    for room in rooms:
        if(room["title"].find(roomNameToSearch) != -1):
            print ("Found rooms with the word " + roomNameToSearch)
            print(room["title"])
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room : " + roomTitleToGetMessages)
            break

    if(roomIdToGetMessages == None):
        print("Sorry, I didn't find any room with " + roomNameToSearch + " in it.")
        print("Please try again...")
    else:
        break
#-------------------------------------------------------------------------------------
# Recentste bericht tonen van de room
#-------------------------------------------------------------------------------------
# Deze loop zorgt ervoor dat altijd de recenste bericht getoond wordt in de room van de gebruiker
while True:
    # time.sleep(1) is een vertraging naar de loop om niet de rate limiet te overschrijden van de API calls
    time.sleep(1)
    
    GetParameters = {
                        "roomId": roomIdToGetMessages,
                        "max": 1
                        }
    
    r = requests.get("https://api.ciscospark.com/v1/messages",
                      params = GetParameters,
                      headers = {"Authorization": accessToken}
                  )
                
    if not r.status_code == 200:
        raise Exception( "Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
 
    json_data = r.json()
    #Als de room geen berichten heeft krijg je deze exception en wordt stopt de script.
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")
 
    messages = json_data["items"]
    message = messages[0]["text"]
    print("Gekregen bericht: \n" + message)
    #-------------------------------------------------------------------------------------
    # command aan de bot geven(print_devices_uptime)
    #-------------------------------------------------------------------------------------
    # Nu dat via de CLI kunnen zien wat het recenste bericht is van de room. kunnen nu een commands geven
    # zodat de bot meerdere functies heeft.
    # Het eerste command is om de om de virtuele apparten van APIC-em op te vragen, de gegevens dan vormen in
    # een tabel en die tabel dan versturen naar de room van de gebruiker
    
    if message.find("print_devices_uptime()") == 0:
        
        #In dit stuk vragen we de gegevens van de virtuele apparaten op APIC-EM aan         
        api_url = "https://devnetsbx-netacad-apicem-3.cisco.com/api/v1/network-device"
        #Om te ticket aan te vragen maken we een variabel aan die functie get_ticket() aanvraagt
        ticket = get_ticket()
# 
        headers = {
            "content-type": "application/json",
            "X-Auth-Token": ticket
            }
#        
        resp = requests.get(api_url, headers=headers, verify=False)
        print("Status of / device request: ", resp.status_code)
# 
        if resp.status_code != 200:
            raise Exception("Status code does not equeal 200. Response text: " + resp.text)
        #-------------------------------------------------------------------------------------
        # Tabel aanmaken
        #-------------------------------------------------------------------------------------
        # We zullen eerst een json_body opvragen en daarnaast maken we lijst maken waar we de gegevens toevoegen
        # voor ons tabel
        # Daarnaast maken nog een list voor de header van tabel en zetten we die twee lists samen in een variabel.
        response_json = resp.json()
        device_list=[]
        i = 0
# 
        for item in response_json["response"]:
            i += 1
            device = [
                    i,
                    item["id"],
                    item["hostname"],
                    item["upTime"]]
            device_list.append( device )
        table_header = [
                "Number",
                "ID",
                "Hostname",
                "uptime"
                ]
#
        response_message = (tabulate (device_list, table_header) )      
        
        #------------------------------------------------------------------------------------------
        # Tabel versturen naar de gekozen room van de gebruiker
        #------------------------------------------------------------------------------------------
        # We versturen dit tabel naar dan naar de room van de gebruiker op webex teams
        print("verstuurd naar Webex Teams: \n" +response_message)
        time.sleep(1)
        # 
        HTTPHeaders = {
                        "Authorization":accessToken,
                        "Content-Type": "application/json"
                        }
        # 
        PostData = {
                        "roomId": roomIdToGetMessages,
                        "text":response_message
            }
        #
        r = requests.post( "https://api.ciscospark.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )
        
        if not r.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    # Het command "command()" toont een kleine lijst met allerlei commando's

    elif message.find("commands()") == 0:
        response_message = "Commands: \n print_devices_uptime(): toont apparaten met hun uptime. \n quit(): stopt de script"
        print("verstuurd naar Webex Teams: \n" +response_message)

        HTTPHeaders = {
                        "Authorization":accessToken,
                        "Content-Type": "application/json"
                        }

        PostData = {
                        "roomId": roomIdToGetMessages,
                        "text":response_message
            }

        r = requests.post( "https://api.ciscospark.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )

        if not r.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
    # De laatste command is quit(). quit() zorgt ervoor dat de bot uitgeschakeld wordt.

    elif message.find("quit()") == 0:
        response_message = "script wordt gestopt"
        print("verstuurd naar Webex Teams: \n" +response_message)

        HTTPHeaders = {
                        "Authorization":accessToken,
                        "Content-Type": "application/json"
                        } 
        PostData = {
                        "roomId": roomIdToGetMessages,
                        "text":response_message
            }
        r = requests.post( "https://api.ciscospark.com/v1/messages", 
                              data = json.dumps(PostData), 
                              headers = HTTPHeaders
                         )
        if not r.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
        break
