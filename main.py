import requests
import json
import urllib.parse
import flask
from flask import request
from cards import createIncidentCards


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

textMessage = "Thanks for using **ServiceNow Bot!**<br />\
                In order to use ServiceNow Bot you can issue following commands to interact with it<br />\
                ```@ServiceNowBot help```              -   you will receive the help information<br />\
                ```@ServiceNowBot update <comments>``` -   this will update the ServiceNow ticket with comments<br />\
                ```@ServiceNowBot create incident```   -   this will allow you to open a new ServiceNow incident."

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
    elif responseAccessToken.status_code == 401:
        responseRefreshToken = getRefreshToken(clientId, clientSecret, username, password, url)
        responseRefreshToken = json.loads(responseRefreshToken.text)
    return responseAccessToken


def getIncidentSysId(accessToken, incidentNumber, url):

    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken}
    url = url + "/api/now/table/incident?sysparm_limit=1&number=" + incidentNumber
    response = requests.get(url, headers=headers, verify=False)
    return response


def getUserSysId(email, url):
    #email = "marcin.koszykowski@aon.com"
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
    return response


def putWorkComment(accessToken, incidentSysId, url, additionalComment):

    accessToken = "Bearer " + accessToken
    headers = {
        'Authorization': accessToken,
        'Content-Type': 'application/json'}
    data = "{\"comments\" :\"" + additionalComment + "\"}"
    url = url + "/api/now/table/incident/" + incidentSysId
    response = requests.put(url, headers=headers, data=data, verify=False)
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
    return response



def updateCommand(responseMessage, messageText, botToken, webexUrl, getMessageDetailsUrl, getRoomDetailsUrl):
    comment = "User " + responseMessage["personEmail"] + " has added a comment: " + responseMessage["text"].split("Bot update")[1]
    roomId = responseMessage["roomId"]
    response = getWebexItemDetails(botToken, roomId, webexUrl, getRoomDetailsUrl)
    response = json.loads(response.text)
    incidentNumber = response["title"].split(":")[0]
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    print(accessToken)
    responseIncidentSysId = getIncidentSysId(accessToken, incidentNumber, url)
    responseIncidentSysId = json.loads(responseIncidentSysId.text)
    responseWorkComment = putWorkComment(accessToken, responseIncidentSysId["result"][0]["sys_id"], url, comment)
    return responseWorkComment


def createIncidentCommand():
    return
#responseRefreshToken = getRefreshToken(clientId, clientSecret, username, password, url)
#responseRefreshToken = json.loads(responseRefreshToken.text)
#print(responseRefreshToken)

@app.route('/api/v1/resources/webhook', methods=['POST'])
def webhook():
    req = request.json
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getMessageDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    print(responseMessage)
    if responseMessage["personEmail"] == "ServiceNowTest@webex.bot":
        return "this is a message sent from a ServiceNowBot itself - ignoring."
    if "ServiceNowBot" in responseMessage["text"]:
        messageText = responseMessage["text"].split("ServiceNowBot ")[1]
    else:
        messageText = responseMessage["text"]
    messageCommand = messageText.split(" ")[0]

    if messageCommand == "update" and responseMessage["personEmail"] != "ServiceNowTest@webex.bot":
        print(messageCommand)
        responseWorkComment = updateCommand(responseMessage, messageText, botToken, webexUrl, getMessageDetailsUrl, getRoomDetailsUrl)
        return "Update command to incident has been issued."
    elif (messageCommand == "help" or messageCommand == "-help" or messageCommand == "?") and responseMessage["personEmail"] != "ServiceNowTest@webex.bot":
        responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
        return "Message posted to Webex space."
    elif messageCommand == "create" and messageText.split(" ")[1] == "incident":
        responsegetUserSysId = getUserSysId(responseMessage["personEmail"], url)
        responsegetUserSysId = json.loads(responsegetUserSysId.text)
        if responsegetUserSysId["result"]:
            print(responsegetUserSysId["result"][0]["sys_id"])
            textMessage = "This is a Webex card message."
            responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage, createIncidentCards())
        else:
            responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseMessage["personEmail"] + " is not available at ServiceNow. Please use account existing in Service Now.")
            return "The account associated with your email: " + responseMessage["personEmail"] + " is not available at ServiceNow. Please use account existing in Service Now."
    else:
        responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please use the ```@ServiceNowBot``` help to list available commands.")

    return "good"

@app.route('/api/v1/resources/webhook/cards', methods=['POST'])
def cards():
    req = request.json
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getAttachmentDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    print(responseMessage)
    responseGetPersonDetails = getWebexItemDetails(botToken, responseMessage["personId"], webexUrl, getPersonDetailsUrl)
    responseGetPersonDetails = json.loads(responseGetPersonDetails.text)
    responseGetUserSysId = getUserSysId(responseGetPersonDetails["emails"][0], url)
    responseGetUserSysId = json.loads(responseGetUserSysId.text)
    print(responseGetUserSysId)
    if not responseGetUserSysId["result"]:
        deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
        responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseGetPersonDetails["emails"][0] + " is not available at ServiceNow. Please use account existing in Service Now.")
        return "The account associated with your email: " + responseGetPersonDetails["emails"][0] + " is not available at ServiceNow. Please use account existing in Service Now."        
    textMessage = "Thank you for submitting an incident via ServiceNow Bot. Please standy as your incident is created."
    responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
    responseCreateIncident = createIncident(responseGetUserSysId["result"][0]["sys_id"], url, responseMessage["inputs"]["shortDescription"], responseMessage["inputs"]["fullDescription"], responseMessage["inputs"]["urgency"], responseMessage["inputs"]["impact"], responseMessage["inputs"]["checkbox"])
    responseCreateIncident = json.loads(responseCreateIncident.text)
    print(responseCreateIncident)
    textMessage = "Please be advised that the Incident: " + responseCreateIncident["result"]["number"] + " has been created. Please use the Webex space or the following link to track your newly created Incident: [LINK](https://dev70378.service-now.com/sp?id=ticket&is_new_order=true&table=incident&sys_id=" + responseCreateIncident["result"]["sys_id"] + ")"
    responsePostWebexMessage = postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)

    

    return "good"

app.run(host='0.0.0.0', port=5002, ssl_context='adhoc')
