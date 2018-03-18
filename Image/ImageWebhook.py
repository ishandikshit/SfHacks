from __future__ import print_function
import json
from flask import Flask,request,make_response,session
import logging
from logging import Formatter, FileHandler
from time import gmtime, strftime
import recognizeURI as macy
import urllib
import mysql.connector    
import numpy as np

app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def Image():
        app.logger.debug("Inside function Form2")
        req = request.get_json(silent=True, force=True)
        app.logger.debug("Request json:"+str(req))
        print(json.dumps(req, indent=4))
        res = processRequest(req)
        res = json.dumps(res, indent=4)
        app.logger.debug("Response json:"+res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        app.logger.debug("Response json:"+ str(r))
        return r


def processRequest(req):

    if(req.has_key("queryResult")):
        intentName=req.get("queryResult").get("intent").get("displayName")
    else:
        intentName=req.get("result").get("metadata").get("intentName")
    print(intentName)
    
    if(req.has_key("result")):
        if(req["result"].has_key("resolvedQuery")):
            if(req.get("result").get("resolvedQuery").startswith("FACEBOOK_MEDIA")):
                attach=req["originalRequest"]["data"]["data"]["message"]["attachments"]
                imageData=attach[0]
                if(imageData["type"]=="image"):
                    urllib.urlretrieve(imageData["payload"]["url"], "local-filename.jpg")
                    macyReply=macy.detect_labels_uri("local-filename.jpg")
                    return prepareResponseForMacy(macyReply)
    if(req.has_key("queryResult")):
        if(req.get("queryResult").get("queryText").startswith("FACEBOOK_MEDIA")):
            if(req.has_key("originalDetectIntentRequest")):
                attach=req["originalDetectIntentRequest"]["payload"]["data"]["message"]["attachments"]
                imageData=attach[0]
                if(imageData["type"]=="image"):
                    urllib.urlretrieve(imageData["payload"]["url"], "local-filename.jpg")
                    macyReply=macy.detect_labels_uri("local-filename.jpg")
                    return prepareResponseForMacy(macyReply)
    
    if ( intentName == 'facebook_macy_url'):
        if(req.has_key("result")):
            urllib.urlretrieve(req.get("result").get("resolvedQuery"), "local-filename.jpg")
            macyReply=macy.detect_labels_uri("local-filename.jpg")
            return prepareResponseForMacy(macyReply)
        else:
            urllib.urlretrieve(req.get("queryResult").get("queryText"), "local-filename.jpg")
            macyReply=macy.detect_labels_uri("local-filename.jpg")
            return prepareResponseForMacy(macyReply)

    if ( intentName == 'facebook_macy_price_max'):
        con=database()
        conn=con.cursor()
        conn.execute("Select * from macytable")
        data=conn.fetchall()
        maxValue=-1.0
        Answer=None
        for row in data:
            if(float(row[3])>maxValue):
                Answer = row
                maxValue=float(row[3])
        row=Answer
        return facebookResult(row[0],row[1],row[2],"$"+str(row[3]))
    if ( intentName == 'facebook_macy_price_min'):
        con=database()
        conn=con.cursor()
        conn.execute("Select * from macytable")
        data=conn.fetchall()
        minValue=20000000
        Answer=None
        for row in data:
            if(float(row[3])<minValue):
                Answer = row
                minValue=float(row[3])
        row=Answer
        return facebookResult(row[0],row[1],row[2],"$"+str(row[3]))
        return intentName
    if ( intentName == 'facebook_macy_review'):
        con=database()
        conn=con.cursor()
        conn.execute("Select * from macytable")
        data=conn.fetchall()
        maxValue=-1.0
        Answer=None
        for row in data:
            if(float(row[4])>maxValue):
                Answer = row
                maxValue=float(row[4])
        row=Answer
        return facebookResult(row[0],row[1],row[2],row[4])

    if ( intentName == 'facebook_macy_photo_match'):
        context=req["result"]["contexts"]
        for cntx  in context:
            contextName=cntx["name"]
            #contextName=a[len(a)-1]
            if(contextName == 'generic'):
                tag=cntx["parameters"]["DressEntity"]
                city=cntx["parameters"]["geo-city"]
                startDate=cntx["parameters"]["date-period"].split("/")[0]
                endDate=cntx["parameters"]["date-period"].split("/")[1]
                break
        
        con = database()
        conn=con.cursor()
        conn.execute("Select * from macyimages")
        data=conn.fetchall()
        startDate= np.datetime64(startDate)
        endDate= np.datetime64(endDate)
        List=[]
        for row in data:
            temp= np.datetime64(row[2])
            if(temp > startDate and temp < endDate):
                List.append(row)

        if not List:
            return  makeWebhookResultV2("No such Image")

        for cty in List:
            if(cty[1].lower()==city.lower()):
                ImageName= cty[0]
                break
        macyReply=macy.detect_labels_uri2(ImageName,tag)
        return prepareResponseForMacy(macyReply)



        
    
    res=intent(intentName,req)
    if(req.has_key("queryResult")):
        res = makeWebhookResultV2(res)
    else:
        res = makeWebhookResultV1(res)
    return res
    

def intent(intentName,req):
    if (intentName =='Default Welcome Intent'):
        return DefaultResponse(req)
    if (intentName == 'Default Fallback Intent'):
        return DefaultResponse(req)
    else:
        return DefaultResponse(req)

def DefaultResponse(req):
        return 'Sorry I do not understand that but I am learning new stuff.'




def facebookResult(text,imageurl,postback,price):
    return{
        "messages": [
        {
          "buttons": [
                     {
                      "postback": postback,
                      "text": text
                      }
                      ],
                      "imageUrl": imageurl,
                      "platform": "facebook",
                      "subtitle": "",
                       "title": price,
                        "type": 1
                      }
                  ]
    }

def makeWebhookResultV2(speech,fullfillment="",flag=1):
    return {
  "fulfillmentText": speech,
  "source": speech,
  "followupEventInput": ""
}

def makeWebhookResultV1(speech,fullfillment="",flag=1):
      return {
        "followupEvent": {
            "name": fullfillment
        },
        "speech": speech,
        "displayText": speech,
        "source": "apiai-webhook-rebecca"
    }



def database():
    cnx = mysql.connector.connect(user='macyuser', password='password',host='localhost',database='macy')
    return cnx


def prepareResponseForMacy(macyDict):      
    
    print("##$#$#$#$#$#$#$#$#$#$#$#$#$#$#$#$")
    message=[]
    count=0
    for recommendation in macyDict["response"]: 
        count=count+1
        Card={}
        Card["buttons"]=[{"postback":recommendation["producturl"], "text": recommendation["title"]}]
        Card["imageUrl"]=recommendation["imageurl"]
        Card["platform"]= "facebook"
        Card["subtitle"]= "Card Subtitle"
        Card["title"]="Recommendation "+ str(count)
        Card["type"]=1
        message.append(Card)
    reply={}
    reply["messages"]=message
    print(reply)
    return reply


if __name__ == '__main__':
    file_handler = FileHandler('output.log')
    handler = logging.StreamHandler()
    file_handler.setLevel(logging.DEBUG)
    handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(handler)
    app.logger.addHandler(file_handler)
    app.logger.warning('Server started at '+strftime("%Y-%m-%d %H:%M:%S", gmtime()) )
    app.run(host='0.0.0.0', port=80,debug=False)
    app.logger.debug('Server stoped at '+strftime("%Y-%m-%d %H:%M:%S", gmtime()) )



