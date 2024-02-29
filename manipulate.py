import json
from datetime import timedelta,datetime
from typing_extensions import TypedDict
import requests
from json import JSONDecodeError
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

date = datetime.today()
date = datetime.strftime(date,"%d-%b-%Y")
logging.basicConfig(filename=f"logs//{date}.log",format='%(asctime)s %(message)s',filemode='a',encoding="utf-8")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
requests.Session

class Options(TypedDict):
   convert_to_datetime: str
   opened_at: str
   closed_at: str

class manipulate():
   
    def __init__(self):
        self.session = requests.Session()
        headers={"Accept":"application/json"}
        username = "service_account"
        password = "Flask@123"
        self.session.auth = (username,password)
        self.adap = requests.adapters.HTTPAdapter(pool_maxsize=10,pool_connections=10)
        self.session.mount("https://",self.adap)
        self.session.headers = headers
        self.session.verify = False
        self.workers = 10

    def datetime_operations(self,convert_datetime: bool,**kwargs:Options)->None:

        date_format = "%Y-%m-%d %H:%M:%S"
        if convert_datetime:
            # print("passed")
            convert_to_datetime = kwargs.get("convert_to_datetime",str)
            converted = datetime.strptime(convert_to_datetime,date_format) 
            return converted       

        else:
                
            opened_at = kwargs.get("opened_at",str)
            closed_at = kwargs.get("closed_at",str)
            opened_at_formatted = datetime.strptime(opened_at,date_format)
            closed_at_formatted = datetime.strptime(closed_at,date_format)
            elapse_time = closed_at_formatted - opened_at_formatted
            # print(opened_at,closed_at)
            return elapse_time
        
    def get_from_time_period(self,days:int):

        from_start_date = datetime.now() - timedelta(days=days)
        return from_start_date
        
    def get_incidents_within_days(self,days:int,resp):

        filter_start_date = self.get_from_time_period(days)
        for i in resp["result"]:
            i_keys = i.keys()
            nested_elements = {"elem":[p for p in i_keys if (isinstance(i[p],dict))]for p in i}
            # print(nested_elements)
            resolve_dependencies = self.resolve_api_dependencies(i,nested_elements)
            break 
        # return a
        format_datetime = self.datetime_operations(True,convert_to_datetime=i["opened_at"])

# Function to be used as a process to be mapped with thread dispatcher  
    def get_fn(self,url,retries=0):
        retry_limit = 10
        try:
                
            url_key = list(url)[0]
            logger.info(f"retries: {retries} {current_thread().getName()} URL GOT FOR Thread:{url} {url_key}")
            base_url = url[url_key]
            resp = self.session.get(url=base_url)
            if resp.status_code == 200 and retries<retry_limit:
                resp = resp.json()
                if "error" in resp.keys():
                    return {url_key:resp["error"]["message"]}
                elif "name" not in resp["result"].keys():
                    return {url_key:"Could Not be resolved"}
                else:
                    return {url_key:resp["result"]["name"]}
            elif resp.status_code == 404 and retries<retry_limit:
                resp = resp.json()
                if "error" in resp.keys():
                    return {url_key:resp["error"]["message"]}
                else:
                    return {url_key:"Could Not be resolved"}
            elif retries<retry_limit:
                retries = retries+1
                c = self.get_fn(url,retries=retries)
                return c
            else:
                return {url_key: f"Error : Max retries exceeded status code:{resp.status_code} resp: {resp.text}"}
            return resp
        except Exception as err:
            with open("logs//response-dump.txt","a") as dump:
                dump.writelines(f"Error: {err} |  retries: {retries} {current_thread().getName()} URL GOT FOR Thread:{url} {url_key}\n")
            return {url_key: f"Error : {err}"}

# Function for thread execution in batch
    def api_threads_executor(self,ticket:dict):
        
        ticket_keys = ticket.keys()
        #Tto be used in case of reverting back to old model of threading without Sub-threads
        # key = {"elem":[p for p in ticket_keys if (isinstance(ticket[p],dict))]for p in ticket} 
        key = key = [p for p in ticket_keys if (isinstance(ticket[p],dict))]
        #Transform the ticket data to a list[Dictionary] with the field name as a dict key containing a nested dictionary
        list_dependencies_with_keys = [{key[i]:ticket[key[i]]}for i in range(len(key))]
        #Callback to parent function to create subthreads **bit messy
        fetch_values_of_dependencies = self.sub_threads(sub_pool_data=list_dependencies_with_keys)
        logger.info(f"{current_thread().getName()} {fetch_values_of_dependencies}")

        # print(list_try)
        for i in fetch_values_of_dependencies:
            if list(i)[0] in ticket.keys():
                logger.info(f"Writing values into keys {current_thread().getName()} i:{i} list(i):{list(i)} list(i)[0]:{list(i)[0]} ticket[list(i)[0]]:{ticket[list(i)[0]]}")
                ticket[list(i)[0]] = next(iter(i.values()))
                logger.info(f"New Value ticket[list(i)[0]]:{ticket[list(i)[0]]}")
                
            else:
                pass
            logger.info(f"Value of Ticket being returned {current_thread().getName()} {ticket}")
        return ticket
    

    def sub_threads(self,sub_pool_data):
        #transform the listed[dictionary data] from a list of nested dictionary to
        #  a list of dictionary with key as field name and value as the link url 
        sub_urls = [{list(i)[0]:i[list(i)[0]]["link"]} for i in sub_pool_data]
        with ThreadPoolExecutor(max_workers=10) as sub_pool:
            results = sub_pool.map(self.get_fn,sub_urls)
            sub_pool.shutdown(wait=True, cancel_futures=False)
            return list(results)

#Multithread Dispatch Function to resolve all dependencies that come as a nested child value pair when get Incidents/get Requests API called.
    def resolve_api_dependencies(self,tickets=None,call_type=None,sub_pool_data=None):

        try:
        
            with ThreadPoolExecutor(max_workers=20) as pool:
                urls = tickets
                results = pool.map(self.api_threads_executor,tickets)
                pool.shutdown(wait=True, cancel_futures=False)
                return list(results)

        except JSONDecodeError or requests.HTTPError as err:
            return err.msg
        


    def resolve_dependencies_single_thread(self,tickets:dict):
        try:
            for c,ticket in enumerate(tickets):
                ticket_keys = ticket.keys()
                key = {"elem":[p for p in ticket_keys if (isinstance(ticket[p],dict))]for p in ticket}
                logger.info(f"{ticket}")
                # json_resp_keys = json_resp.keys()
                # if key in json_resp_keys:
                for i in key["elem"]:
                    # print(i)
                    # print(ticket[i], type(ticket[i]))
                    # print(ticket[i]['link'])
                    url = ticket[i]['link']
                    resp = self.session.get(url=url)
                    resp = resp.json()
                    # print(resp)
                    if "error" in resp.keys():
                        tickets[c][i] = resp["error"]["message"]  
                    elif "name" not in resp["result"].keys():
                        tickets[c][i] = "Could Not be resolved"
                    else:
                        tickets[c][i] = resp["result"]["name"]
                    
                
                # print(json.dumps(tickets,indent=4))
            return tickets
                # else:
                #     return "key not found"
        except JSONDecodeError or requests.HTTPError as err:
            return err.msg