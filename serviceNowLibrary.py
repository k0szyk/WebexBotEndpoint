import requests
import json
import urllib.parse
import logging
import time
import connectDb

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', filename='./WebexBotEndpoint.log', filemode='a')

def getRefreshToken(clientId: str, clientSecret: str, url: str, username: str, password: str) -> dict:
    """
    Creates (POST) the refreshToken for ServiceNow OAuth2.
    
    :param clientId: String required for OAuth2 with ServiceNow. The auto-generated unique ID of the application. The instance uses the client ID when requesting an access token.
    :param clientSecret: String required for OAuth2 with ServiceNow. The shared secret string that both the instance and the client application or website use to authorize communications with one another. 
    :param url: ServiceNow instance URL.
    :param username: ServiceNow bot username at ServiceNow instance.
    :param password: ServiceNow bot password at ServiceNow instance. 
    :return: Dictionary with ServiceNow API response for the RefreshToken POST message.
    """
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


def getAccessToken(clientId: str, clientSecret: str, refreshToken: str, url: str, username: str, password: str) -> dict:
    """
    Creates (POST) the accessToken for ServiceNow OAuth2.
    
    :param clientId: String required for OAuth2 with ServiceNow. The auto-generated unique ID of the application. The instance uses the client ID when requesting an access token.
    :param clientSecret: String required for OAuth2 with ServiceNow. The shared secret string that both the instance and the client application or website use to authorize communications with one another. 
    :param url: ServiceNow instance URL.
    :param username: ServiceNow bot username at ServiceNow instance.
    :param password: ServiceNow bot password at ServiceNow instance. 
    :return: Dictionary with ServiceNow API response for the AccessToken POST message.
    """
    access_token = connectDb.connect("access_token", "value, expiry")
    logging.debug("[getAccessToken]### RETRIEVED access token table {}".format(access_token))
    for key in access_token:
        if int(access_token[key]) > int(time.time()):
            logging.debug("[getAccessToken]### Access Token is still valid. Expiry of current access token: {}, current time {}".format(int(access_token[key]), int(time.time())))
            return {"access_token": key, "refresh_token": refreshToken, 'scopte': 'useraccount', 'token_type': 'Bearer', 'expires_in': 1770}
    data = {
                'grant_type': 'refresh_token',
                'client_id': clientId,
                'client_secret': clientSecret,
                'refresh_token': refreshToken}
    url = url + "/oauth_token.do"
    responseAccessToken = requests.post(url, data=data, verify=False)
    if responseAccessToken.status_code == 200:
        ### Catching developer instance of ServiceNow in hibernated status.
        if "Instance Hibernating page" in responseAccessToken.text:
            logging.error("[getAccessToken]### ERROR: ServiceNow {} is hibernated at this moment.".format(url))
        responseAccessToken = json.loads(responseAccessToken.text)
        logging.debug("[getAccessToken]### RETRIEVED succesfully access token.")
        responseUpdateAccessToken = connectDb.updateAccessToken(1, responseAccessToken["access_token"], int(time.time()+1770))
        logging.debug("[getAccessToken]### Update database with access token.")
    elif responseAccessToken.status_code == 401:
        responseRefreshToken = getRefreshToken(clientId, clientSecret, username, password, url)
        responseRefreshToken = json.loads(responseRefreshToken.text)
        logging.debug("[getAccessToken]### RETRIEVED succesfully access token through refresh token.")
    return responseAccessToken


def getIncidentSysId(accessToken: str, incidentNumber: str, url: str) -> dict:
    """
    Gets (GET) the sys_id for incident from ServiceNow instance.
    
    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param incidentNumber: String with Incident number in format: "INCXXXXXXX" where X are digits representing an identifier in ServiceNow.
    :param url: ServiceNow instance URL.
    :return: Dictionary with ServiceNow API response for the GET Incident message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken}
    url = url + "/api/now/table/incident?sysparm_limit=1&number=" + incidentNumber
    response = requests.get(url, headers=headers, verify=False)
    response = json.loads(response.text)
    return response


def getUserSysId(accessToken: str, email: str, url: str) -> dict:
    """
    Gets (GET) the sys_id for the user from ServiceNow instance.
    
    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param email: String with email address of the ServiceNow user.
    :param url: ServiceNow instance URL.
    :return: Dictionary with ServiceNow API response for the GET sys_user message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken}
    query = {"sysparm_query": "email=" + email, "sysparm_display_value": "sys_id", "sysparm_limit": 1}
    url = url + "/api/now/table/sys_user?" + urllib.parse.urlencode(query)
    response = requests.get(url, headers=headers, verify=False)
    response = json.loads(response.text)
    return response


