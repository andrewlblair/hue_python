import json
import requests
import os.path

##FUNC DEF

def firstTime():
    
      lights= requests.get("https://www.meethue.com/api/nupnp")
      js1= lights.json()
      
      bridgeIP = [index["internalipaddress"] for index in js1]
      
      bridgeIP= ",".join(bridgeIP)
      
      baseUsername= "http://%s/api" % bridgeIP

      success=False
      while success==False:
        try:
          jsonFirst= '{"devicetype":"my_hue_app#andrewspc"}'
          username= requests.post(baseUsername, jsonFirst)
          js2=username.json()
          username = [index['success']['username'] for index in js2]
          success=True
        except KeyError:
          bridgeNot = input("Please press the link button on your Phillips Hue Bridge. Press any key once you have done this.")
      
      username= ",".join(username)
      persist= "notfirst"
      dump = [{
              "bridge_ip" : bridgeIP,
              "username" : username,
              "persist" : persist
              }]
      f = open("hueforpc.json", "w")
      json.dump(dump, f)
      f.close()

def connect(a):

    login = [index["username"] for index in a]
    bridgeIP = [index["bridge_ip"] for index in a]
    
    login = ",".join(login)
    bridgeIP = ",".join(bridgeIP)

    get_address = "http://%s/api/%s/lights" % (bridgeIP, login) 
    return get_address

def getLights(address):
    lights = requests.get(address)
    js= lights.json()
    return js

def humanList(js):

    lights= [index + " - " + js[index]["name"] for index in js]
    
    temp = ""
    for i in range(len(lights),0,-1):
      for j in range(0,i-1):
        if int(lights[j][0:2])>int(lights[j+1][0:2]):
          temp=lights[j]
          lights[j]=lights[j+1]
          lights[j+1]=temp

    return lights

def isNumber(msg):
    valid=False
    while valid==False:
        try:
            value=int(input(msg)) 
        except ValueError:
            print("That is not a number. Please try again")
        else:
            valid=True
    return value

def getValue(msg,low,high):
    valid=False
    while valid==False:
        value=isNumber(msg)
        if value<low or value>high:
            print("Invalid number. Please try again")
        else:
            valid = True
    return value


def setStateMsg(light):
      valid=False
      while valid==False:
            valid=True
            
            choice = input("On, Off, Brightness, Temperature or Color? (Input On,Off,B,T,C")

            if choice.lower()=="on":
              js = '{"on": true}'
            elif choice.lower()=="off":
              js = '{"on": false}'
            elif choice.lower()=="t" and light=="Extended color light" or light=="Color temperature light":
              value = getValue("Enter a temperature (between 153 and 454)",153,454)
              js = '{"on": true, "ct": %s}' % value
            elif choice.lower()=="c" and light=="Extended color light":
              value = getValue("Enter a color (between 0 and 65535)",0,65535)
              js = '{"on": true, "hue": %s}' % value
            elif choice.lower()=="b":
              value = getValue("Enter brightness (between 1 and 254)",1,254)
              js = '{"on": true, "bri": %s}' % value
            else:
                  print("Oops, the light you have selected cannot control that attribute. Please try again")
                  valid=False

      return js

def lightsChange(address,info):
    r = requests.put(address,info)
    if r.status_code==200:
        print("Success!")
    else:
        print("Error " + r.status_code)

def progExit():
    value=input("Do you want to exit? Y/N")
    if value.lower() == "y":
        return False
    else:
        return True


      
##MAIN

if os.path.isfile("hueforpc.json")==False:
    firstTime()
    
f = open("hueforpc.json", "r")
data = json.loads(f.read())
f.close()

hubAddress = connect(data)
lightsJS = getLights(hubAddress)
ordLights = humanList(lightsJS)

x=True
while x:
    print('\n'.join(ordLights),'\n')
    
    lightChoice = isNumber("What light would you like to control?")
    lightAddress = hubAddress + "/%s/state" % lightChoice

    try:
        typeLight = lightsJS[str(lightChoice)]["type"]
    except KeyError:
        print("This light does not exist. Please try again\n")
        continue
    
    state = setStateMsg(typeLight)

    lightsChange(lightAddress,state)

    x = progExit()
