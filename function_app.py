import logging
import azure.functions as func
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel)

@app.route(route="incrementVisitor", methods=["POST"])
@app.cosmos_db_output(arg_name="cosmosOutput",
                      connection="CosmosDBConnection",
                      database_name="VisitorDatabase",
                      container_name="Visitors")
def increment_visitor(req: func.HttpRequest, cosmosOutput: func.Out[dict]) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        visitor_id = req_body.get("id")
        
        if not visitor_id:
            return func.HttpResponse("Missing 'id' in request body", status_code=400)
        
        # Increment the counter
        document = {
            "id": visitor_id,
            "count": req_body.get("count", 0) + 1
        }
        
        # Write updated document to Cosmos DB
        cosmosOutput.set(document)
        
        return func.HttpResponse(f"Visitor count incremented to {document['count']}", status_code=200)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse("Error updating counter", status_code=400)