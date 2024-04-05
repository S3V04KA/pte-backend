from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.utils import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, authenticate_user, create_access_token, get_password_hash, oauth2_scheme
from app.DB import add_chapter, add_favorate_db, add_section, add_user, get_all_chapters, get_chapter, get_favorates, get_formated_chapter, get_section, get_sections, get_user, search
from app.Models import Chapter, ChapterResponse, ChapterResponseNoContent, RegisterUser, SearchResponse, Section, SectionResponse, TokenModel, UserInDB, UserResponse

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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
    await add_user(UserInDB(**user_dict))
    return {"message": "User successfully registered"}

@app.get('/chapter')
async def get_chapters() -> list[ChapterResponseNoContent]:
    return await get_all_chapters()

@app.get('/chapter/{chapter_id}')
async def get_highlighted_chapter(chapter_id: str, query: str | None = None, iter: int | None = None) -> ChapterResponse:
    if query is None and iter is None:
        return await get_chapter(chapter_id)
    else:
        return await get_formated_chapter(chapter_id, query, iter)

@app.get('/section')
async def get_sections_get() -> list[SectionResponse]:
    return await get_sections()

@app.get('/section/{section_id}')
async def get_section_from_id(section_id: str) -> SectionResponse:
    return await get_section(section_id)

@app.get('/search')
async def search_post(query: str) -> list[SearchResponse]:
    return await search(query)