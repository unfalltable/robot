"""
基础数据访问层
"""
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """基础数据访问层"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """创建记录"""
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def get(self, id: Any) -> Optional[ModelType]:
        """根据ID获取记录"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """获取多条记录"""
        query = select(self.model)
        
        # 添加过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        # 添加排序
        if order_by:
            if order_by.startswith('-'):
                # 降序
                field = order_by[1:]
                if hasattr(self.model, field):
                    query = query.order_by(getattr(self.model, field).desc())
            else:
                # 升序
                if hasattr(self.model, order_by):
                    query = query.order_by(getattr(self.model, order_by))
        
        # 添加分页
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """更新记录"""
        # 先获取记录
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        # 更新字段
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: Any) -> bool:
        """删除记录"""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        await self.session.delete(db_obj)
        await self.session.commit()
        return True
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计记录数量"""
        query = select(func.count(self.model.id))
        
        # 添加过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """检查记录是否存在"""
        query = select(self.model.id)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar() is not None
    
    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """批量创建记录"""
        db_objects = [self.model(**obj) for obj in objects]
        self.session.add_all(db_objects)
        await self.session.commit()
        
        # 刷新所有对象
        for obj in db_objects:
            await self.session.refresh(obj)
        
        return db_objects
    
    async def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """批量更新记录"""
        if not updates:
            return 0
        
        # 假设每个更新字典都包含id字段
        updated_count = 0
        for update_data in updates:
            if 'id' not in update_data:
                continue
            
            obj_id = update_data.pop('id')
            if update_data:  # 如果还有其他字段需要更新
                result = await self.session.execute(
                    update(self.model)
                    .where(self.model.id == obj_id)
                    .values(**update_data)
                )
                updated_count += result.rowcount
        
        await self.session.commit()
        return updated_count
    
    async def bulk_delete(self, ids: List[Any]) -> int:
        """批量删除记录"""
        if not ids:
            return 0
        
        result = await self.session.execute(
            delete(self.model).where(self.model.id.in_(ids))
        )
        await self.session.commit()
        return result.rowcount
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """根据指定字段获取记录"""
        if not hasattr(self.model, field):
            return None
        
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()
    
    async def get_multi_by_field(
        self, 
        field: str, 
        values: List[Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """根据指定字段获取多条记录"""
        if not hasattr(self.model, field):
            return []
        
        result = await self.session.execute(
            select(self.model)
            .where(getattr(self.model, field).in_(values))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search(
        self, 
        search_fields: List[str], 
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """搜索记录"""
        if not search_fields or not search_term:
            return []
        
        # 构建搜索条件
        conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                field_attr = getattr(self.model, field)
                # 使用ILIKE进行不区分大小写的模糊搜索
                conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if not conditions:
            return []
        
        query = select(self.model).where(or_(*conditions))
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_latest(self, limit: int = 10, order_field: str = "created_at") -> List[ModelType]:
        """获取最新记录"""
        if not hasattr(self.model, order_field):
            order_field = "id"
        
        result = await self.session.execute(
            select(self.model)
            .order_by(getattr(self.model, order_field).desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_paginated(
        self, 
        page: int = 1, 
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """分页获取记录"""
        skip = (page - 1) * page_size
        
        # 获取记录
        items = await self.get_multi(
            skip=skip, 
            limit=page_size, 
            filters=filters, 
            order_by=order_by
        )
        
        # 获取总数
        total = await self.count(filters)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
