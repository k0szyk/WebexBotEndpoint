import requests
import json
import flask
from flask import request

clientId = "ddbddd39a4b10110bebfa2dcd57241bc"
clientSecret = "MiyNOb<iKU"
username = "webex.bot"
password = "koszyK)0"
## temp value ##
refreshToken = "nVaWXXFFUGeUDM4dgMT2HvMWFOHLZGnJnmJSrcWSXHzeuBgpgkgBBHUFwzELCWYZKK5yVhwCPonjBaCHupLR2w"
##
url = "https://dev70378.service-now.com"
additionalComment = "User X added a comment via Webex application: Yet another comment!!!"

webexUrl = "https://webexapis.com"

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
    response = requests.post(url, data=data, verify=False)
    return response


def getIncidentSysId(accessToken, incidentNumber, url):

    accessToken = "Bearer " + accessToken
    headers = {
        'Authorization': accessToken}
    url = url + "/api/now/table/incident?sysparm_limit=1&number=INC0010050"
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
    return response


def getWebexItemDetails(botToken, messageId, webexUrl, itemSpecificUrl):
    botToken = "Bearer " + botToken
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json'}
    url = webexUrl + itemSpecificUrl + messageId
    response = requests.get(url, headers=headers, verify=False)
    return response

#responseRefreshToken = getRefreshToken(clientId, clientSecret, username, password, url)
#responseRefreshToken = json.loads(responseRefreshToken.text)
#print(responseRefreshToken)

@app.route('/api/v1/resources/webhook', methods=['POST'])
def webhook():
    
    webexUrl = "https://webexapis.com/"
    getMessageDetailsUrl = "v1/messages/"
    getRoomDetailsUrl = "v1/rooms/"
    botToken = "OTI5NGY2OTUtNzhhYS00ZDVmLTg0ODktZDAxMjQ3NDM4ZTFiYmEyMGI4MTAtNGQx_PF84_3889a4c9-3174-445a-b3b8-b0528d045fab"

    req = request.json
    responseMessage = getWebexItemDetails(botToken, req["data"]["id"], webexUrl, getMessageDetailsUrl)
    responseMessage = json.loads(responseMessage.text)
    comment = "User " + responseMessage["personEmail"] + " has added a comment: " + responseMessage["text"].split("Bot")[1]
    roomId = responseMessage["roomId"]
    response = getWebexItemDetails(botToken, roomId, webexUrl, getRoomDetailsUrl)
    response = json.loads(response.text)
    incidentNumber = response["title"].split(":")[0]

    responseAccessToken = getAccessToken(clientId, clientSecret, refreshToken, url)
    responseAccessToken = json.loads(responseAccessToken.text)
    responseIncidentSysId = getIncidentSysId(responseAccessToken["access_token"], incidentNumber, url)
    responseIncidentSysId = json.loads(responseIncidentSysId.text)
    responseWorkComment = putWorkComment(responseAccessToken["access_token"], responseIncidentSysId["result"][0]["sys_id"], url, comment)
    return responseWorkComment.text

app.run(host='0.0.0.0', port=5002, ssl_context='adhoc')
