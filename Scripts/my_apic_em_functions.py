#----------------------------
# Sectie 1. functies importeren
#----------------------------

# Hier importeren weren functies die we nodig hebben voor de volgende scripts
import sys
print(sys.executable)
import time
import json
import requests
# Een pretty print-tabular om een tabbelen te maken via een CLI utility.
from tabulate import*


requests.packages.urllib3.disable_warnings()

# Deze fucntie zorgt ervoor dat we ticket gaan aanvragen als authenticatie token.
def get_ticket():
    # De API waar we een ticken zullen aanvragen
    api_url = "https://devnetsbx-netacad-apicem-3.cisco.com/api/v1/ticket"
    # De media type zal een apllication zijn met een structuur van json
    headers = {
        "content-type": "application/json"  
        }
    # In de body hebben we de authenticatie gegevens van de devnetsbx-netacad-apicem-3 gezet.
    # Zo zullen toegang krijgen in 
    body_json = {
        "username": "devnetuser",
        "password": "Xj3BDqbU"
        }
    # Maakt de aanvraag naar de API.
    resp=requests.post(api_url, json.dumps(body_json),headers=headers,verify=False)
    # In de body hebben we de authenticatie gegevens van de devnetsbx-netacad-apicem-3 gezet.
    # Zo zullen toegang krijgen in     print("Ticket request status: ", resp.status_code)
    #Inspecteert de retourneerde aanvraag om een serviceticket te krijgen
    print("Ticket request status: ", resp.status_code)
    response_json = resp.json() 
    # Deze variabel zal onze ticket maken
    serviceTicket = response_json["response"]["serviceTicket"]
    print("The service ticket number is: ", serviceTicket)
    # Retouneertd de ticket. Dit is belangrijk want de volgende functies zullen werken.
    return serviceTicket
#============================
# Script 2. Gegevens van de host inventory in een tabel vormen
#============================


# Deze functiie zal een tabel printen met al de host die op je account van van sandboxapicem.com
def print_hosts():
    api_url = "https://devnetsbx-netacad-apicem-3.cisco.com/api/v1/host"
    # Deze variabel vraagt ons ticket op via de functie get_ticket()
    ticket = get_ticket()
    # X-Auth-Token wordt toegevoegd in de header om toegang te krijgen op sandboxapicem.com
    headers = {
        "content-type": "application/json",
        "X-Auth-Token": ticket
        }
    resp = requests.get(api_url, headers=headers, verify=False)
    print("Status of / host request: ", resp.status_code)

    if resp.status_code != 200:
        raise Exception("Status code does not equal 200. Response text: " + resp.text)
    response_json = resp.json()
    # We zullen een list moeten gebruiken om daarin items te gebruiken
    host_list=[]
    i = 0
    # Deze loop zorgt voor dat we een aantal items of parameters in onze tabel stoppen
    for item in response_json["response"]:
        i += 1
        host = [
                i,
                item["vlanId"],
                item["hostType"],
                item["hostIp"],
                item["hostMac"]]
        host_list.append( host )
    # de variabel toont de namen van de rijen
    table_header = [
                    "Number",
                    "VlanId",
                    "Type",
                    "IP",
                    "hostMac"
                    ]
    # Ons tabel wordt geprint
    print (tabulate (host_list, table_header) )


#============================
# Script 2. Gegevens van de host inventory in een tabel vormen
#============================

#Deze functie toont de apparaten van devnetsbx-netacad-apicem-3
def print_devices():
    
    api_url = "https://devnetsbx-netacad-apicem-3.cisco.com/api/v1/network-device"

    ticket = get_ticket()
    
    headers = {
        "content-type": "application/json",
        "X-Auth-Token": ticket
        }

    resp = requests.get(api_url, headers=headers, verify=False)
    print("Status of / host request: ", resp.status_code)

    if resp.status_code != 200:
        raise Exception("Status code does not equal 200. Response text: " + resp.text)
    response_json = resp.json()

    devices_list=[]

    i = 0
    for item in response_json["response"]:
        i += 1
        device = [
                i,
                 item["serialNumber"],
                item["type"],
                item["family"],
                item["series"]
                ]

        devices_list.append( device )

    table_header = [
                    "Number",
                    "Serial"
                    "Type",
                    "Family",
                    "Series"
                    ]
    print (tabulate (devices_list, table_header) )

#============================
# Script 3. pad traceren van twee nodes
#============================

