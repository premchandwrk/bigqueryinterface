from flask import Flask, request, jsonify
from flasgger import Swagger
from google.cloud import bigquery
import yaml

app = Flask(__name__)

# Load YAML specification from file
with open('api_documentation.yaml', 'r') as file:
    swagger_config = yaml.safe_load(file)

app.config['SWAGGER'] = {
    'title': 'BigQuery API with Flask',
    'uiversion': 3,
    'spec': swagger_config
}

Swagger(app)

class BigQueryConnector:
    def __init__(self):
        self.client = None
        self.dataset = None

    def connect_to_project(self, project_id):
        self.client = bigquery.Client(project=project_id)

    def connect_to_dataset(self, dataset_id):
        self.dataset = self.client.dataset(dataset_id)

    def connect_to_table(self, table_id):
        if self.dataset is None:
            raise Exception("Dataset should be connected before the table")
        table_ref = self.dataset.table(table_id)
        table = self.client.get_table(table_ref)
        return table

    def get_table_data_as_dataframe(self, table, limit=None):
        query_job = self.client.list_rows(table, max_results=limit)
        df = query_job.to_dataframe()
        return df

bq_connector = BigQueryConnector()
current_table_id = None

@app.route('/connect_to_project', methods=['GET'])
def connect_to_project():
    """
    Connect to a BigQuery project.
    ---
    parameters:
      - name: project_id
        in: query
        type: string
        required: true
        description: The BigQuery project ID.
    responses:
      200:
        description: Successful connection to the BigQuery project.
    """
    try:
        project_id = request.args.get('project_id')

        bq_connector.connect_to_project(project_id)

        return jsonify({'success': True, 'message': f'Connected to project {project_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/connect_to_dataset', methods=['GET'])
def connect_to_dataset():
    """
    Connect to a BigQuery dataset.
    ---
    parameters:
      - name: dataset_id
        in: query
        type: string
        required: true
        description: The BigQuery dataset ID.
    responses:
      200:
        description: Successful connection to the BigQuery dataset.
    """
    try:
        dataset_id = request.args.get('dataset_id')

        bq_connector.connect_to_dataset(dataset_id)

        return jsonify({'success': True, 'message': f'Connected to dataset {dataset_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/connect_to_table', methods=['GET'])
def connect_to_table():
    """
    Connect to a BigQuery table.
    ---
    parameters:
      - name: table_id
        in: query
        type: string
        required: true
        description: The BigQuery table ID.
    responses:
      200:
        description: Successful connection to the BigQuery table.
    """
    try:
        global current_table_id
        current_table_id = request.args.get('table_id')

        table = bq_connector.connect_to_table(current_table_id)

        return jsonify({'success': True, 'message': f'Connected to table {current_table_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_table_data', methods=['GET'])
def get_table_data():
    """
    Get data from a specified BigQuery table.
    ---
    parameters:
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
        description: The maximum number of rows to retrieve.
    responses:
      200:
        description: A list of records from the specified BigQuery table.
    """
    try:
        global current_table_id
        limit = request.args.get('limit', default=10, type=int)

        if current_table_id is None:
            return jsonify({'success': False, 'error': 'Table ID not provided. Connect to a table first.'})

        table = bq_connector.connect_to_table(current_table_id)
        df = bq_connector.get_table_data_as_dataframe(table, limit)
        data = df.to_dict(orient='records')

        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
