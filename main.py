from fastapi import FastAPI


app = FastAPI(title="FunktionsQL API", version="1.0.0")


@app.get("/")
async def healthcheck():
    return {"status": True}
