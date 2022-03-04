import requests
import json
import urllib.parse
import flask
import logging
from flask import request
from cards import createIncidentCards

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', filename='./WebexBotEndpoint.log', filemode='w')
clientId = "ddbddd39a4b10110bebfa2dcd57241bc"
clientSecret = "MiyNOb<iKU"
username = "webex.bot"
password = "koszyK)0"
## temp value ##
refreshToken = "nVaWXXFFUGeUDM4dgMT2HvMWFOHLZGnJnmJSrcWSXHzeuBgpgkgBBHUFwzELCWYZKK5yVhwCPonjBaCHupLR2w"
##
url = "https://dev70378.service-now.com"
additionalComment = "User X added a comment via Webex application: Yet another comment!!!"

webexUrl = "https://webexapis.com/"
getMessageDetailsUrl = "v1/messages/"
getRoomDetailsUrl = "v1/rooms/"
getAttachmentDetailsUrl = "v1/attachment/actions/"
getPersonDetailsUrl = "v1/people/"

botToken = "OTI5NGY2OTUtNzhhYS00ZDVmLTg0ODktZDAxMjQ3NDM4ZTFiYmEyMGI4MTAtNGQx_PF84_3889a4c9-3174-445a-b3b8-b0528d045fab"
webexAppId = "Y2lzY29zcGFyazovL3VzL0FQUExJQ0FUSU9OL0MzMmM4MDc3NDBjNmU3ZGYxMWRhZjE2ZjIyOGRmNjI4YmJjYTQ5YmE1MmZlY2JiMmM3ZDUxNWNiNGEwY2M5MWFh"

helpMessageGroup = "This is a help message for **ServiceNow Bot!**<br />\
                In order to use ServiceNow Bot you can issue following commands to interact with it.<br />\
                ```@ServiceNowBot help```              -   you will receive the help information<br />\
                ```@ServiceNowBot update <comments>``` -   this will update the ServiceNow ticket with comments<br />\
                ```@ServiceNowBot create incident```   -   this will allow you to open a new ServiceNow incident."
                
helpMessageDirect = "This is a help message for **ServiceNow Bot!**<br />\
                In order to use ServiceNow Bot you can issue following commands to interact with it<br />\
                ```help```              -   you will receive the help information<br />\
                ```create incident```   -   this will allow you to open a new ServiceNow incident."

app = flask.Flask(__name__)

def getRefreshToken(clientId, clientSecret, username, password, url):

    data = {
                'grant_type': 'password',
                'client_id': clientId,
                'client_secret': clientSecret,
                'username': username,
                'password': password}
    url = url + "/oauth_token.do"
    response = requests.post(url, data=data, verify=False)
    logging.debug("[getRefreshToken]### RETRIEVED succesfully refresh token and access token.")
    return response


def getAccessToken(clientId, clientSecret, refreshToken, url):

    data = {
                'grant_type': 'refresh_token',
                'client_id': clientId,
                'client_secret': clientSecret,
                'refresh_token': refreshToken}
    url = url + "/oauth_token.do"
    responseAccessToken = requests.post(url, data=data, verify=False)
    if responseAccessToken.status_code == 200:
        responseAccessToken = json.loads(responseAccessToken.text)
        logging.debug("[getAccessToken]### RETRIEVED succesfully access token.")
    elif responseAccessToken.status_code == 401:
        responseRefreshToken = getRefreshToken(clientId, clientSecret, username, password, url)
        responseRefreshToken = json.loads(responseRefreshToken.text)
        logging.debug("[getAccessToken]### RETRIEVED succesfully access token through refresh token.")
    return responseAccessToken


def getIncidentSysId(accessToken, incidentNumber, url):

    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken}
    url = url + "/api/now/table/incident?sysparm_limit=1&number=" + incidentNumber
    response = requests.get(url, headers=headers, verify=False)
    return response


def getUserSysId(email, url):
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken}
    query = {"sysparm_query": "email=" + email, "sysparm_display_value": "sys_id", "sysparm_limit": 1}
    url = url + "/api/now/table/sys_user?" + urllib.parse.urlencode(query)
    response = requests.get(url, headers=headers, verify=False)
    return response

