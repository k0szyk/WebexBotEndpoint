import requests
import json
import urllib.parse
import flask
import logging
import time
from flask import request
from cards import createIncidentCard, createWelcomeCard, previousIncidentsCard, createFeedbackCard
from domains import domains

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', filename='./WebexBotEndpoint.log', filemode='a')
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
webexOrgId = "Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi8xZTAwZTkyMi01ZWM2LTRmM2ItOTZhMy0zNDhkOTEyODhkNmQ"
webexAppId = "Y2lzY29zcGFyazovL3VzL0FQUExJQ0FUSU9OL0MzMmM4MDc3NDBjNmU3ZGYxMWRhZjE2ZjIyOGRmNjI4YmJjYTQ5YmE1MmZlY2JiMmM3ZDUxNWNiNGEwY2M5MWFh"
feedbackSpaceId = "Y2lzY29zcGFyazovL3VzL1JPT00vM2MxNTc3MzAtOWZhNi0xMWVjLTlmMzUtNmQyY2I5YWY5MmRh"
botEmailAddress = "ServiceNowTest@webex.bot"

helpMessageGroup = "This is a help message for **ServiceNow Bot!**<br />\
                In order to use ServiceNow Bot you can issue following commands to interact with it.<br />\
                ```@ServiceNowBot help``` - help information.<br />\
                ```@ServiceNowBot update <comments>``` - updates the ServiceNow ticket with comments.<br />\
                ```@ServiceNowBot create incident``` - opens a new ServiceNow incident.<br />\
                ```@ServiceNowBot assign``` - assigns a new ServiceNow incident to yourself (your account need to have correct priviliges).<br />\
                ```@ServiceNowBot assign <email_address>``` - assigns a new ServiceNow incident to specified person (your account need to have correct priviliges).<br />"

markdownDisabledMessage = "This message is intended to be an interactive Webex card. If you do not see the interactive card it is most likely that your Webex application has the markdown option disabled."

incidentStates = {"1": "New", "2": "In Progress", "3": "On Hold", "4": "Canceled", "5": "Unknown", "6": "Resolved", "7": "Closed", "8": "Unknown", "9": "Unknown"}

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
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
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


def updateIncident(url, sysId, updatedAttributes):
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = updatedAttributes
    data = json.dumps(data)
    url = url + "/api/now/table/incident/" + sysId
    response = requests.patch(url, headers=headers, data=data, verify=False)
    logging.debug("[createIncident]### UPDATED an incident in ServiceNow: \"{}\" with sys_id: {}.".format(json.loads(response.text)["result"]["number"], json.loads(response.text)["result"]["sys_id"]))
    return response


def getPreviousIncidents(url, userSysId, count):
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    query = {"sysparm_query": "caller_id=" + userSysId + "^ORDERBYDESCsys_created_on",
             "sysparm_display_value": "sys_created_on,caller_id,short_description,sys_id,x_773797_webex_dem_spaceid,state,number", 
             "sysparm_limit": count}
    url = url + "/api/now/table/incident?" + urllib.parse.urlencode(query)
    response = requests.get(url, headers=headers, verify=False)
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
    #logging.debug("[postWebexMessage]### RECEIVED a response: \"{}\".".format(response.text))
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


def updateCommand(responseMessage, botToken, webexUrl, getRoomDetailsUrl):
    comment = "User " + responseMessage["personEmail"] + " has added a comment: " + responseMessage["text"].split("Bot update")[1]
    roomId = responseMessage["roomId"]
    response = getWebexItemDetails(botToken, roomId, webexUrl, getRoomDetailsUrl)
    response = json.loads(response.text)
    incidentNumber = response["title"].split(" [")[0]
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    responseIncidentSysId = getIncidentSysId(accessToken, incidentNumber, url)
    responseIncidentSysId = json.loads(responseIncidentSysId.text)
    responseWorkComment = putWorkComment(accessToken, responseIncidentSysId["result"][0]["sys_id"], url, comment)
    return responseWorkComment


