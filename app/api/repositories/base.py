from typing import Type , TypeVar , Generic , Optional , List , Dict , Any 
from beanie import Document
from pymango.results import DeleteResult , UpdateResult

T = TypeVar('T',bound=Document)

class BaseRepository(Generic[T]):
    def __init__(self,model:Type[T]):
        self.model = model

    async def create(self,document:T)->T:
        await document.insert()
        return document

    async def get_by_id(self,id:str)->Optional[T]:
        try:
            return await self.model.get(id)
        except:
            return None
    
    async def get_all(self,skip:int=0,limit:int=100)->List[T]:
        return await self.model.find().skip(skip).limit(limit).to_list()

    async def update(self,id:str,data:Dict[str,Any])->Optional[T]:
        doc = await self.get_by_id(id)
        if doc:
            await doc.set(data)
            return doc
        return None
    
    async def delete(self,id:str)->bool:
        doc = await self.get_by_id(id)
        if doc:
            await doc.delete()
            return True
        return False

    async def find_one(self,query:Dict[str,Any])->Optional[T]:
        return await self.model.find_one(query)

    async def find_many(self,query:Dict[str,Any],skip:int=0,limit:int=100)->List[T]:
        return await self.model.find(query).skip(skip).limit(limit).to_list()

    
    


    

