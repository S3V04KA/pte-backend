from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class TokenModel(BaseModel):
    access_token: str
    token_type: str

class myBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
        }
    )

class User(myBaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    favorates: Optional[list[str]] = []

class RegisterUser(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: str

class UserInDB(User):
    hashed_password: str
    created_at: datetime

class UserResponse(UserInDB):
    id: str|ObjectId = Field(alias="id", default=None, validation_alias='_id')

class Chapter(myBaseModel):
    name: str
    content: str

class ChapterResponse(Chapter):
    id: str|ObjectId = Field(alias="id", default=None, validation_alias='_id')
    
class ChapterResponseNoContent(ChapterResponse):
    content: None = None

class Section(myBaseModel):
    name: str
    content: list[ChapterResponse]|list[ChapterResponseNoContent] = []

class SectionResponse(Section):
    id: str|ObjectId = Field(alias="id", default=None, validation_alias='_id')

class Section(myBaseModel):
    name: str
    chapterIds: list[str]|None = []

class SectionResponse(Section):
    id: str|ObjectId = Field(alias="id", default=None, validation_alias='_id')
    chapters: list[ChapterResponse]|list[ChapterResponseNoContent] = []
    
class ChaptersManyRequest(BaseModel):
    ids: List[str] = []

class SearchResponse(myBaseModel):
    id: int
    chapterId: str
    chapterName: str
    sectionName: str