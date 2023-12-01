from flask import Flask, request, jsonify
from flasgger import Swagger
import pandas as pd
import yaml
import os
from bigQueryInterface.bigQueryConnector import BigQueryConnector
from config import project_id, dataset_id, table_id

app = Flask(__name__)


# Load YAML specification from file
with open('api_documentation.yaml', 'r') as file:
    swagger_config = yaml.safe_load(file)

Swagger(app, template=swagger_config)



bq_connector = BigQueryConnector()
bq_connector.connect_to_project(project_id)
bq_connector.connect_to_dataset(dataset_id)
bq_connector.connect_to_table(table_id)


@app.route('/connect_to_project', methods=['GET'])
def connect_to_project():
    
    try:
        project_id = request.args.get('project_id')

        bq_connector.connect_to_project(project_id)

        return jsonify({'success': True, 'message': f'Connected to project {project_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/connect_to_dataset', methods=['GET'])
def connect_to_dataset():
   
    try:
        dataset_id = request.args.get('dataset_id')

        bq_connector.connect_to_dataset(dataset_id)

        return jsonify({'success': True, 'message': f'Connected to dataset {dataset_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/connect_to_table', methods=['GET'])
def connect_to_table():
    
    try:
        table_id = request.args.get('table_id')

        bq_connector.connect_to_table(table_id)

        return jsonify({'success': True, 'message': f'Connected to table {table_id}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_table_data', methods=['GET'])
def get_table_data():
    try:
        limit = request.args.get('limit', default=10, type=int)

        df = bq_connector.get_table_data_as_dataframe(limit)
        data = df.to_dict(orient='records')

        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/filter_table_data', methods=['GET'])
def filter_table_data():
    try:
        # Get dynamic filters from query parameters
        filters = {param: request.args.get(param) for param in request.args}

        df = bq_connector.get_table_data_as_dataframe()

        # Validate filters against DataFrame columns
        invalid_filters = [key for key in filters if key not in df.columns]
        if invalid_filters:
            raise ValueError(f"Invalid filter(s): {', '.join(invalid_filters)}")

        # Validate and apply dynamic filters to the DataFrame
        for key, value in filters.items():
            if key not in df.columns:
                raise ValueError(f"Invalid filter: {key}")
            df = df[df[key] == value]

        # Convert the filtered DataFrame to a list of records
        data = df.to_dict(orient='records')

        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/filter_row_data', methods=['GET'])
def filter_row_data():
    try:
        # Get the 'search_value' query parameter
        search_value = request.args.get('search_value', None)

        if search_value is None:
            raise ValueError("Missing 'search_value' parameter")

        df = bq_connector.get_table_data_as_dataframe()

        # Perform search on all columns for the specified value
        matching_rows = df[df.apply(lambda row: any(str(search_value) in str(cell) for cell in row), axis=1)]

        # Convert the matching rows to a list of records
        data = matching_rows.to_dict(orient='records')

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
