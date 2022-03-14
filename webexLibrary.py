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
    response = requests.get(url, headers=headers, verify=False)
    response = json.loads(response.text)
    return response


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
    url  = webexUrl + messageUrl
    logging.debug("[postWebexMessage]### SENT a message: \"{}\".".format(textMessage))
    response = requests.post(url, headers=headers, data=data, verify=False)
    response = json.loads(response.text)
    #logging.debug("[postWebexMessage]### RECEIVED a response: \"{}\".".format(response.text))
    return response


def deleteWebexMessage(botToken: str, messageId: str, webexUrl: str, messageUrl: str) -> dict:
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
    response = requests.delete(url, headers=headers, verify=False)
    logging.debug("[deleteWebexMessage]### DELETED a message with a messageId: \"{}\".".format(messageId))
    return response

