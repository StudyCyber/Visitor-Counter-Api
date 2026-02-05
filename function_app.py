import logging
import json
import os
import azure.functions as func
from azure.data.tables import TableServiceClient, TableEntity
from azure.core.exceptions import ResourceNotFoundError

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="incrementVisitor", methods=["POST"])
def increment_visitor(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        visitor_id = req_body.get("id")

        if not visitor_id:
            return func.HttpResponse("Missing 'id' in request body", status_code=400)

        # Connect to table storage (Cosmos DB Table API)
        connection_string = os.environ.get("CosmosDBConnection", "UseDevelopmentStorage=true")
        table_service = TableServiceClient.from_connection_string(connection_string)
        table_client = table_service.get_table_client("VisitorCounter")

        # Create table if it doesn't exist
        try:
            table_client.create_table()
        except:
            pass  # Table might already exist

        # Try to get existing visitor count
        try:
            entity = table_client.get_entity(partition_key="visitor", row_key=visitor_id)
            count = entity["count"] + 1
        except ResourceNotFoundError:
            count = 1

        # Update or create the entity
        entity = TableEntity()
        entity["PartitionKey"] = "visitor"
        entity["RowKey"] = visitor_id
        entity["count"] = count

        table_client.upsert_entity(entity)

        return func.HttpResponse(
            json.dumps({"visitor_id": visitor_id, "count": count}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Error updating counter")
        return func.HttpResponse(f"Error updating counter: {str(e)}", status_code=500)
