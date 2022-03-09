def createWelcomeCard():

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
                        \"url\": \"https://banner2.cleanpng.com/20180810/laf/kisspng-logo-manchester-united-f-c-aon-organization-compa-bh2-our-clients-5b6e10d25d6154.3252090615339399223825.jpg\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Aon Service Now bot\",\
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
                \"wrap\": true}],\
            \"actions\":\
                [{\"type\": \"Action.Submit\",\
                \"title\": \"Create an Incident\",\
                \"data\":{\
                    \"flow\": \"createIncidentCard\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Previous Incidents\",\
                \"data\":{\
                    \"flow\": \"previousIncidents\"}},\
                {\"type\": \"Action.Submit\",\
                \"title\": \"Feedback\",\
                \"data\":{\
                    \"flow\": \"feedback\"}}]}}]"
    return payload


def createIncidentCard():

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
                        \"url\": \"https://banner2.cleanpng.com/20180810/laf/kisspng-logo-manchester-united-f-c-aon-organization-compa-bh2-our-clients-5b6e10d25d6154.3252090615339399223825.jpg\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Aon Service Now Bot\",\
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
                    \"flow\": \"createIncident\"}}]}}]"
    return payload

def previousIncidentsCard(incidentList, url):
    incidentString = ""
    i = 0
    for incident in incidentList:
        i = i + 1
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
                        \"url\": \"https://banner2.cleanpng.com/20180810/laf/kisspng-logo-manchester-united-f-c-aon-organization-compa-bh2-our-clients-5b6e10d25d6154.3252090615339399223825.jpg\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Aon Service Now bot\",\
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


def createFeedbackCard():

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
                        \"url\": \"https://banner2.cleanpng.com/20180810/laf/kisspng-logo-manchester-united-f-c-aon-organization-compa-bh2-our-clients-5b6e10d25d6154.3252090615339399223825.jpg\",\
                        \"size\": \"Medium\",\
                        \"height\": \"50px\"}],\
                    \"width\": \"auto\"},{\
                        \"type\": \"Column\",\
                        \"items\": [\
                            {\"type\": \"TextBlock\",\
                            \"text\": \"Aon Service Now bot\",\
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
                    \"flow\": \"submitFeedback\"}}]}}]"
    return payload