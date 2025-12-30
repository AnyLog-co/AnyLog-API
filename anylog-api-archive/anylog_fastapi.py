import fastapi
import uvicorn

from anylog_connector import AnyLogConnector

app = fastapi.FastAPI()

CONN={}

@app.get("/")
def health():
    return {"message": "Hello, FastAPI!"}

@app.post("/copilot")
def copilot_query(query: str = Body(..., embed=True)):
    # crude mapping: look for "status on X"
    if query.lower().startswith("what is the status on"):
        node_id = query.split()[-1]  # last word = node_id
        if node_id in CONN:
            return CONN[node_id].get(command="get status")
        return {"message": f"Connection {node_id} not found"}
    return {"message": "Unsupported query"}


@app.post("/config/{node_id}/{conn}")
def config_node(node_id, conn):
    if node_id not in CONN:
        CONN[node_id] =  AnyLogConnector(conn=conn)

@app.get("/config")
def get_config():
    if not CONN:
        return {"message": "No connections"}
    output = {}
    for conn in CONN:
        output[conn] = CONN[conn].conn
    return output

@app.get("/status/{node_id}")
def get_config(node_id):
    if node_id in CONN:
        return CONN[node_id].get(command="get status")
    return {"message": f"Connection: {node_id} not found"}


if __name__ == "__main__":
    uvicorn.run(
        "anylog_fastapi:app",
        host="127.0.0.1",   # your IP / interface
        port=8080,        # your port
        reload=True
    )
