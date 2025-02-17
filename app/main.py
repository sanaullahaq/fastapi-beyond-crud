# from typing import List
from typing import Optional
from fastapi import FastAPI, Header

# from app.crud import create_items, get_items
# from app.models import Item, items
from app.schemas import UserSchema

app = FastAPI()

@app.get('/')
async def read_root():
    return {"message": "Hello World!"}


#path parameters example
@app.get('/greet/{username}')
async def greet(username: str):
    return {"message": f"Hello {username}"}


#optional parameters example
@app.get('/greet/')
async def greet(username: Optional[str]="User"):
    return {"message": f"Hello {username}"}


user_list = ["Sanaulla", "Emon", "Akib"]


#query params example
@app.get('/search')
async def search_for_user(username: str):
    if username in user_list:
        return {"message": f"details for user {username}"}
    else:
        return {"message": "details not found!"}


users = []


@app.post('/create_user')
async def create_user(user_data: UserSchema):
    new_user = {
        'username': user_data.username,
        'email': user_data.email
    }
    # users.append(UserSchema(**user_data.model_dump()))
    # print(users)
    users.append(new_user)
    return {'message':'User Created Successfully!', 'user': users[-1]}


# inspect the headers information
@app.get('/get_headers')
async def get_all_request_headers(
    user_agent: Optional[str] = Header(None),
    accept_encoding: Optional[str] = Header(None),
    referer: Optional[str] = Header(None),
    connection: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    host: Optional[str] = Header(None),
    accept: Optional[str] = Header(None),
):
    request_headers = {}
    request_headers["User-Agent"] = user_agent
    request_headers["Accept-Encoding"] = accept_encoding
    request_headers["Referer"] = referer
    request_headers["Accept-Language"] = accept_language
    request_headers["Connection"] = connection
    request_headers["Host"] = host
    request_headers["Accept"] = accept

    return request_headers