def createIncident(callerId, url, shortDescription, fullDescription="", urgency=3, impact=3, checkbox=True):
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Content-Type': 'application/json'}
    data = {'short_description': shortDescription,
            'description': fullDescription,
            'urgency': urgency,
            'impact': impact,
            'caller_id': callerId,
            'x_773797_webex_dem_wbxcheckbox': checkbox}
    data = json.dumps(data)
    url = url + "/api/now/table/incident"
    response = requests.post(url, headers=headers, data=data, verify=False)
    logging.debug("[createIncident]### CREATED an incident in ServiceNow: \"{}\" with sys_id: {}.".format(json.loads(response.text)["result"]["number"], json.loads(response.text)["result"]["sys_id"]))
    return response


def putWorkComment(accessToken, incidentSysId, url, additionalComment):

    accessToken = "Bearer " + accessToken
    headers = {
        'Authorization': accessToken,
        'Content-Type': 'application/json'}
    data = "{\"comments\" :\"" + additionalComment + "\"}"
    url = url + "/api/now/table/incident/" + incidentSysId
    response = requests.put(url, headers=headers, data=data, verify=False)
    logging.debug("[putWorkComment]### ADDED a message: \"{}\" to ServiceNow incident (sys_id): {}.".format(additionalComment, incidentSysId))
    return response


def getWebexItemDetails(botToken, messageId, webexUrl, itemSpecificUrl):
    botToken = "Bearer " + botToken
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json'}
    url = webexUrl + itemSpecificUrl + messageId
    response = requests.get(url, headers=headers, verify=False)
    return response


def postWebexMessage(botToken, spaceId, webexUrl, itemSpecificUrl, textMessage, attachments = []):
    botToken = "Bearer " + botToken
    textMarkdown = textMessage
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json',
        'Content-Type': 'application/json'}
    data = "{\"roomId\" : \"" + spaceId + "\",\"text\" : \"" + textMessage + "\",\"markdown\" : \"" + textMarkdown + "\",\"attachments\" : " + str(attachments) + "}"
    url  = webexUrl + itemSpecificUrl
    logging.debug("[postWebexMessage]### SENT a message: \"{}\".".format(textMessage))
    response = requests.post(url, headers=headers, data=data, verify=False)
    
    return response

def deleteWebexMessage(botToken, messageId, webexUrl, itemSpecificUrl):
    botToken = "Bearer " + botToken
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json',
        'Content-Type': 'application/json'}
    url  = webexUrl + itemSpecificUrl + messageId
    response = requests.delete(url, headers=headers, verify=False)
    logging.debug("[deleteWebexMessage]### DELETED a message with a messageId: \"{}\".".format(messageId))
    return response



def updateCommand(responseMessage, messageText, botToken, webexUrl, getMessageDetailsUrl, getRoomDetailsUrl):
    comment = "User " + responseMessage["personEmail"] + " has added a comment: " + responseMessage["text"].split("Bot update")[1]
    roomId = responseMessage["roomId"]
    response = getWebexItemDetails(botToken, roomId, webexUrl, getRoomDetailsUrl)
    response = json.loads(response.text)
    incidentNumber = response["title"].split(":")[0]
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    responseIncidentSysId = getIncidentSysId(accessToken, incidentNumber, url)
    responseIncidentSysId = json.loads(responseIncidentSysId.text)
    responseWorkComment = putWorkComment(accessToken, responseIncidentSysId["result"][0]["sys_id"], url, comment)
    return responseWorkComment


