from __future__ import print_function
import json
from flask import Flask,request,make_response,session
import logging
from logging import Formatter, FileHandler
from time import gmtime, strftime



temperary={}


temperary={"messaages": [{"subtitle": "Card Subtitle", "title": "Recommendation 1", "imageUrl": "https://slimages.macys.com/is/image/MCY/products/0/optimized/3442430_fpx.tif?bgc=255,255,255&wid=164&qlt=90&layer=comp&op_sharpen=0&resMode=bicub&op_usm=0.7,1.0,0.5,0&fmt=jpeg", "buttons": [{"text": "Lauren Ralph Lauren Lace Sheath Dress", "postback": "http://www1.macys.com/shop/product/lauren-ralph-lauren-lace-sheath-dress?ID=1968356"}], "platform": "facebook", "type": 1}]}




app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def Image():
        app.logger.debug("Inside function Form2")
        req = request.get_json(silent=True, force=True)
        app.logger.debug("Request json:"+str(req))
        print (json.dumps(req, indent=4, sort_keys=True))
        res = processRequest(req)
        res = json.dumps(res, indent=4)
        app.logger.debug("Response json:"+res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        app.logger.debug("Response json:"+ str(r))
        return r


def processRequest(req):
    if(req.has_key("result")):
        if(req["result"].has_key("resolvedQuery")):
            if(req.get("result").get("resolvedQuery").startswith("FACEBOOK_MEDIA")):
                attach=req["originalRequest"]["data"]["data"]["message"]["attachments"]
                print(attach)
                imageData=attach[0]
                if(imageData["type"]=="image"):
                    #return imageData["payload"]["url"]
                    #JsonReply=Process(url)
                    print("########################################")
                    print(temperary)
                    return temperary[0]
        
    if(req.has_key("queryResult")):
        intentName=req.get("queryResult").get("intent").get("displayName")
    else:
        intentName=req.get("result").get("metadata").get("intentName")
    print(intentName)


    if ( intentName == 'Facebook'):
        return temperary[0]

    res=intent(intentName,req)
    if(req.has_key("queryResult")):
        res = makeWebhookResultV2(res)
    else:
        res = makeWebhookResultV1(res)
    return res
    

def intent(x,req):
    if (x=='Default Welcome Intent'):
        return DefaultResponse(req)
    if (x == 'Default Fallback Intent'):
        return DefaultResponse(req)

    else:
        return DefaultResponse(req)

def DefaultResponse(req):
        return 'Sorry I do not understand that but I am learning new stuff.'




def facebookResult():
    return{
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




