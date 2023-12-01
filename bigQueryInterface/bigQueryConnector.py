from google.cloud import bigquery
import pandas as pd

# class BigQueryConnector:
#     def __init__(self,project_id):

#         self.client = bigquery.Client(project = project_id)
#         self.dataset = None
#         self.table = None

#     def list_datasets(self):
#         datasets = list(self.client.list_datasets())
#         return [dataset.dataset_id for dataset in datasets]
    
#     def connect_to_dataset(self,dataset_id):
#         self.dataset = self.client.dataset(dataset_id)

#     def connect_to_table(self,table_id):
#         if self.dataset is None:
#             raise Exception("Dataset should be connect before table")
        
#         self.table = self.dataset.table(table_id)

#     def get_table_data_as_dataframe(self,limit = None):
#         if self.table is  None:
#             raise Exception("Table is not connected")
        
#         query_job = self.client.list_rows(self.table,max_results=limit)

#         df = query_job.to_dataframe()

#         return df

class BigQueryConnector:
    def __init__(self):
        self.client = None
        self.dataset = None
        self.table = None
        self.df = None

    def connect_to_project(self, project_id):
        self.client = bigquery.Client(project=project_id)

    def connect_to_dataset(self, dataset_id):
        self.dataset = self.client.dataset(dataset_id)

    def connect_to_table(self, table_id):
        if self.dataset is None:
            raise Exception("Dataset should be connected before the table")
        self.table = self.dataset.table(table_id)

    def get_table_data_as_dataframe(self, limit=None):
        if self.table is None:
            raise Exception("Table is not connected")
        
        if self.df is not None:
            return self.df
        
        query_job = self.client.list_rows(self.table,max_results=limit)

        self.df = query_job.to_dataframe()

        return self.df