from service_now import servicenowrequests
import json
import os
from dotenv import load_dotenv
from flask import Flask, request, url_for, render_template,redirect, jsonify
from datetime import datetime
import logging
import pandas as pd
from controller import Controller

date = datetime.today()
date = datetime.strftime(date,"%d-%b-%Y")

app = Flask(__name__)
load_dotenv()
servicenow_username = os.getenv("service_now_username")
servicenow_pass = os.getenv("service_now_password")

@app.route("/")
def home():
    return render_template("app-home.html")

@app.route("/incidents/all")
def get_all_incident():
    incidents = servicenowrequests("https://dev202603.service-now.com/")
    resp = incidents.get_details("incident",servicenow_username,servicenow_pass)
    print(type(resp))
    if type(resp) is str:
        status = {"status":"Failed"}
        resp_failed = {"response":resp}|status
        return jsonify(resp_failed)
    else:
        print(type(resp))
        status = {"status":"Success"}
        resp.append(status)
        with open("resp.json","w") as write_resp:
            json.dump(resp,write_resp,indent=4)
        write_resp.close()
        with open("resp.json","r") as read_resp:
            resp = json.load(read_resp)
            con = Controller()
            con.write_data(resp)
        return jsonify(resp)



@app.route("/incidents/filter/",methods=["POST"])
def get_specific_incidents():
    posted_data = request.json["date"]
    return jsonify({"input":posted_data})


@app.route("/sc_tasks/")
def get_sc_tasks():
    sc_tasks = servicenowrequests("https://dev202603.service-now.com/")
    resp = sc_tasks.get_details("sc_task",servicenow_username,servicenow_pass)
    if type(resp) is str:
        status = {"status":"Failed"}
        resp_failed = {"response":resp}|status
        return jsonify(resp_failed)
    else:
        print(type(resp))
        status = {"status":"Success"}
        resp.append(status)
        with open("resp_sc_task.json","w") as write_resp:
            json.dump(resp,write_resp,indent=4)
        
        return jsonify(resp)
    
@app.route("/sc_req_items/")
def get_tasks():
    tasks = servicenowrequests("https://dev202603.service-now.com/")
    resp = tasks.get_details("sc_req_item",servicenow_username,servicenow_pass)
    if type(resp) is str:
        status = {"status":"Failed"}
        resp_failed = {"response":resp}|status
        return jsonify(resp_failed)
    else:
        print(type(resp))
        status = {"status":"Success"}
        resp.append(status)
        with open("resp_sc_task.json","w") as write_resp:
            json.dump(resp,write_resp,indent=4)
        return resp


@app.route("/incidents/summary/",methods=["POST"])
def summary():
    days = request.json["days"]
    return jsonify({"input":days})

if __name__ == "__main__":
    app.run(debug=True)
    logging.basicConfig(filename=f"logs//app-{date}.log",format='%(asctime)s %(message)s',filemode='a')
    app_logger = logging.getLogger()
    app_logger.setLevel(logging.DEBUG)
    app_logger.info("initallizing...")