import json
from datetime import timedelta,datetime
from typing_extensions import TypedDict
import requests
from json import JSONDecodeError
from requests import HTTPError

class Options(TypedDict):
   convert_to_datetime: str
   opened_at: str
   closed_at: str

with open("resp.json","r") as api_resp:
    resp = json.load(api_resp)

def datetime_operations(convert_datetime: bool,**kwargs:Options)->None:
    date_format = "%Y-%m-%d %H:%M:%S"
    if convert_datetime:
        print("passed")
        convert_to_datetime = kwargs.get("convert_to_datetime",str)
        converted = datetime.strptime(convert_to_datetime,date_format) 
        return converted       

    else:
            
        opened_at = kwargs.get("opened_at",str)
        closed_at = kwargs.get("closed_at",str)
        opened_at_formatted = datetime.strptime(opened_at,date_format)
        closed_at_formatted = datetime.strptime(closed_at,date_format)
        elapse_time = closed_at_formatted - opened_at_formatted
        print(opened_at,closed_at)
        return elapse_time

def get_from_time_period(days:int):
    from_start_date = datetime.now() - timedelta(days=days)
    return from_start_date

def get_incidents_within_days(days:int):
    filter_start_date = get_from_time_period(days)
    for i in resp["result"]:
        i_keys = i.keys()
        nested_elements = {"elem":[p for p in i_keys if (isinstance(i[p],dict))]for p in i}
        print(nested_elements)
        resolve_dependencies = resolve_api_dependencies(i,nested_elements)
        break 
    # return a
    format_datetime = datetime_operations(True,convert_to_datetime=i["opened_at"])

def resolve_api_dependencies(json_resp:dict,key:dict[list]):
    try:
        headers={"Accept":"application/json"}
        username = "service_account"
        password = "Capg@8420"
        # json_resp_keys = json_resp.keys()
        # if key in json_resp_keys:
        for i in key["elem"]:
            print(i)
            print(json_resp[i])
            url = json_resp[i]['link']
            resp = requests.get(url=url,auth=(username,password),headers=headers,verify=False)
            resp = resp.json()
            print(i)
            if "error" in resp.keys():
                json_resp[i] = resp["error"]["message"]   
            else:
                json_resp[i] = resp["result"]["name"]
        
        print(json.dumps(json_resp,indent=4))
        return json_resp
        # else:
        #     return "key not found"

    except JSONDecodeError or HTTPError as err:
        return err.msg


    
c = get_incidents_within_days(3)
# print("result:",c)