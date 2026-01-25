import azure.functions as func
import logging
import json
import os
from azure.cosmos import CosmosClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="save_to_cosmos", methods=["POST"])
def save_to_cosmos(req: func.HttpRequest) -> func.HttpResponse:
    """Save a value to Cosmos DB."""
    logging.info('Saving data to Cosmos DB.')
    
    try:
        # Get Cosmos DB connection details from environment
        cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
        cosmos_key = os.getenv('COSMOS_KEY')
        database_name = os.getenv('COSMOS_DATABASE', 'VisitorDatabase')
        container_name = os.getenv('COSMOS_CONTAINER', 'Visitors')
        
        # Create Cosmos client
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Get data from request body
        req_body = req.get_json()
        
        # Save to Cosmos DB
        response = container.create_item(body=req_body)
        
        return func.HttpResponse(
            json.dumps({"status": "success", "id": response.get('id')}),
            status_code=201,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error saving to Cosmos DB: {str(e)}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e)}),
            status_code=500,
            mimetype="application/json"
        )