def assignIncident(responseMessage, botToken, webexUrl, getRoomDetailsUrl, assignee):
    assignee = {"assigned_to": assignee}
    roomId = responseMessage["roomId"]
    response = getWebexItemDetails(botToken, roomId, webexUrl, getRoomDetailsUrl)
    response = json.loads(response.text)
    incidentNumber = response["title"].split(" [")[0]
    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    accessToken = responseAccessToken["access_token"]
    responseIncidentSysId = getIncidentSysId(accessToken, incidentNumber, url)
    responseIncidentSysId = json.loads(responseIncidentSysId.text)
    responseUpdateIncident = updateIncident(url, responseIncidentSysId["result"][0]["sys_id"], assignee)
    return responseUpdateIncident


def createIncidentFlow(responseMessage):
    responseGetPersonDetails = getWebexItemDetails(botToken, responseMessage["personId"], webexUrl, getPersonDetailsUrl)
    responseGetPersonDetails = json.loads(responseGetPersonDetails.text)
    responseGetUserSysId = getUserSysId(responseGetPersonDetails["emails"][0], url)
    responseGetUserSysId = json.loads(responseGetUserSysId.text)
    if not responseGetUserSysId["result"]:
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseGetPersonDetails["emails"][0] + " is not available at ServiceNow. Please use an account existing in Service Now.")
        return ('Card received', 200)
    if len(responseMessage["inputs"]["shortDescription"]) == 0:
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "In order to submit an incident please make sure that at least short description is filled in a card..")
        return ('Card received', 200)
    textMessage = "Thank you for submitting an incident via ServiceNow Bot. Please standy as your incident is created."
    postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
    if "\n" in responseMessage["inputs"]["fullDescription"]:
        responseMessage["inputs"]["fullDescription"] = responseMessage["inputs"]["fullDescription"].replace("\n"," ")
    responseCreateIncident = createIncident(responseGetUserSysId["result"][0]["sys_id"], url, responseMessage["inputs"]["shortDescription"], responseMessage["inputs"]["fullDescription"], responseMessage["inputs"]["urgency"], responseMessage["inputs"]["checkbox"])
    responseCreateIncident = json.loads(responseCreateIncident.text)
    textMessage = "Please be advised that the Incident: ```" + responseCreateIncident["result"]["number"] + "``` has been created. Please use the **Webex space** or the following link to track your newly created Incident: [LINK](https://dev70378.service-now.com/sp?id=ticket&is_new_order=true&table=incident&sys_id=" + responseCreateIncident["result"]["sys_id"] + ")"
    postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    return


