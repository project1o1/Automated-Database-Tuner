import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strategy import localOptimalStrategy

SIZE = 400
MIN_DIFF = 0.5

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class Query(BaseModel):
    query: str
    columns: str
    cost: int

@app.get("/new_query")
async def execute_sql_query(request: Request):
    try:
        query_params = request.query_params
        query = query_params["query"]
        columns = query_params["columns"]
        cost = query_params["cost"]
        if not (query and columns and cost):
            raise HTTPException(status_code=400, detail="Missing query parameters")
        
        query_dict = {
            "query": query,
            "cost": cost,
            "columns": columns.split(",")
        }
        # import threading
        # threading.Thread(target=localOptimalStrategy, args=(query_dict, SIZE, MIN_DIFF)).start()
        localOptimalStrategy(query_dict, SIZE, MIN_DIFF)
        return {"message": "Parameters received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    print("Running server")
    uvicorn.run(app, host="0.0.0.0", port=8000)


# localOptimalStrategy({"query":"SELECT first_name, first_name, first_name, age, username FROM users  WHERE user_id <= 85",
#                       "columns":["user_id"],
#                       "cost": 1000}, 400, 0.5)