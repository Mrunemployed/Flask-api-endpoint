import requests
import json
import pandas as pd
from manipulate import manipulate


class servicenowrequests():

    def __init__(self,url:str):
        self.url = str(url)
        print(url)

    def get_details(self,tablename:str,username:str,password:str,):
        base_url = self.url
        headers={"Accept":"application/json"}
        try:
                
            if base_url[-1::1] != "/":
                api_url= base_url+"/"+"api/now/table/{}".format(tablename)  
                response = requests.get(url=api_url, auth=(username,password),headers=headers, verify=False)
            elif base_url[-1::1] == "/":
                api_url= base_url+"api/now/table/{}".format(tablename)    
                response = requests.get(url=api_url, auth=(username,password),headers=headers, verify=False)
            else:
                return ("Method not defined")
            
            if response.status_code == 200:
                resp = response
                try:
                    # print("Status Code:",response.status_code)
                    response = response.json()
                except Exception as err:
                    return resp.text
                    # print(response.keys(),type(response))
                if "result" in response.keys():
                    mani = manipulate()
                    response = mani.resolve_api_dependencies(response["result"])
                    # print("Status Code:",response)
                    return(response)

                # print("passed successfully")
            else: 
                try:
                    response = response.json()
                    return response
                except Exception as err:
                        return err
                    
            
        except requests.exceptions.HTTPError or requests.exceptions.MissingSchema or Exception as httperr:
            print(httperr.args[0])
            return(httperr)
        
        



# incidents = servicenowrequests("https://dev167044.service-now.com/")
# resp = incidents.get_tasks_details("task","service_account","Capg@8420")
# with open("sample_resp.json","w") as print_json_resp_sample:
#     json.dump(resp,print_json_resp_sample,indent=4)
# print(resp)