@app.route('/api/v1/resources/webhook', methods=['POST'])
def webhook():

    req = request.json
    if req["data"]["personEmail"] == botEmailAddress:
        logging.debug("RECEIVED a message from ServiceNow bot itself. The message was sent from: {}".format(req["data"]["personEmail"]))
        return ('Message received', 200)
    elif req["appId"] != webexAppId:
        logging.error("RECEIVED incorrect webexAppId: {}".format(req["appId"]))
        logging.error("Full message: {}".format(req))
        return ('Incorrect orgId', 401)
    else:
        logging.debug("RECEIVED correct webexAppId: {}".format(req["appId"]))
    logging.debug("RECEIVED correct orgId: {}".format(req))
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getMessageDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    logging.debug("RECEIVED a message: \"{}\" from user: {}.".format(responseMessage["text"], responseMessage["personEmail"]))
    
    responseMessageList = " ".join(responseMessage["text"].split()).split(" ")
    if responseMessageList[0] == "ServiceNowBot":
        responseMessageList.pop(0)
    messageCommand = responseMessageList[0]
    logging.debug("RECEIVED a command message: {}".format(messageCommand))

    if messageCommand in ["help", "-h", "?", "/help", "start"]:
        if responseMessage["roomType"] == "direct":
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createWelcomeCard())
        elif responseMessage["roomType"] == "group":
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, helpMessageGroup)
        return ('Message received', 200)
    elif messageCommand == "assign" and responseMessage["roomType"] == "group":
        if len(responseMessageList) == 2 and "@" in responseMessageList[1]:
            responsegetUserSysId = getUserSysId(responseMessageList[1], url)
            responsegetUserSysId = json.loads(responsegetUserSysId.text)
            if responsegetUserSysId["result"]:
                responseAssignIncident = assignIncident(responseMessage, botToken, webexUrl, getRoomDetailsUrl, (responsegetUserSysId["result"][0]["sys_id"]))
                responseAssignIncident = json.loads(responseAssignIncident.text)
            else:
                logging.error("NOT CREATED and incident as the ServiceNow does not have this account available: {}.".format(responseMessageList[1]))
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The incident was not assigned. The provided email addres: {} is invalid. Please verify the email address.".format(responseMessageList[1]))
        elif len(responseMessageList) == 1:
            responsegetUserSysId = getUserSysId(responseMessage["personEmail"], url)
            responsegetUserSysId = json.loads(responsegetUserSysId.text)
            responseAssignIncident = assignIncident(responseMessage, botToken, webexUrl, getRoomDetailsUrl, (responsegetUserSysId["result"][0]["sys_id"]))
            responseAssignIncident = json.loads(responseAssignIncident.text)
        else:
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please use the ```@ServiceNowBot``` help to list available commands.")
    elif len(responseMessageList) >= 2:
        if messageCommand == "update" and responseMessage["roomType"] == "group":
            responseWorkComment = updateCommand(responseMessage, botToken, webexUrl, getRoomDetailsUrl)
            if responseWorkComment.status_code == 200:
                responseWorkComment = json.loads(responseWorkComment.text)
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "Your comment has been added to the incident: ```" + responseWorkComment["result"]["number"] + "```.")
            return ('Message received', 200)
        elif messageCommand == "create" and responseMessageList[1] == "incident":
            responsegetUserSysId = getUserSysId(responseMessage["personEmail"], url)
            responsegetUserSysId = json.loads(responsegetUserSysId.text)
            if responsegetUserSysId["result"]:
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createIncidentCard())
            else:
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseMessage["personEmail"] + " is not available at ServiceNow. Please use account existing in Service Now.")
                return ('Message received', 200)
        else:
            if responseMessage["roomType"] == "group":
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please use the ```@ServiceNowBot help``` to list available commands.")
            if responseMessage["roomType"] == "direct":
                postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please type in ```help``` to receive available options.")
    else:
        if responseMessage["roomType"] == "group":
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please use the ```@ServiceNowBot help``` to list available commands.")
        if responseMessage["roomType"] == "direct":
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "ServiceNow Bot has not recognized the command provided. Please type in ```help``` to receive available options.")

    return ('Message received', 200)


