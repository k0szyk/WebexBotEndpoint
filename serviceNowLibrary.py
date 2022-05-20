import requests
import json
import urllib.parse
import logging
import time
import connectDb

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', filename='./WebexBotEndpoint.log', filemode='a')

def getRefreshToken(clientId: str, clientSecret: str, url: str, username: str, password: str):
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
    try:
        response = requests.post(url, data=data, verify=False)
        logging.debug("[getRefreshToken]### RETRIEVED successfully refresh token and access token.")
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.error("[getRefreshToken]### HTTP Error encountered while POSTING for Refresh Token: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getRefreshToken]### Connection Error encountered while POSTING for Refresh Token: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getRefreshToken]### Timeout Error encountered while POSTING for Refresh Token: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getRefreshToken]### General Error encountered while POSTING for Refresh Token: \"{}\".".format(err))
        response = err
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
    for key in access_token:
        if int(access_token[key]) > int(time.time()):
            logging.debug("[getAccessToken]### Access Token is still valid. Expiry of current access token: {}, current time {}".format(int(access_token[key]), int(time.time())))
            return {"access_token": key, "refresh_token": refreshToken, 'scope': 'useraccount', 'token_type': 'Bearer'}
    data = {
                'grant_type': 'refresh_token',
                'client_id': clientId,
                'client_secret': clientSecret,
                'refresh_token': refreshToken}
    url = url + "/oauth_token.do"
    try:
        responseAccessToken = requests.post(url, data=data, verify=False)
        responseAccessToken.raise_for_status()
        if responseAccessToken.status_code == 200:
            ### Catching developer instance of ServiceNow in hibernated status.
            if "Instance Hibernating page" in responseAccessToken.text:
                logging.error("[getAccessToken]### ERROR: ServiceNow {} is hibernated at this moment.".format(url))
            responseAccessToken = json.loads(responseAccessToken.text)
            logging.debug("[getAccessToken]### RETRIEVED successfully access token.")
            connectDb.updateAccessToken('access_token', 1, responseAccessToken["access_token"], int(time.time()+1770))
            logging.debug("[getAccessToken]### Update database with access token.")
        elif responseAccessToken.status_code == 401:
            responseRefreshToken = getRefreshToken(clientId, clientSecret, url, username, password)
            responseRefreshToken = json.loads(responseRefreshToken.text)
            responseAccessToken = responseRefreshToken
            connectDb.updateAccessToken('credentials', 5, responseAccessToken["refresh_token'"])
            logging.debug("[getAccessToken]### RETRIEVED successfully access token through refresh token.")
    except requests.exceptions.HTTPError as errh:
        logging.error("[getAccessToken]### HTTP Error encountered while POSTING for Access Token: \"{}\".".format(errh))
        responseAccessToken = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getAccessToken]### Connection Error encountered while POSTING for Access Token: \"{}\".".format(errc))
        responseAccessToken = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getAccessToken]### Timeout Error encountered while POSTING for Access Token: \"{}\".".format(errt))
        responseAccessToken = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getAccessToken]### General Error encountered while POSTING for Access Token: \"{}\".".format(err))
        responseAccessToken = err
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
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        logging.error("[getIncidentSysId]### HTTP Error encountered while GETTING Incident SysId: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getIncidentSysId]### Connection Error encountered while GETTING Incident SysId: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getIncidentSysId]### Timeout Error encountered while GETTING Incident SysId: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getIncidentSysId]### General Error encountered while GETTING Incident SysId: \"{}\".".format(err))
        response = err
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
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        logging.error("[getUserSysId]### HTTP Error encountered while GETTING User SysId: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getUserSysId]### Connection Error encountered while GETTING User SysId: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getUserSysId]### Timeout Error encountered while GETTING User SysId: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getUserSysId]### General Error encountered while GETTING User SysId: \"{}\".".format(err))
        response = err
    return response


