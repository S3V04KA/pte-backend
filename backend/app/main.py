from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, WebSocket, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from h2o_lightwave import wave_serve
from h2o_lightwave_web import web_directory
from app.usersPage import serve_users
from app.utils import ALGORITHM, SECRET_KEY, authenticate_user, create_access_token, get_password_hash, oauth2_scheme
from app.DB import add_favorate_db, delete_user, get_users, add_user, delete_favorate_db, get_all_chapters, get_chapter, get_favorates, get_section, get_sections, get_user, search
from app.Models import ChapterResponse, ChapterResponseNoContent, RegisterUser, SearchResponse, SectionResponse, TokenModel, UserInDB, UserResponse

app = FastAPI()

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenModel:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users")
async def read_users() -> list[UserResponse]:
    users = await get_users()
    return users

@app.websocket('/users_menu/')
async def ws(ws: WebSocket):
    try:
        await ws.accept()
        await wave_serve(serve_users, ws.send_text, ws.receive_text)
        await ws.close()
    except:
        pass

@app.delete('/users')
async def delete_user_api(username: str) -> bool:
    return await delete_user(username)

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data)
    if user is None:
        raise credentials_exception
    return user

@app.post('/users/favorates/{chapter_id}')
async def add_favorate(chapter_id: str, token: str = Depends(oauth2_scheme)) -> list[ChapterResponse]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    favorates = await add_favorate_db(token_data, chapter_id)
    if favorates is None:
        raise credentials_exception
    return favorates

@app.get('/view/{chapter_id}', response_class=HTMLResponse)
async def view(chapter_id: str) -> HTMLResponse:
    chapter = await get_chapter(chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter['content']

@app.delete('/users/favorates/{chapter_id}')
async def delete_favorate(chapter_id: str, token: str = Depends(oauth2_scheme)) -> list[ChapterResponse]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    favorates = await delete_favorate_db(token_data, chapter_id)
    if favorates is None:
        raise credentials_exception
    return favorates

@app.get('/users/favorates')
async def get_favorates_get(token: str = Depends(oauth2_scheme)) -> list[ChapterResponse]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    favorates = await get_favorates(token_data)
    if favorates is None:
        raise credentials_exception
    return favorates

@app.post("/register")
async def register_user(user: RegisterUser):
    userF = await get_user(user.username)
    if userF:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = await get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict.update({"hashed_password": hashed_password})
    # Удалите пароль в открытом виде из словаря, чтобы не сохранять его
    del user_dict["password"]
    user_dict['disabled'] = False
    await add_user(UserInDB(created_at=datetime.now(), **user_dict))
    return {"message": "User successfully registered"}

@app.get('/chapter')
async def get_chapters() -> list[ChapterResponseNoContent]:
    return await get_all_chapters()

@app.get('/chapter/{chapter_id}')
async def get_highlighted_chapter(chapter_id: str) -> ChapterResponse:
    return await get_chapter(chapter_id)

@app.get('/section')
async def get_sections_get() -> list[SectionResponse]:
    return await get_sections()

@app.get('/section/{section_id}')
async def get_section_from_id(section_id: str) -> SectionResponse:
    return await get_section(section_id)

@app.get('/search')
async def search_post(query: str) -> list[SearchResponse]:
    return await search(query)

app.mount('/images', StaticFiles(directory='./images'), name='images')
app.mount('/documents', StaticFiles(directory='./docs'), name='docs')
app.mount('/', StaticFiles(directory=web_directory, html=True), name='/')