@app.route('/api/v1/resources/webhook', methods=['POST'])
def webhook():

    req = request.json
    if req["data"]["personEmail"] == "ServiceNowTest@webex.bot":
        return ('Message received', 200)
    elif req["appId"] != webexAppId:
        logging.error("RECEIVED incorrect appId")
        return ('Incorrect appId', 401)
    else:
        logging.debug("RECEIVED correct appId")
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getMessageDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    logging.debug("RECEIVED a message: \"{}\" from user: {}.".format(responseMessage["text"], responseMessage["personEmail"]))
    
    responseMessageList = responseMessage["text"].split(" ")
    if responseMessageList[0] == "ServiceNowBot":
        responseMessageList.pop(0)
    messageCommand = responseMessageList[0]
    textMessage = ' '.join(responseMessageList)

    if messageCommand == "help" or messageCommand == "-h" or messageCommand == "?" or messageCommand == "/help":
        if responseMessage["roomType"] == "direct":
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, helpMessageDirect)
        elif responseMessage["roomType"] == "group":
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, helpMessageGroup)
        return ('Message received', 200)
    elif len(responseMessageList) >= 2:
        if messageCommand == "update":
            responseWorkComment = updateCommand(responseMessage, textMessage, botToken, webexUrl, getMessageDetailsUrl, getRoomDetailsUrl)
            if responseWorkComment.status_code == 200:
                responseWorkComment = json.loads(responseWorkComment.text)
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "Your comment has been added to the incident: ```" + responseWorkComment["result"]["number"] + "```.")
            return ('Message received', 200)
        elif messageCommand == "create":
            responsegetUserSysId = getUserSysId(responseMessage["personEmail"], url)
            responsegetUserSysId = json.loads(responsegetUserSysId.text)
            if responsegetUserSysId["result"]:
                print(responsegetUserSysId["result"][0]["sys_id"])
                textMessage = "This is a Webex card message."
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage, createIncidentCards())
            else:
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseMessage["personEmail"] + " is not available at ServiceNow. Please use account existing in Service Now.")
                return ('Message received', 200)
    else:
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please use the ```@ServiceNowBot``` help to list available commands.")
    return ('Message received', 200)

@app.route('/api/v1/resources/webhook/cards', methods=['POST'])
def cards():
    req = request.json
    if req["appId"] != webexAppId:
        logging.error("RECEIVED incorrect appId")
        return ('Incorrect appId', 401)
    else: 
        logging.debug("RECEIVED correct appId")
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getAttachmentDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    print(responseMessage)
    responseGetPersonDetails = getWebexItemDetails(botToken, responseMessage["personId"], webexUrl, getPersonDetailsUrl)
    responseGetPersonDetails = json.loads(responseGetPersonDetails.text)
    responseGetUserSysId = getUserSysId(responseGetPersonDetails["emails"][0], url)
    responseGetUserSysId = json.loads(responseGetUserSysId.text)
    if not responseGetUserSysId["result"]:
        deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseGetPersonDetails["emails"][0] + " is not available at ServiceNow. Please use account existing in Service Now.")
        return ('Card received', 200)
    if len(responseMessage["inputs"]["shortDescription"]) == 0:
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "In order to submit an incident please make sure that at least short description is filled in a card..")
        deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
        return ('Card received', 200)
    textMessage = "Thank you for submitting an incident via ServiceNow Bot. Please standy as your incident is created."
    postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
    if "\n" in responseMessage["inputs"]["fullDescription"]:
        responseMessage["inputs"]["fullDescription"] = responseMessage["inputs"]["fullDescription"].replace("\n"," ")
    responseCreateIncident = createIncident(responseGetUserSysId["result"][0]["sys_id"], url, responseMessage["inputs"]["shortDescription"], responseMessage["inputs"]["fullDescription"], responseMessage["inputs"]["urgency"], responseMessage["inputs"]["impact"], responseMessage["inputs"]["checkbox"])
    responseCreateIncident = json.loads(responseCreateIncident.text)
    textMessage = "Please be advised that the Incident: " + responseCreateIncident["result"]["number"] + " has been created. Please use the Webex space or the following link to track your newly created Incident: [LINK](https://dev70378.service-now.com/sp?id=ticket&is_new_order=true&table=incident&sys_id=" + responseCreateIncident["result"]["sys_id"] + ")"
    postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    return ('Card received', 200)

app.run(host='0.0.0.0', port=5002, ssl_context='adhoc')
