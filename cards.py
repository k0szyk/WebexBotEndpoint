import base64
import logging

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', filename='./WebexBotEndpoint.log', filemode='a')


def createWelcomeCard(iconUrl: str, faqUrl: str, spaceIdUrl: str) -> str:
    """
    Contains a payload required to create a Webex card - createWelcomeCard.
    
    :param iconUrl: String with icon URL (branding).
    :param faqUrl: String with the URL for the Frequently Asked Questions page.
    :param spaceIdUrl: String with the URL to join the Webex space where a user can get some assistance.
    :return: String with a payload required to create a Webex card - createWelcomeCard.
    """
    payload = "[{\
        \"contentType\": \"application/vnd.microsoft.card.adaptive\",\
        \"content\": \
            {\"$schema\": \"http://adaptivecards.io/schemas/adaptive-card.json\",\
            \"type\": \"AdaptiveCard\",\
            \"version\": \"1.2\",\
            \"body\": [{\
                \"type\": \"ColumnSet\",\
                \"columns\": [{\
                    \"type\": \"Column\",\
                    \"items\": [{\
                        \"type\": \"Image\",\
                        \"url\": \"" + iconUrl + "\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Service Now bot\",\
                            \"weight\": \"Lighter\",\
                            \"color\": \"Accent\"},\
                            {\"type\": \"TextBlock\",\
                            \"weight\": \"Bolder\",\
                            \"text\": \"Welcome to Service Now bot!\",\
                            \"wrap\": true,\
                            \"color\": \"Light\",\
                            \"size\": \"Large\",\
                            \"spacing\": \"Small\"}]}]},\
                {\"type\": \"TextBlock\",\
                \"text\": \"Thanks for using ServiceNow bot.\",\
                \"wrap\": true},\
                {\"type\": \"TextBlock\",\
                \"text\": \"* To **create an incident** press ```Create Incident``` button.\",\
                \"wrap\": true},\
                {\"type\": \"TextBlock\",\
                \"text\": \"* To verify the status of already opened incident press ```Opened Incidents```.\",\
                \"wrap\": true},\
                {\"type\": \"TextBlock\",\
                \"text\": \"* If you have some ideas on how to improve the bot, please select ```Feedback```.\",\
                \"wrap\": true},\
                {\"type\": \"TextBlock\",\
                \"text\": \"Questions? Check our [FAQ page](" + faqUrl + ") or join our [Webex space](" + spaceIdUrl + ").\",\
                \"weight\": \"Lighter\",\
                \"color\": \"Light\"}],\
            \"actions\":\
                [{\"type\": \"Action.Submit\",\
                \"title\": \"Create an incident\",\
                \"data\":{\
                    \"flow\": \"createIncidentCard\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Previous incidents\",\
                \"data\":{\
                    \"flow\": \"previousIncidents\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Update an incident\",\
                \"data\":{\
                    \"flow\": \"updateIncident\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Feedback\",\
                \"data\":{\
                    \"flow\": \"feedback\"}}\
                    ]}}]"
    return payload


def createIncidentCard(iconUrl: str) -> str:
    """
    Contains a payload required to create a Webex card - createIncidentCard.
    
    :param iconUrl: String with icon URL (branding).
    :return: String with a payload required to create a Webex card - createIncidentCard.
    """
    payload = "[{\
        \"contentType\": \"application/vnd.microsoft.card.adaptive\",\
        \"content\": \
            {\"$schema\": \"http://adaptivecards.io/schemas/adaptive-card.json\",\
            \"type\": \"AdaptiveCard\",\
            \"version\": \"1.2\",\
            \"body\": [{\
                \"type\": \"ColumnSet\",\
                \"columns\": [{\
                    \"type\": \"Column\",\
                    \"items\": [{\
                        \"type\": \"Image\",\
                        \"url\": \"" + iconUrl + "\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Service Now Bot\",\
                            \"weight\": \"Lighter\",\
                            \"color\": \"Accent\"},\
                            {\"type\": \"TextBlock\",\
                            \"weight\": \"Bolder\",\
                            \"text\": \"Create Service Now Incident\",\
                            \"wrap\": true,\
                            \"color\": \"Light\",\
                            \"size\": \"Large\",\
                            \"spacing\": \"Small\"}]}]},\
                {\"type\": \"TextBlock\",\
                \"text\": \"Short description:\",\
                \"wrap\": true},\
                {\"type\": \"Input.Text\",\
                \"id\": \"shortDescription\",\
                \"placeholder\": \"Please provide initial details.\" },\
                {\"type\": \"TextBlock\",\
                \"text\": \"Full description:\",\
                \"wrap\": true},\
                {\"type\": \"Input.Text\",\
                \"id\": \"fullDescription\",\
                \"placeholder\": \"Please provide additional details.\",\
                \"isMultiline\": true},\
                {\"type\": \"TextBlock\",\
                \"text\": \"Urgency:\",\
                \"wrap\": true},\
                {\"type\": \"Input.ChoiceSet\",\
                \"choices\": [{\
                    \"title\": \"3 - Low\",\
                    \"value\": \"3\"},\
                    {\"title\": \"2 - Medium\",\
                    \"value\": \"2\"},\
                    {\"title\": \"1 - High\",\
                    \"value\": \"1\"}],\
                \"placeholder\": \"Select a value\",\
                \"value\": \"3\",\
                \"id\": \"urgency\"},\
                {\"type\": \"Input.Toggle\",\
                \"title\": \"Follow in Webex Space?\",\
                \"id\": \"checkbox\",\
                \"value\": \"true\"}],\
            \"actions\":\
                [{\"type\": \"Action.Submit\",\
                \"title\": \"Submit\",\
                \"data\":{\
                    \"flow\": \"createIncident\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Go back\",\
                \"data\":{\
                    \"flow\": \"goBack\"}}]}}]"
    return payload