def createIncident(accessToken: str, callerId: str, url: str, shortDescription: str, fullDescription="", urgency=3, impact=3, checkbox=True) -> dict:
    """
    Creates (POST) the incident in ServiceNow instance.
    
    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param callerId: String with email address of the ServiceNow user.
    :param url: ServiceNow instance URL.
    :param shortDescription: String with short description of the incident.
    :param fullDescription: String with full description of the incident.
    :param urgency: Integer representing the level of urgency (optional).
    :param impact: Integer representing the level of impact (optional).
    :param checkbox: Boolean representing if the Incident will be opened with a Webex space.
    :return: Dictionary with ServiceNow API response for the POST incident message.
    """
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
    response = json.loads(response.text)
    logging.debug("[createIncident]### CREATED an incident in ServiceNow: \"{}\" with sys_id: {}.".format(response["result"]["number"], response["result"]["sys_id"]))
    return response


def updateIncident(accessToken: str, url: str, sysId: str, updatedAttributes: dict) -> dict:
    """
    Updates (PATCH) the incident in ServiceNow instance.
    
    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param url: ServiceNow instance URL.
    :param sysId: String which identifies the incident in ServiceNow.
    :param updatedAttributes: Dictionary with incident attributes to be updated.
    :return: Dictionary with ServiceNow API response for the PATCH incident message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = updatedAttributes
    data = json.dumps(data)
    url = url + "/api/now/table/incident/" + sysId
    response = requests.patch(url, headers=headers, data=data, verify=False)
    response = json.loads(response.text)
    logging.debug("[updateIncident]### UPDATED an incident in ServiceNow: \"{}\" with sys_id: {}.".format(response["result"]["number"], response["result"]["sys_id"]))
    return response


def getPreviousIncidents(accessToken: str, url: str, userSysId: str, count: int) -> dict:
    """
    Gets (GET) previously opened incident in ServiceNow instance in the descending order by open timestamp.
    
    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param url: ServiceNow instance URL.
    :param userSysId: String which identifies the user that opened previous incidents in ServiceNow.
    :param count: Integer representing the number of previously opened incidents to be retrieved.
    :return: Dictionary with ServiceNow API response for the GET incident message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    query = {"sysparm_query": "caller_id=" + userSysId + "^ORDERBYDESCsys_created_on",
             "sysparm_display_value": "sys_created_on,caller_id,short_description,sys_id,x_773797_webex_dem_spaceid,state,number", 
             "sysparm_limit": count}
    url = url + "/api/now/table/incident?" + urllib.parse.urlencode(query)
    response = requests.get(url, headers=headers, verify=False)
    response = json.loads(response.text)
    return response


def putWorkComment(accessToken, incidentSysId, url, additionalComment):
    """
    Creates (PUT) a work comment into the ServiceNow incident.
    
    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param incidentSysId: String which identifies the incident in ServiceNow.
    :param url: ServiceNow instance URL.
    :param additionalComment: String representing comments to be added from Webex space into the incident in ServiceNow as the work comments.
    :return: Dictionary with ServiceNow API response for the PUT incident message.
    """
    accessToken = "Bearer " + accessToken
    headers = {
        'Authorization': accessToken,
        'Content-Type': 'application/json'}
    data = "{\"comments\" :\"" + additionalComment + "\"}"
    url = url + "/api/now/table/incident/" + incidentSysId
    response = requests.put(url, headers=headers, data=data, verify=False)
    logging.debug("[putWorkComment]### ADDED a message: \"{}\" to ServiceNow incident (sys_id): {}.".format(additionalComment, incidentSysId))
    return response