@app.route('/api/v1/resources/webhook/cards', methods=['POST'])
def cards():
    req = request.json
    logging.debug("RECEIVED correct webexAppId: {}".format(req))
    if req["appId"] != webexAppId:
        logging.error("RECEIVED incorrect webexAppId: {}".format(req["appId"]))
        logging.error("Full message: {}".format(req))
        return ('Incorrect orgId', 401)
    else:
        logging.debug("RECEIVED correct webexAppId: {}".format(req["appId"]))
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getAttachmentDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    logging.debug("RECEIVED the message regarding card submission. Flow type: {}".format(responseMessage["inputs"]["flow"]))
    responseGetPersonDetails = getWebexItemDetails(botToken, responseMessage["personId"], webexUrl, getPersonDetailsUrl)
    responseGetPersonDetails = json.loads(responseGetPersonDetails.text)
    deleteWebexMessage(botToken, responseMessage["messageId"], webexUrl, getMessageDetailsUrl)
    if responseMessage["inputs"]["flow"] == "createIncident":
        createIncidentFlow(responseMessage)
        time.sleep(3)
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createWelcomeCard())
    elif responseMessage["inputs"]["flow"] == "createIncidentCard":
        responsegetUserSysId = getUserSysId(responseGetPersonDetails["emails"][0], url)
        responsegetUserSysId = json.loads(responsegetUserSysId.text)
        if responsegetUserSysId["result"]:
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createIncidentCard())
        else:
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseGetPersonDetails["emails"][0] + " is not available at ServiceNow. Please use account existing in Service Now.")
            return ('Message received', 200)
    elif responseMessage["inputs"]["flow"] == "previousIncidents":
        responsegetUserSysId = getUserSysId(responseGetPersonDetails["emails"][0], url)
        responsegetUserSysId = json.loads(responsegetUserSysId.text)
        if responsegetUserSysId["result"]:
            responsGetPreviousIncidents = getPreviousIncidents(url, responsegetUserSysId["result"][0]["sys_id"], 5)
            responsGetPreviousIncidents = json.loads(responsGetPreviousIncidents.text)
            incidentList = []
            for incident in responsGetPreviousIncidents["result"]:
                incidentDict = {"number": incident["number"], "state": incidentStates[incident["state"]], "shortDescription": incident["short_description"], "spaceId": incident["x_773797_webex_dem_spaceid"], "sysId": incident["sys_id"]}
                incidentList.append(incidentDict)
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, previousIncidentsCard(incidentList, url))        
        else:
            postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "The account associated with your email: " + responseGetPersonDetails["emails"][0] + " is not available at ServiceNow. Please use account existing in Service Now.")
            return ('Message received', 200)
    elif responseMessage["inputs"]["flow"] == "feedback":
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createFeedbackCard())
    elif responseMessage["inputs"]["flow"] == "submitFeedback":
        print(responseMessage)
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, "Thanks for sharing your opinon with us.")
        time.sleep(3)
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createWelcomeCard())
        feedbackText = "User {} has shared feedback:<br /> ```{}``` ".format(responseGetPersonDetails["emails"][0], responseMessage["inputs"]["feedbackText"])
        responsePostWebexMessage = postWebexMessage(botToken, feedbackSpaceId, webexUrl, getMessageDetailsUrl, feedbackText)
        logging.debug("RECEIVED the response to sending a message: {}".format(responsePostWebexMessage.text))
    elif responseMessage["inputs"]["flow"] == "goBack":
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createWelcomeCard())
    else:
        textMessage = "This is embarrassing. ServiceNow bot encountered critical error. "
        postWebexMessage(botToken, responseMessage["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    return ('Card received', 200)


@app.route('/api/v1/resources/webhook/membership', methods=['POST'])
def membership():
    req = request.json
    if req["data"]["personEmail"] == botEmailAddress:
        logging.debug("RECEIVED a message from ServiceNow bot itself. The message was sent from: {}".format(req["data"]["personEmail"]))
        return ('Message received', 200)
    elif req["appId"] != webexAppId:
        logging.error("RECEIVED incorrect webexAppId: {}".format(req["appId"]))
        logging.error("Full message: {}".format(req))
        return ('Incorrect orgId', 401)
    else:
        logging.debug("RECEIVED correct webexAppId: {}".format(req["appId"]))
    #logging.debug("RECEIVED membership creation event: {}".format(req))
    responseGetWebexItemDetails = getWebexItemDetails(botToken, req["data"]["roomId"], webexUrl, getRoomDetailsUrl)
    responseGetWebexItemDetails = json.loads(responseGetWebexItemDetails.text)
    responseGetPersonDetails = getWebexItemDetails(botToken, responseGetWebexItemDetails["creatorId"], webexUrl, getPersonDetailsUrl)
    responseGetPersonDetails = json.loads(responseGetPersonDetails.text)
    logging.debug("RECEIVED room details: {}".format(responseGetWebexItemDetails))
    logging.debug("RECEIVED a notification about new space created with user: {} in a space type: {}.".format(responseGetPersonDetails["emails"][0], responseGetWebexItemDetails["type"]))
    emailDomain = responseGetPersonDetails["emails"][0].split("@")[1]
    if (emailDomain in domains() or emailDomain == "gmail.com") and responseGetWebexItemDetails["type"] == "direct":
        textMessage = "Welcome! **ServiceNow bot** is at your service. <br />Please take a look at the below options or type in help:"
        postWebexMessage(botToken, req["data"]["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
        responsePostWebexMessage = postWebexMessage(botToken, req["data"]["roomId"], webexUrl, getMessageDetailsUrl, markdownDisabledMessage, createWelcomeCard())
        print(responsePostWebexMessage)
        responsePostWebexMessage = json.loads(responsePostWebexMessage.text)
        logging.debug("RECEIVED the response to the createWelcomeCard: ".format(responsePostWebexMessage))
    elif responseGetWebexItemDetails["type"] == "direct":
        textMessage = "Unfortunately, your account is not part of the AON Webex organization. Please contact your IT Service Desk to resolve this issue."
        postWebexMessage(botToken, req["data"]["roomId"], webexUrl, getMessageDetailsUrl, textMessage)
    return ('Membership received', 200)

app.run(host='0.0.0.0', port=5002, ssl_context='adhoc')
