from typing import Optional
from fastapi import FastAPI, HTTPException, Header, status

from app.schemas import BookUpdate, User, Book
from app.books import books
from typing import List


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
async def create_user(user_data: User):
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


#####################################
####Books Example Stars from here####
#####################################

@app.get('/books', response_model=List[Book])
async def get_all_books():
    return books


@app.post('/books', status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data: Book)->dict:
    books.append(book_data.model_dump())
    return books[-1]


@app.get('/books/{book_id}')
async def get_book(book_id: int)->dict:
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.patch('/books/{book_id}')
async def update_book(book_id: int, book_update_data: BookUpdate)->dict:
    for book in books:
        if book['id'] == book_id:
            # book['title'] = book_update_data.title
            # book['author'] = book_update_data.author
            # book['publisher'] = book_update_data.publisher
            # book['page_count'] = book_update_data.page_count
            # book['language'] = book_update_data.language
            for k, v in book_update_data.model_dump().items():
                book[k] = v
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.delete('/books/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return {}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

