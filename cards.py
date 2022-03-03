

def createIncidentCards():

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
                            \"text\": \"AON Service Now Bot\",\
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
                \"text\": \"Impact:\",\
                \"wrap\": true},\
                {\"type\": \"Input.ChoiceSet\",\
                \"choices\": [\
                    {\"title\": \"3 - Low\",\
                    \"value\": \"3\"},\
                    {\"title\": \"2 - Medium\",\
                    \"value\": \"2\"},\
                    {\"title\": \"1 - High\",\
                    \"value\": \"1\"}],\
                    \"placeholder\": \"Select a value\",\
                    \"value\": \"3\",\
                    \"id\": \"impact\"},\
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
                \"title\": \"Submit\"}]}}]"
    return payload