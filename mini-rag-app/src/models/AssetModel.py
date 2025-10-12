from .BaseDataModel import BaseDataModel
from models.db_scehmes.project import Project
from models.enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId
from models.db_scehmes.asset import Asset

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        # only initiates at the first project creation only >> Need to clean up database and docker before start running it
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    
    # Very important as we can not recall async function from insider init
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client = db_client)
        await instance.init_collection()
        return instance 


    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        records = await self.collection.find({"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
                                             "asset_type": asset_type}).to_list(length=None)
        return [Asset(**record) for record in records]


    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one({"asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
                                                 "asset_name": asset_name})
        if record is None:
            return None
        return Asset(**record)