def previousIncidentsCard(incidentList: list, url: str, iconUrl: str) -> str:
    """
    Contains a payload required to create a Webex card - createIncidentCard.
    
    :param incidentList: List with previously opened incidents.
    :param url: String representing the ServiceNow instance URL.
    :param iconUrl: String with icon URL (branding).
    :return: String with a payload required to create a Webex card - createIncidentCard.
    """
    incidentString = ""
    i = 0
    for incident in incidentList:
        i = i + 1
        if incident["state"] != "Closed" and incident["spaceId"]:
            incidentString = incidentString + "{{\"type\": \"TextBlock\",\"text\": \"[{}]({}/sp?id=ticket&table=incident&view=sp&sys_id={}): [{}] - {} - [go to Webex space](webexteams://im?space={})\",\"wrap\": true}}".format(incident["number"], url, incident["sysId"], incident["state"], incident["shortDescription"], base64.b64decode(incident["spaceId"]).decode('utf-8').split("/")[-1])
        else:
            incidentString = incidentString + "{{\"type\": \"TextBlock\",\"text\": \"[{}]({}/sp?id=ticket&table=incident&view=sp&sys_id={}): [{}] - {}\",\"wrap\": true}}".format(incident["number"], url, incident["sysId"], incident["state"], incident["shortDescription"])
        if len(incidentList) > i:
            incidentString = incidentString + ","
    payload = "[{\
        \"contentType\": \"application/vnd.microsoft.card.adaptive\",\
        \"content\": \
            {\"$schema\": \"http://adaptivecards.io/schemas/adaptive-card.json\",\
            \"type\": \"AdaptiveCard\",\
            \"version\": \"1.2\",\
            \"body\": [{\
                \"type\": \"ColumnSet\",\
                \"columns\": [{\
                    \"type\": \"Column\",\
                    \"items\": [{\
                        \"type\": \"Image\",\
                        \"url\": \"" + iconUrl + "\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Service Now bot\",\
                            \"weight\": \"Lighter\",\
                            \"color\": \"Accent\"},\
                            {\"type\": \"TextBlock\",\
                            \"weight\": \"Bolder\",\
                            \"text\": \"Previous Incidents\",\
                            \"wrap\": true,\
                            \"color\": \"Light\",\
                            \"size\": \"Large\",\
                            \"spacing\": \"Small\"}]}]},\
                {\"type\": \"TextBlock\",\
                \"text\": \"Below is the list of last 5 incidents opened for your account:\",\
                \"wrap\": true},\
                " + incidentString + "],\
            \"actions\":\
                [{\"type\": \"Action.Submit\",\
                \"title\": \"Go back\",\
                \"data\":{\
                    \"flow\": \"goBack\"}}]}}]"
    return payload


