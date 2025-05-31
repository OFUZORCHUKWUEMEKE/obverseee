from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from pymongo.collection import Collection
from bson import ObjectId
from fastapi import HTTPException

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, item: T) -> T:
        item_dict = item.dict()
        result = await self.collection.insert_one(item_dict)
        item_dict['_id'] = str(result.inserted_id)
        return item.__class__(**item_dict)

    async def get_by_id(self, id: str) -> Optional[T]:
        try:
            if not ObjectId.is_valid(id):
                raise HTTPException(status_code=400, detail="Invalid ID format")
            item = await self.collection.find_one({"_id": ObjectId(id)})
            if item:
                item['_id'] = str(item['_id'])
                return self.model(**item)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving item: {str(e)}")

    async def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            return [self.model(**{**item, '_id': str(item['_id'])}) for item in items]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving items: {str(e)}")

    async def update(self, id: str, item: T) -> Optional[T]:
        try:
            if not ObjectId.is_valid(id):
                raise HTTPException(status_code=400, detail="Invalid ID format")
            item_dict = item.dict(exclude_unset=True)
            result = await self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": item_dict}
            )
            if result.modified_count:
                updated_item = await self.collection.find_one({"_id": ObjectId(id)})
                updated_item['_id'] = str(updated_item['_id'])
                return self.model(**updated_item)
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")

    async def delete(self, id: str) -> bool:
        try:
            if not ObjectId.is_valid(id):
                raise HTTPException(status_code=400, detail="Invalid ID format")
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")

    @property
    def model(self):
        raise NotImplementedError("Subclasses must define the model property")