def get_element_parameter(accessToken: str, url: str, table: str, query_string: str ) -> dict:
    """
    Gets (GET) the parameter of the element in ServiceNow table with a given query string

    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param url: ServiceNow instance URL.
    :param table: String representing the table in ServiceNow.
    :param query_string: String representing query string for required parameters
    :return: Dictionary with ServiceNow API response for the GET element(s) message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken}
    url = "{}/api/now/table/{}?sysparm_query={}".format(url, table, urllib.parse.quote(query_string, safe='&='))
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        logging.error("[getUserSysId]### HTTP Error encountered while GETTING User SysId: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getUserSysId]### Connection Error encountered while GETTING User SysId: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getUserSysId]### Timeout Error encountered while GETTING User SysId: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getUserSysId]### General Error encountered while GETTING User SysId: \"{}\".".format(err))
        response = err
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
    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
        logging.debug("[createIncident]### CREATED an incident in ServiceNow: \"{}\" with sys_id: {}.".format(response["result"]["number"], response["result"]["sys_id"]))
    except requests.exceptions.HTTPError as errh:
        logging.error("[createIncident]### HTTP Error encountered while POSTING new incident in Service Now: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[createIncident]### Connection Error encountered while POSTING new incident in Service Now: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[createIncident]### Timeout Error encountered while POSTING new incident in Service Now: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[createIncident]### General Error encountered while POSTING new incident in Service Now: \"{}\".".format(err))
        response = err
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
    try:
        response = requests.patch(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
        logging.debug("[updateIncident]### UPDATED an incident in ServiceNow: \"{}\" with sys_id: {}.".format(response["result"]["number"], response["result"]["sys_id"]))
    except requests.exceptions.HTTPError as errh:
        logging.error("[updateIncident]### HTTP Error encountered while PATCHING the incident in Service Now: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[updateIncident]### Connection Error encountered while PATCHING the incident in Service Now: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[updateIncident]### Timeout Error encountered while PATCHING the incident in Service Now: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[updateIncident]### General Error encountered while PATCHING the incident in Service Now: \"{}\".".format(err))
        response = err
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
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        logging.error("[getPreviousIncidents]### HTTP Error encountered while GETTING previous incidents: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getPreviousIncidents]### Connection Error encountered while GETTING previous incidents: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getPreviousIncidents]### Timeout Error encountered while GETTING previous incidents: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getPreviousIncidents]### General Error encountered while GETTING previous incidents: \"{}\".".format(err))
        response = err
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
    try:
        response = requests.put(url, headers=headers, data=data, verify=False)
        logging.debug("[putWorkComment]### ADDED a message: \"{}\" to ServiceNow incident (sys_id): {}.".format(additionalComment, incidentSysId))
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.error("[putWorkComment]### HTTP Error encountered while PUTTING work comments into the incident: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[putWorkComment]### Connection Error encountered while PUTTING work comments into the incident: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[putWorkComment]### Timeout Error encountered while PUTTING work comments into the incident: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[putWorkComment]### General Error encountered while PUTTING work comments into the incident: \"{}\".".format(err))
        response = err
    return response


def approval(accessToken, url, sysId, updatedAttributes):
    """
    Updates (PATCH) the approval in ServiceNow instance.

    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param url: ServiceNow instance URL.
    :param sysId: String which identifies the approval in ServiceNow.
    :param updatedAttributes: Dictionary with approval attributes to be updated.
    :return: Dictionary with ServiceNow API response for the PATCH approval message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = json.dumps(updatedAttributes)
    url = url + "/api/now/table/sysapproval_approver/" + sysId
    try:
        response = requests.patch(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
        logging.debug("[updateIncident]### UPDATED an approval in ServiceNow with sys_id: {}.".format(response["result"]["sys_id"]))
    except requests.exceptions.HTTPError as errh:
        logging.error("[updateIncident]### HTTP Error encountered while PATCHING the incident in Service Now: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[updateIncident]### Connection Error encountered while PATCHING the incident in Service Now: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[updateIncident]### Timeout Error encountered while PATCHING the incident in Service Now: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[updateIncident]### General Error encountered while PATCHING the incident in Service Now: \"{}\".".format(err))
        response = err
    return response


def getApproval(accessToken: str, url: str, sysId: str) -> dict:
    """
    Gets (GET) the paramers of the approval from ServiceNow instance.

    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param url: ServiceNow instance URL.
    :param sysId: String representing the Id of the Approval.
    :return: Dictionary with ServiceNow API response for the GET sys_user message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Accept': 'application/json',
               'Content-Type': 'application/json'}
    url = url + "/api/now/table/sysapproval_approver/" + sysId
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        logging.error("[getUserSysId]### HTTP Error encountered while GETTING User SysId: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getUserSysId]### Connection Error encountered while GETTING User SysId: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getUserSysId]### Timeout Error encountered while GETTING User SysId: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getUserSysId]### General Error encountered while GETTING User SysId: \"{}\".".format(err))
        response = err
    return response


def getApprovalbyChangeId(accessToken: str, url: str, document_id: str) -> dict:
    """
    Gets (GET) the approvals for a specific Change Request.

    :param accessToken: String with accessToken required to authentication with SerivceNow instance via OAuth2.
    :param url: ServiceNow instance URL.
    :param document_id: String representing the SysId of the Change Request.
    :param updatedAttributes: Dictionary with approval attributes to be updated.
    :return: Dictionary with ServiceNow API response for the GET sysapproval_approver message.
    """
    accessToken = "Bearer " + accessToken
    headers = {'Authorization': accessToken,
               'Accept': 'application/json',
               'Content-Type': 'application/json'}
    query = {"sysparm_query": "document_id=" + document_id}
    url = url + "/api/now/table/sysapproval_approver?" + urllib.parse.urlencode(query)
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
        sys_ids = list()
        for element in response["result"]:
            sys_ids.append(element["sys_id"])
        logging.debug("[getApprovalbyChangeId]### GET approvals by Change Request ID in ServiceNow with array of approval sys_ids: {}.".format(sys_ids))
    except requests.exceptions.HTTPError as errh:
        logging.error("[getApprovalbyChangeId]### HTTP Error encountered while GETTING User SysId: \"{}\".".format(errh))
        response = errh
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getApprovalbyChangeId]### Connection Error encountered while GETTING User SysId: \"{}\".".format(errc))
        response = errc
    except requests.exceptions.Timeout as errt:
        logging.error("[getApprovalbyChangeId]### Timeout Error encountered while GETTING User SysId: \"{}\".".format(errt))
        response = errt
    except requests.exceptions.RequestException as err:
        logging.error("[getApprovalbyChangeId]### General Error encountered while GETTING User SysId: \"{}\".".format(err))
        response = err
    return response
