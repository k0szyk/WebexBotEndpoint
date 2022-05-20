import requests
import logging
import json

def getWebexItemDetails(botToken: str, id: str, webexUrl: str, itemSpecificUrl: str) -> dict:
    """
    Gets (GET) detail of the Webex item (space, person, membership etc.).
    
    :param botToken: String required for OAuth2 with Webex API.
    :param id: String representing the id of the Webex item (space, person, membership etc.).
    :param webexUrl: Webex API URL.
    :param itemSpecificUrl: URN for a specific item to be queried via Webex API.
    :return: Dictionary with Webex API response for the item query GET message.
    """
    botToken = "Bearer " + botToken
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json'}
    url = webexUrl + itemSpecificUrl + id
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        logging.error("[getWebexItemDetails]### HTTP Error encountered while GETTING Webex message: \"{}\".".format(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error("[getWebexItemDetails]### Connection Error encountered while GETTING Webex message: \"{}\".".format(errc))
    except requests.exceptions.Timeout as errt:
        logging.error("[getWebexItemDetails]### Timeout Error encountered while GETTING Webex message: \"{}\".".format(errt))
    except requests.exceptions.RequestException as err:
        logging.error("[getWebexItemDetails]### General Error encountered while GETTING Webex message: \"{}\".".format(err))


def postWebexMessage(botToken: str, spaceId: str, webexUrl: str, messageUrl: str, textMessage: str, attachments = []) -> dict:
    """
    Creates (POST) the Webex message (message is created by ServiceNowbot).
    
    :param botToken: String required for OAuth2 with Webex API.
    :param spaceId: String representing the id of the Webex space.
    :param webexUrl: Webex API URL.
    :param messageUrl: Webex API URN to send a message.
    :param textMessage: String representing the message.
    :param textMessage: List with a card message (optional).
    :return: Dictionary with Webex API response for the POST message.
    """
    botToken = "Bearer " + botToken
    textMarkdown = textMessage
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json',
        'Content-Type': 'application/json'}
    data = "{\"roomId\" : \"" + spaceId + "\",\"text\" : \"" + textMessage + "\",\"markdown\" : \"" + textMarkdown + "\",\"attachments\" : " + str(attachments) + "}"
    url = webexUrl + messageUrl
    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        logging.debug("[postWebexMessage]### SENT a message: \"{}\".".format(textMessage))
        response.raise_for_status()
        response = json.loads(response.text)
        return response
    except requests.exceptions.HTTPError as errh:
        logging.error("[postWebexMessage]### HTTP Error encountered while SENDING Webex message: \"{}\".".format(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error("[postWebexMessage]### Connection Error encountered while SENDING Webex message: \"{}\".".format(errc))
    except requests.exceptions.Timeout as errt:
        logging.error("[postWebexMessage]### Timeout Error encountered while SENDING Webex message: \"{}\".".format(errt))
    except requests.exceptions.RequestException as err:
        logging.error("[postWebexMessage]### General Error encountered while SENDING Webex message: \"{}\".".format(err))
    #logging.debug("[postWebexMessage]### RECEIVED a response: \"{}\".".format(response.text))



def deleteWebexMessage(botToken: str, messageId: str, webexUrl: str, messageUrl: str):
    """
    Creates (POST) the Webex message (message is created by ServiceNowbot).
    
    :param botToken: String required for OAuth2 with Webex API.
    :param ispaceIdd: String representing the id of the Webex space.
    :param webexUrl: Webex API URL.
    :param messageUrl: Webex API URN to send a message.
    :return: Dictionary with Webex API response for the DELETE message.
    """
    botToken = "Bearer " + botToken
    headers = {
        'Authorization': botToken,
        'Accepts': 'application/json',
        'Content-Type': 'application/json'}
    url  = webexUrl + messageUrl + messageId
    try:
        response = requests.delete(url, headers=headers, verify=False)
        logging.debug("[deleteWebexMessage]### DELETED a message with a messageId: \"{}\".".format(messageId))
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        logging.error("[deleteWebexMessage]### HTTP Error encountered while DELETING Webex message: \"{}\".".format(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error("[deleteWebexMessage]### Connection Error encountered while DELETING Webex message: \"{}\".".format(errc))
    except requests.exceptions.Timeout as errt:
        logging.error("[deleteWebexMessage]### Timeout Error encountered while DELETING Webex message: \"{}\".".format(errt))
    except requests.exceptions.RequestException as err:
        logging.error("[deleteWebexMessage]### General Error encountered while DELETING Webex message: \"{}\".".format(err))


def createWebexMeeting(accessToken: str, data: dict, webexUrl: str):
    """
    Creates a Webex Meeting

    :param accessToken: Access Token required for authentication.
    :param title: String representing a title of the Meeting.
    :param start: String representing start time.
    :param end: String representing end time.
    :param host_email: String representing the email address of the host.
    :param siteUrl: String representing the URL of the site that is hosting the meeting.
    :param webexUrl: String representing the URL of Webex API.
    :param invitees: List representing
    :return: Dictionary with Webex API response for the create Webex Meeting.
    """
    accessToken = "Bearer " + accessToken
    headers = {
        'Authorization': accessToken,
        'Accepts': 'application/json',
        'Content-Type': 'application/json'}
    url = webexUrl + 'v1/meetings'
    data = json.dumps(data)
    logging.debug("Data after json: {}.".format(data))
    try:
        response = requests.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        response = json.loads(response.text)
        logging.debug("[createWebexMeeting]### Create a Webex Meeting with a meetingId: \"{}\".".format(response["meetingNumber"]))
        return response
    except requests.exceptions.HTTPError as errh:
        logging.error("[createWebexMeeting]### HTTP Error encountered while CREATING Webex Meeting: \"{}\".".format(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error("[createWebexMeeting]### Connection Error encountered while CREATING Webex Meeting: \"{}\".".format(errc))
    except requests.exceptions.Timeout as errt:
        logging.error("[createWebexMeeting]### Timeout Error encountered while CREATING Webex Meeting: \"{}\".".format(errt))
    except requests.exceptions.RequestException as err:
        logging.error("[createWebexMeeting]### General Error encountered while CREATING Webex Meeting: \"{}\".".format(err))


def refreshWebexToken(refresh_token: str, webex_client_id: str, webex_secret_id: str) -> dict:
    """
    Acquires new Access Token and refreshes the Refresh Token

    :param refresh_token: String representing the Refresh Token.
    :param webex_client_id: String representing the Webex Client ID.
    :param webex_secret_id: String representing the Webex Secret.
    :return: Dictionary with Webex API response for the refresh token request.
    """
    payload = ("?grant_type=refresh_token&client_id={}&client_secret={}&refresh_token={}").format(webex_client_id, webex_secret_id, refresh_token)
    headers = {'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded'}
    url = 'https://webexapis.com/v1/access_token' + payload
    try:
        response = requests.post(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            response = json.loads(response.text)
            return response
    except requests.exceptions.HTTPError as errh:
        logging.error("[refreshWebexToken]### HTTP Error encountered while REFRESHING Webex Tokens: \"{}\".".format(errh))
    except requests.exceptions.ConnectionError as errc:
        logging.error("[refreshWebexToken]### Connection Error encountered while REFRESHING Webex Tokens: \"{}\".".format(errc))
    except requests.exceptions.Timeout as errt:
        logging.error("[refreshWebexToken]### Timeout Error encountered while REFRESHING Webex Tokens: \"{}\".".format(errt))
    except requests.exceptions.RequestException as err:
        logging.error("[refreshWebexToken]### General Error encountered while REFRESHING Webex Tokens: \"{}\".".format(err))