def createFeedbackCard(iconUrl: str) -> str:
    """
    Contains a payload required to create a Webex card - createFeedbackCard.
    
    :param iconUrl: String with icon URL (branding).
    :return: String with a payload required to create a Webex card - createFeedbackCard.
    """
    payload = "[{\
        \"contentType\": \"application/vnd.microsoft.card.adaptive\",\
        \"content\": \
            {\"$schema\": \"http://adaptivecards.io/schemas/adaptive-card.json\",\
            \"type\": \"AdaptiveCard\",\
            \"version\": \"1.2\",\
            \"body\": [{\
                \"type\": \"ColumnSet\",\
                \"columns\": [{\
                    \"type\": \"Column\",\
                    \"items\": [{\
                        \"type\": \"Image\",\
                        \"url\": \"" + iconUrl + "\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Service Now bot\",\
                            \"weight\": \"Lighter\",\
                            \"color\": \"Accent\"},\
                            {\"type\": \"TextBlock\",\
                            \"weight\": \"Bolder\",\
                            \"text\": \"Thanks for your feedback!\",\
                            \"wrap\": true,\
                            \"color\": \"Light\",\
                            \"size\": \"Large\",\
                            \"spacing\": \"Small\"}]}]},\
                {\"type\": \"TextBlock\",\
                \"text\": \"Please share with us your opinions or ideas:\",\
                \"wrap\": true},\
                {\"type\": \"Input.Text\",\
                \"id\": \"feedbackText\",\
                \"placeholder\": \"Please share with us your opinions or ideas:\",\
                \"isMultiline\": true}],\
            \"actions\":\
                [{\"type\": \"Action.Submit\",\
                \"title\": \"Submit\",\
                \"data\":{\
                    \"flow\": \"submitFeedback\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Go back\",\
                \"data\":{\
                    \"flow\": \"goBack\"}}]}}]"
    return payload

def createUpdateIncidentCard(incidentList: list, iconUrl: str, isVisible = "true", value = "") -> str:
    """
    Contains a payload required to create a Webex card - createUpdateIncidentCard.
    
    :param incidentList: List with previously opened incidents.
    :param iconUrl: String with icon URL (branding).
    :param isVisible: String specifing if incidents drop list is visible or not.
    :param value: String representing a default incident - used when only when we know what is the incident to be updated.
    :return: String with a payload required to create a Webex card - createUpdateIncidentCard.
    """ 
    incidentString = ""
    for incident in incidentList:
        if incident["state"] != "Closed" and incident["state"] != "Resolved":
            if incidentString != "":
                incidentString = incidentString + ","
            incidentString = incidentString + "{\"title\": \"" + incident["number"] + "\",\"value\": \"" + incident["number"] + "\"}"
            
    logging.debug("Prepared the incident string: {}".format(incidentString))

    if isVisible == "true":
        actions = "[{\"type\": \"Action.Submit\",\"title\": \"Submit\",\"data\":{\"flow\": \"submitUpdate\"}},{\"type\": \"Action.Submit\",\"title\": \"Go back\",\"data\":{\"flow\": \"goBack\"}}]"
    else:
        actions = "[{\"type\": \"Action.Submit\",\"title\": \"Submit\",\"data\":{\"flow\": \"submitUpdateDirect\"}}]"
    logging.debug("Prepared the actions string: {}".format(actions))
    payload = "[{\
        \"contentType\": \"application/vnd.microsoft.card.adaptive\",\
        \"content\": \
            {\"$schema\": \"http://adaptivecards.io/schemas/adaptive-card.json\",\
            \"type\": \"AdaptiveCard\",\
            \"version\": \"1.2\",\
            \"body\": [{\
                \"type\": \"ColumnSet\",\
                \"columns\": [{\
                    \"type\": \"Column\",\
                    \"items\": [{\
                        \"type\": \"Image\",\
                        \"url\": \"" + iconUrl + "\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Service Now bot\",\
                            \"weight\": \"Lighter\",\
                            \"color\": \"Accent\"},\
                            {\"type\": \"TextBlock\",\
                            \"weight\": \"Bolder\",\
                            \"text\": \"Update an incident:\",\
                            \"wrap\": true,\
                            \"color\": \"Light\",\
                            \"size\": \"Large\",\
                            \"spacing\": \"Small\"}]}]},\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Please select an incident:\",\
                            \"isVisible\": " + isVisible + ",\
                            \"wrap\": true},\
                            {\"type\": \"Input.ChoiceSet\",\
                            \"choices\": [" + incidentString + "],\
                            \"placeholder\": \"Select an incident\",\
                            \"value\": \"" + value + "\",\
                            \"isVisible\": " + isVisible + ",\
                            \"id\": \"incidentNumber\"},\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Please type in your comment/update to be added to the incident:\",\
                            \"wrap\": true},\
                            {\"type\": \"Input.Text\",\
                            \"id\": \"updateText\",\
                            \"placeholder\": \"Your comments...\",\
                            \"isMultiline\": true}],\
            \"actions\": " + actions + "}}]"
    return payload