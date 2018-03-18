from __future__ import print_function
import json
from flask import Flask,request,make_response,session
import logging
from logging import Formatter, FileHandler
from time import gmtime, strftime

import RebeccaIntro as IntentIntro
import RebeccaFollowUp as IntentFollowUp
import RebeccaBookAppt as IntentBookAppt

app = Flask(__name__)
@app.route('/Form2', methods=['POST'])
def form2():
        app.logger.debug("Inside function Form2")
        req = request.get_json(silent=True, force=True)
        app.logger.debug("Request json:"+str(req))
        res = processRequest(req)
	if str(res).startswith("@EVENT="):
		res=makeWebhookResult("a", str(res.split('=')[1]), 1)
        else:
            	res = makeWebhookResult(res)
        res = json.dumps(res, indent=4)
        app.logger.debug("Response json:"+res)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        app.logger.debug("Response json:"+ str(r))
        return r


def processRequest(req):
    intentName=req.get("result").get("metadata").get("intentName")
    print(intentName)
    return (intent(intentName,req))

def intent(x,req):
    if (x=='Default Welcome Intent'):
        return IntentIntro.welcome(req)
    if (x == 'Name'):
        return IntentIntro.Name(req)
    if (x == 'Interest'):
        return IntentIntro.Interest(req)
    if (x == 'Organization-Name'):
        return IntentIntro.Organization_Name(req)
    if (x == 'IntroFollowUp'):
        return IntentIntro.IntroFollowUp(req)
    if (x == 'Calendar_api'):
	return IntentBookAppt.Calendar_api(req)
    if (x == 'Calendar_Confirm'):
	return IntentBookAppt.Calendar_Confirm(req)
    if (x == 'CalendarTime'):
	return IntentBookAppt.CalendarTime(req)
    if (x == 'ContactInfo'):
	return IntentFollowUp.ContactInfo(req)
    if (x == 'NotYet'):
	return IntentFollowUp.NotYet(req)
    if (x == 'SkipBookAppt'):
	return IntentBookAppt.SkipBookAppt(req)
    if (x == 'SkipFollowUp'):
	return IntentFollowUp.SkipFollowUp(req)
    if (x == 'Default Fallback Intent'):
	return DefaultResponse(req)

def DefaultResponse(req):
	return 'Sorry I do not understand that but I am learning new stuff.'

def makeWebhookResult(speech,fullfillment="",flag=1):
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
    app.run(host='0.0.0.0', port=8081,debug=True)
    app.logger.debug('Server stoped at '+strftime("%Y-%m-%d %H:%M:%S", gmtime()) )


