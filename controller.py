import pandas as pd
from datetime import datetime
import json
import logging

date = datetime.today()
date = datetime.strftime(date,"%d-%b-%Y")
logging.basicConfig(filename=f"logs//{date}.log",format='%(asctime)s %(message)s',filemode='a',encoding="utf-8")

class Controller():

    def __init__(self):
        self.date = datetime.now()
        print(self.date)
        self.open_tasks = r"tickets/open_tickets.csv"
        self.completed_tasks = r"tickets/completed_tickets.csv"

    def write_data(self,resp:dict,**kwargs):
        # data = json.loads(resp)
        df = pd.json_normalize(resp)
        df["description"].fillna("Empty",inplace=True)
        df = df[["number","opened_by","resolved_by","opened_at","closed_at","cmdb_ci","assignment_group","short_description","description","closed_by","assigned_to","close_notes"]]
        df.to_csv(self.open_tasks,mode="a",index=False,header=False)
        print("Data appended")

class ControllerCore(Controller):

    def __init__(self) -> None:
        super().__init__()
        self.set_conditions = dict()

    def read_data(self):
        df = pd.read_csv(self.open_tasks)
        return df
    
    def read_tasks_parse_info(self):
        try:
                
            with open(r"tickets/tasks/tasks-config.json", "r") as read_config:
                config = json.load(read_config)
            self.set_conditions = config
        except Exception as err:
            return err
    
    def main(self):
        try:

            df = self.read_data()
            if type(df) == pd.DataFrame():
                pass


        except Exception as err:
            return False


