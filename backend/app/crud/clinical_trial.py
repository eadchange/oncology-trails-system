"""
临床研究相关CRUD操作
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.clinical_trial import (
    Study,
    Intervention,
    Condition,
    MolecularTarget,
    Outcome,
    Result,
    Publication
)
from app.schemas.clinical_trial import StudyCreate, StudyUpdate


class CRUDStudy(CRUDBase[Study, StudyCreate, StudyUpdate]):
    """
    研究的CRUD操作
    """
    
    async def get_by_nct_id(self, db: AsyncSession, nct_id: str) -> Optional[Study]:
        """
        根据NCT ID获取研究
        """
        stmt = select(Study).where(Study.nct_id == nct_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search_studies(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Study], int]:
        """
        搜索研究
        
        Args:
            db: 数据库会话
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            size: 每页数量
            sort_by: 排序字段
            sort_order: 排序方向
            
        Returns:
            (研究列表, 总数) 元组
        """
        # 基础查询
        stmt = select(Study).where(Study.is_active == True)
        
        # 全文搜索
        if query:
            search_terms = query.split()
            conditions = []
            for term in search_terms:
                term_conditions = [
                    Study.official_title.ilike(f"%{term}%"),
                    Study.brief_title.ilike(f"%{term}%"),
                    Study.acronym.ilike(f"%{term}%"),
                    Study.brief_summary.ilike(f"%{term}%"),
                    Study.nct_id.ilike(f"%{term}%")
                ]
                conditions.append(or_(*term_conditions))
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        # 应用筛选条件
        if filters:
            # 研究阶段筛选
            if filters.get("phase"):
                stmt = stmt.where(Study.phase.in_(filters["phase"]))
            
            # 研究状态筛选
            if filters.get("status"):
                stmt = stmt.where(Study.status.in_(filters["status"]))
            
            # 研究类型筛选
            if filters.get("study_type"):
                stmt = stmt.where(Study.study_type.in_(filters["study_type"]))
            
            # 时间范围筛选
            if filters.get("start_date_from"):
                stmt = stmt.where(Study.start_date >= filters["start_date_from"])
            if filters.get("start_date_to"):
                stmt = stmt.where(Study.start_date <= filters["start_date_to"])
            
            # 申办方筛选
            if filters.get("sponsor"):
                stmt = stmt.where(Study.sponsor_name.ilike(f"%{filters['sponsor']}%"))
        
        # 排序
        if hasattr(Study, sort_by):
            sort_column = getattr(Study, sort_by)
            if sort_order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())
        
        # 统计总数
        count_stmt = select(func.count(Study.id)).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)
        
        # 执行查询
        result = await db.execute(stmt)
        studies = list(result.scalars().all())
        
        return studies, total
    
    async def get_with_relations(
        self,
        db: AsyncSession,
        id: str,
        load_relations: bool = True
    ) -> Optional[Study]:
        """
        获取研究及其关联数据
        
        Args:
            db: 数据库会话
            id: 研究ID
            load_relations: 是否加载关联数据
            
        Returns:
            研究对象或None
        """
        stmt = select(Study).where(Study.id == id)
        
        if load_relations:
            stmt = stmt.options(
                selectinload(Study.interventions),
                selectinload(Study.conditions),
                selectinload(Study.molecular_targets),
                selectinload(Study.outcomes),
                selectinload(Study.results),
                selectinload(Study.publications),
                selectinload(Study.safety_data)
            )
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_filter_options(self, db: AsyncSession) -> Dict[str, List[str]]:
        """
        获取筛选选项
        
        Args:
            db: 数据库会话
            
        Returns:
            筛选选项字典
        """
        options = {}
        
        # 研究阶段
        phase_stmt = select(Study.phase).distinct().where(Study.phase.isnot(None))
        phase_result = await db.execute(phase_stmt)
        options["phases"] = [p[0] for p in phase_result.fetchall() if p[0]]
        
        # 研究状态
        status_stmt = select(Study.status).distinct().where(Study.status.isnot(None))
        status_result = await db.execute(status_stmt)
        options["statuses"] = [s[0] for s in status_result.fetchall() if s[0]]
        
        # 研究类型
        type_stmt = select(Study.study_type).distinct().where(Study.study_type.isnot(None))
        type_result = await db.execute(type_stmt)
        options["study_types"] = [t[0] for t in type_result.fetchall() if t[0]]
        
        return options


class CRUDIntervention(CRUDBase[Intervention, Any, Any]):
    """
    干预措施的CRUD操作
    """
    
    async def get_by_study(self, db: AsyncSession, study_id: str) -> List[Intervention]:
        """
        获取研究的所有干预措施
        """
        stmt = select(Intervention).where(Intervention.study_id == study_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def search_by_name(self, db: AsyncSession, name: str) -> List[str]:
        """
        搜索干预措施名称
        """
        stmt = select(Intervention.name).distinct().where(
            Intervention.name.ilike(f"%{name}%")
        ).limit(10)
        result = await db.execute(stmt)
        return [r[0] for r in result.fetchall()]


class CRUDCondition(CRUDBase[Condition, Any, Any]):
    """
    疾病/瘤种的CRUD操作
    """
    
    async def get_by_study(self, db: AsyncSession, study_id: str) -> List[Condition]:
        """
        获取研究的所有疾病/瘤种
        """
        stmt = select(Condition).where(Condition.study_id == study_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_categories(self, db: AsyncSession) -> List[str]:
        """
        获取所有疾病分类
        """
        stmt = select(Condition.category_level1).distinct().where(
            Condition.category_level1.isnot(None)
        )
        result = await db.execute(stmt)
        return [r[0] for r in result.fetchall() if r[0]]
    
    async def search_by_name(self, db: AsyncSession, name: str) -> List[str]:
        """
        搜索疾病名称
        """
        stmt = select(Condition.name).distinct().where(
            Condition.name.ilike(f"%{name}%")
        ).limit(10)
        result = await db.execute(stmt)
        return [r[0] for r in result.fetchall()]


class CRUDMolecularTarget(CRUDBase[MolecularTarget, Any, Any]):
    """
    分子靶标的CRUD操作
    """
    
    async def get_by_study(self, db: AsyncSession, study_id: str) -> List[MolecularTarget]:
        """
        获取研究的所有分子靶标
        """
        stmt = select(MolecularTarget).where(MolecularTarget.study_id == study_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all_targets(self, db: AsyncSession) -> List[str]:
        """
        获取所有分子靶标
        """
        stmt = select(MolecularTarget.name).distinct().where(
            MolecularTarget.name.isnot(None)
        )
        result = await db.execute(stmt)
        return [r[0] for r in result.fetchall() if r[0]]


class CRUDOutcome(CRUDBase[Outcome, Any, Any]):
    """
    研究终点的CRUD操作
    """
    
    async def get_by_study(self, db: AsyncSession, study_id: str) -> List[Outcome]:
        """
        获取研究的所有终点
        """
        stmt = select(Outcome).where(Outcome.study_id == study_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())


class CRUDResult(CRUDBase[Result, Any, Any]):
    """
    研究结果的CRUD操作
    """
    
    async def get_by_study(self, db: AsyncSession, study_id: str) -> List[Result]:
        """
        获取研究的所有结果
        """
        stmt = select(Result).where(Result.study_id == study_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_latest_by_type(self, db: AsyncSession, study_id: str, result_type: str) -> Optional[Result]:
        """
        获取指定类型的最新结果
        """
        stmt = select(Result).where(
            Result.study_id == study_id,
            Result.result_type == result_type
        ).order_by(Result.publication_date.desc()).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


class CRUDPublication(CRUDBase[Publication, Any, Any]):
    """
    参考文献的CRUD操作
    """
    
    async def get_by_study(self, db: AsyncSession, study_id: str) -> List[Publication]:
        """
        获取研究的所有参考文献
        """
        stmt = select(Publication).where(Publication.study_id == study_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_latest_publication(self, db: AsyncSession, study_id: str) -> Optional[Publication]:
        """
        获取最新发表的文献
        """
        stmt = select(Publication).where(
            Publication.study_id == study_id
        ).order_by(Publication.publication_year.desc()).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


# 创建CRUD实例
study = CRUDStudy(Study)
intervention = CRUDIntervention(Intervention)
condition = CRUDCondition(Condition)
molecular_target = CRUDMolecularTarget(MolecularTarget)
outcome = CRUDOutcome(Outcome)
result = CRUDResult(Result)
publication = CRUDPublication(Publication)