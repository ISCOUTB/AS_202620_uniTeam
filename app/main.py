from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "UniTeam API"}

@app.get("/activo")
def prueba():
    return {"status": "ok"}