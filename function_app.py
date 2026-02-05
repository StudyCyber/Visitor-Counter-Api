import logging
import json
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="incrementVisitor", methods=["POST"])
@app.table_output(
    arg_name="tableOutput",
    connection="CosmosDBConnection",
    table_name="COSMOS_CONTAINER"
)
def increment_visitor(
    req: func.HttpRequest,
    tableOutput: func.Out[str]
) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        visitor_id = req_body.get("id")

        if not visitor_id:
            return func.HttpResponse("Missing 'id' in request body", status_code=400)

        count = req_body.get("count", 0) + 1

        entity = {
            "PartitionKey": "visitor",
            "RowKey": visitor_id,
            "count": count
        }

        tableOutput.set(json.dumps(entity))

        return func.HttpResponse(
            f"Visitor count incremented to {count}",
            status_code=200
        )

    except Exception:
        logging.exception("Error updating counter")
        return func.HttpResponse("Error updating counter", status_code=500)