# De bedoeling van deze script is dat we een pad op de netwerk van onze sandbox gaan traceren door twee knooppunten en vormen in een tabel 
def path_trace():

    api_url = "https://devnetsbx-netacad-apicem-3.cisco.com/api/v1/flow-analysis"  
    ticket = get_ticket()    
    
    headers = headers = {
        "content-type": "application/json",
        "X-Auth-Token": ticket
        }
    
    # We vragen de gegevens terug van de vorige functies die wij gemaakt hebben
    print("\n\n De volgende host zijn: ")
    print_hosts()
    print("\n\n De volgende apparaten: ")
    print_devices()
    print("\n\n")
    
    # In deze while loop vragen gewoon achter een bron ip adres en het ip adres van onze bestemming.
    # Als alles is ingevuld dan stopt de loop. zo niet, dan wordt het nogmaals gevraagd tot dat alle inputs zijn ingevuld
    while True:
       
        s_ip = input("Geef de source hosts ip adres in a.u.b.: ")  
        d_ip = input("Geef de bestemming hosts ip adres in a.u.b.:")  
  

        if s_ip != "" or d_ip != "":
      
            path_data = {
                "sourceIP": s_ip,
                "destIP": d_ip
            }
          
            print("Source IP: " + s_ip)
            print("Destination IP: " + d_ip)

            break  
        else:
            print("\n\nYOU MUST ENTER IP ADDRESSES TO CONTINUE.\nUSE CTRL-C TO QUIT\n")
            continue  

   
    path = json.dumps(path_data)
    resp = requests.post(api_url, path, headers=headers, verify=False)

    #deze variabelen combineert de URL met de flowAnalysisId die we geretouneerd heeft
    resp_json = resp.json()
    flowAnalysisId = resp_json["response"]["flowAnalysisId"]
    print("FLOW ANALYSIS ID: ", flowAnalysisId)


    check_url = api_url + "/" + flowAnalysisId
    # We zullen nog eens controle uitvoeren met een while loop
    # De bedoeling van deze while loop is een controle op de status
    # De zolang we geen status niet op completed staat stopt de loop niet
    status = ""
    checks = 1  # Deze variabele is de checks. Bij iedere check wordt er opgeteld
    while status != "COMPLETED":
        r = requests.get(check_url, headers=headers, verify=False)
        response_json = r.json()
        status = response_json["response"]["request"]["status"]
        print("REQUEST STATUS: ", status)  
        time.sleep(1)
        if checks == 15:  # Als er 15 checks gebeurt zijn dan stopt de loop en krijgen we deze melding
            raise Exception("Number of status checks exceeds limit. Possible problem with Path Trace.!")
        elif status == "FAILED": #Als de status FAILED is dan gaat dan word de variabele checks opgeteld en gaat de loop gewoon weg verder
            raise Exception("Problem with Path Trace - FAILED!")
        checks += 1
        


    #Deze variabelen vraagt via een json element aan achter de volgende elementen
    path_source = response_json["response"]["request"]["sourceIP"]
    path_dest = response_json["response"]["request"]["destIP"]
    networkElementsInfo = response_json["response"]["networkElementsInfo"]

    all_devices = []     # een list variablel wordt gemaakt om een device en host gemaakt.
    device_no = 1  # deze variabelen geeft gewoon een nummer op een apparaat via een for loop

    # Deze loop zorgt dat we de volgende gegevens kunnen aanspreken op het level van networkelementen
    for networkElement in networkElementsInfo:
        # kijkt of het apparaat een naam heeft of niet
        if "name" not in networkElement:  
            name = "Unnamed Host"
            ip = networkElement["ip"]
            egressInterfaceName = "UNKNOWN"
            ingressInterfaceName = "UNKNOWN"
        # als het volgend apparaat een naam heeft dan wordt de volgende gegevens opgevraagd
        else:  
            name = networkElement["name"]
            ip = networkElement["ip"]
            if "egressInterface" in networkElement:  # not all intermediary devices have ingress and egress interfaces
                egressInterfaceName = networkElement["egressInterface"]["physicalInterface"]["name"]
            else:
                egressInterfaceName = "UNKNOWN"

            if "ingressInterface" in networkElement:
                ingressInterfaceName = networkElement["ingressInterface"]["physicalInterface"]["name"]
            else:
                ingressInterfaceName = "UNKNOWN"
        
        device = [
                    device_no,
                    name,
                    ip,
                    ingressInterfaceName,
                    egressInterfaceName
                 ]
        all_devices.append(device)
        device_no += 1  

    print("Path trace: \n Source: ", path_source, "\n Destination: ", path_dest)  
    print("List of devices on path:")
    table_header = [
                    "Item",
                    "Name",
                    "IP",
                    "Ingress Int",
                    "Egress Int"
                   ]
    print( tabulate(all_devices, table_header) )  




