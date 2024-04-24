import asyncio
import json
import os
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.Models import Chapter, ChapterResponse, ChapterResponseNoContent, SearchResponse, Section, SectionResponse, UserInDB, UserResponse

MONGO_DETAILS = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@mongo:27017"
client = AsyncIOMotorClient(MONGO_DETAILS)
users_database = client.users
user_collection = users_database.get_collection("users_collection")
chapters_collection = users_database.get_collection("chapters_collection")
sections_collection = users_database.get_collection("sections_collection")

paths = [
    'РАЗДЕЛ 1. СТРУКТУРА И ОРГАНИЗАЦИЯ УПРАВЛЕНИЯ',
    'РАЗДЕЛ 2. ОСНОВНОЕ ПРОИЗВОДСТВО',
    'РАЗДЕЛ 3. ВСПОМОГАТЕЛЬНЫЕ СЛУЖБЫ',
    'РАЗДЕЛ 4. ЭКОЛОГИЧЕСКАЯ БЕЗОПАСНОСТЬ',
    'РАЗДЕЛ 5. КОНТРОЛЬ ПРОИЗВОДСТВА',
    'Приложение 1',
    'Приложение 2',
    'Приложение 3',
    'ЗАКЛЮЧЕНИЕ'
]

async def init():
    length = len(await sections_collection.find().to_list(10))
    if length == 0:
        for i in paths:
            chapters = []
            for root, dirs, files in os.walk(f'./docs/{i}'):
                for file in files:
                    with open(f'./docs/{i}/{file}', 'r') as f:
                        chapters.append(Chapter(name=file.split('.')[0], content=json.loads(f.read())))
            chapters.sort(key=lambda chapter: chapter.name)
            chs = await chapters_collection.insert_many(chapters)
            section = await sections_collection.insert_one(Section(name=i, chapterIds=chs.inserted_ids).model_dump())
    
asyncio.create_task(init())

async def add_user(user_data: UserInDB):
    user = await user_collection.insert_one(user_data.model_dump())
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return new_user

async def get_user(username: str):
    user = await user_collection.find_one({"username": username})
    if user:
        user = UserResponse(**user)
        return user
    return None

async def get_favorates(username: str):
    user = await user_collection.find_one({"username": username})
    if not user:
        return None
    favorates = []
    for i in user['favorates']:
        chapter = await chapters_collection.find_one({"_id": ObjectId(i)})
        favorates.append(ChapterResponse(**chapter))
    return favorates

async def add_favorate_db(username: str, chapter_id: str):
    user = await user_collection.find_one({"username": username})
    if not user:
        return None
    if not chapter_id in user['favorates']:
        user['favorates'].append(chapter_id)
        await user_collection.update_one({"_id": user['_id']}, {"$set": {"favorates": user['favorates']}})
    return await get_favorates(username)

async def add_chapter(chapter_data: Chapter):
    chapter = await chapters_collection.insert_one(chapter_data.model_dump())
    new_chapter = await chapters_collection.find_one({"_id": chapter.inserted_id})
    return new_chapter

async def get_all_chapters():
    chapters = []
    async for chapter in chapters_collection.find():
        chapters.append(ChapterResponseNoContent(id=str(chapter['_id']), name=chapter['name']))
    return chapters

async def get_chapter(chapter_id: str):
    chapter: ChapterResponse = await chapters_collection.find_one({"_id": ObjectId(chapter_id)})
    if not chapter:
        return None
    chapter['id'] = str(chapter['_id'])
    del chapter['_id']
    return chapter

async def get_many_chapters(chapter_ids: list[str]):
    chapters = []
    ids = list(map(lambda v: ObjectId(v), chapter_ids))
    finded = chapters_collection.find({"_id": {"$in": ids}})
    async for chapter in finded:
        id = str(chapter['_id'])
        ch = {'name': chapter['name'], 'id': id}
        chapters.append(dict(ch))
    return chapters

async def add_section(section_data: Section):
    section = await sections_collection.insert_one(section_data.model_dump())
    new_section = await sections_collection.find_one({"_id": section.inserted_id})
    new_section['id'] = str(new_section['_id'])
    del new_section['_id']
    return new_section

async def get_sections():
    sections = []
    async for section in sections_collection.find():
        sections.append(SectionResponse(**section))
    return sections

async def get_section(section_id: str):
    section = await sections_collection.find_one({"_id": ObjectId(section_id)})
    if not section:
        return None
    section['chapters'] = (await get_many_chapters(section['chapterIds']))
    section['chapterIds'] = None
    # section['id'] = str(section['_id'])
    # del section['_id']
    return SectionResponse(chapters=section['chapters'], chapterIds=None, id=section['id'], name=section['name'])

async def find_substring_in_content(elements, substring, new_class, modified_elements=None):
    if modified_elements is None:
        modified_elements = []
    for element in elements:
        if "content" in element:
            for content_item in element["content"]:
                if isinstance(content_item, str) and substring.lower() in content_item.lower():
                    if "class" in element and element["class"] != new_class:
                        element["class"] += ' '+new_class
                        modified_elements.append({'el': element, 'iter': len(modified_elements)})  # Добавляем изменённый элемент в список
                    break  
            await find_substring_in_content(element["content"], substring, new_class, modified_elements)
    return modified_elements

async def update_class_value_if_substring_in_content(elements, substring, new_class):
    for element in elements:
        if "content" in element:
            for content_item in element["content"]:
                if isinstance(content_item, str) and substring.lower() in content_item.lower():
                    if "class" in element:
                        element["class"] += ' '+new_class
                    break  
            await update_class_value_if_substring_in_content(element["content"], substring, new_class)

async def search(substring: str):
    searchs = []
    chapters = []
    async for chapter in chapters_collection.find():
        section = await sections_collection.find_one({'chapterIds': chapter['_id']})
        chapters.append({'name': chapter['name'], 'id': str(chapter['_id']), 'content': chapter['content'], 'sectionName': section['name']})
    cnt = 0
    for i in range(len(chapters)):
        modified_elements = await find_substring_in_content(chapters[i]['content'], substring, 'highlighted')
        for j in range(len(modified_elements)):
            searchs.append(SearchResponse(id=cnt, chapterId=chapters[i]['id'], chapterName=chapters[i]['name'], iter=modified_elements[j]['iter'], contentElement=modified_elements[j]['el'], sectionName=chapters[i]['sectionName']))
            cnt+=1
    return searchs

async def get_formated_chapter(chapter_id: str, substring: str, iter: int):
    chapter = await chapters_collection.find_one({"_id": ObjectId(chapter_id)})
    if not chapter:
        return None
    content = chapter['content']
    await update_class_value_if_substring_in_content(content, substring, 'highlighted')
    json_str = json.dumps(content, ensure_ascii=False).replace(' highlighted', '', iter).replace('highlighted', 'Temp', 1).replace(' highlighted', '').replace('Temp', 'highlighted', 1)
    return ChapterResponse(id=str(chapter['_id']), name=chapter['name'], content=json.loads(json_str))