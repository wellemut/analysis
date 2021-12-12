from fastapi import FastAPI

api = FastAPI()


@api.get("/")
def root():
    return {"message": "Hello world! :)"}