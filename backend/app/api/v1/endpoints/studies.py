"""
临床研究相关API端点
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.schemas.clinical_trial import (
    StudyDetailResponse,
    StudyListResponse,
    StudySearchRequest,
    FilterOptionsResponse
)
from app.schemas.common import ErrorResponse
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/search", response_model=StudyListResponse, summary="搜索临床研究")
async def search_studies(
    request: Request,
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=settings.MAX_PAGE_SIZE, description="每页数量"),
    phase: Optional[List[str]] = Query(None, description="研究阶段"),
    status: Optional[List[str]] = Query(None, description="研究状态"),
    study_type: Optional[List[str]] = Query(None, description="研究类型"),
    condition: Optional[str] = Query(None, description="疾病名称"),
    intervention: Optional[str] = Query(None, description="干预措施"),
    molecular_target: Optional[str] = Query(None, description="分子靶标"),
    sponsor: Optional[str] = Query(None, description="申办方"),
    sort_by: str = Query("updated_at", description="排序字段"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="排序顺序"),
    current_user: Optional[UserResponse] = Depends(get_current_user)
) -> Any:
    """
    搜索临床研究
    
    支持全文搜索和多维度筛选
    """
    try:
        # 构建筛选条件
        filters = {
            "phase": phase,
            "status": status,
            "study_type": study_type,
        }
        
        # 搜索研究
        studies, total = await crud.study.search_studies(
            db=db,
            query=q,
            filters=filters,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # 记录搜索历史（登录用户）
        if current_user:
            await crud.search_history.add_search(
                db=db,
                query=q or "",
                filters=filters,
                result_count=total,
                user_id=current_user.id
            )
        
        # 转换响应数据
        study_responses = []
        for study in studies:
            # 获取关联数据
            conditions = await crud.condition.get_by_study(db, study.id)
            interventions = await crud.intervention.get_by_study(db, study.id)
            publications = await crud.publication.get_by_study(db, study.id)
            
            study_response = StudyDetailResponse(
                id=study.id,
                nct_id=study.nct_id,
                official_title=study.official_title,
                acronym=study.acronym,
                phase=study.phase,
                status=study.status,
                start_date=study.start_date,
                completion_date=study.completion_date,
                enrollment=study.enrollment,
                sponsor_name=study.sponsor_name,
                conditions=[c.name for c in conditions],
                interventions=[i.name for i in interventions],
                latest_publication_year=max([p.publication_year for p in publications if p.publication_year], default=None),
                created_at=study.created_at,
                updated_at=study.updated_at
            )
            study_responses.append(study_response)
        
        return StudyListResponse.create(
            studies=study_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"搜索失败: {str(e)}"
        )


@router.get("/{study_id}", response_model=StudyDetailResponse, summary="获取研究详情")
async def get_study_detail(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user)
 -> Any:
    """
    获取研究详情
    
    包含完整的关联数据
    """
    try:
        # 获取研究详情（包含所有关联数据）
        study = await crud.study.get_with_relations(db, study_id)
        if not study:
            raise HTTPException(
                status_code=404,
                detail="研究不存在"
            )
        
        # 记录浏览历史（登录用户）
        if current_user:
            await crud.user_history.add_history(db, current_user.id, study_id)
        
        # 构建响应数据
        return StudyDetailResponse(
            id=study.id,
            nct_id=study.nct_id,
            official_title=study.official_title,
            brief_title=study.brief_title,
            acronym=study.acronym,
            study_type=study.study_type,
            phase=study.phase,
            status=study.status,
            start_date=study.start_date,
            completion_date=study.completion_date,
            enrollment=study.enrollment,
            sponsor_name=study.sponsor_name,
            brief_summary=study.brief_summary,
            detailed_description=study.detailed_description,
            primary_endpoint=study.primary_endpoint,
            secondary_endpoint=study.secondary_endpoint,
            interventions=[
                InterventionResponse(
                    id=i.id,
                    name=i.name,
                    type=i.type,
                    description=i.description,
                    drug_name_generic=i.drug_name_generic,
                    drug_name_brand=i.drug_name_brand,
                    drug_class=i.drug_class
                ) for i in study.interventions
            ],
            conditions=[
                ConditionResponse(
                    id=c.id,
                    name=c.name,
                    mesh_term=c.mesh_term,
                    category_level1=c.category_level1,
                    category_level2=c.category_level2,
                    category_level3=c.category_level3,
                    stage=c.stage
                ) for c in study.conditions
            ],
            molecular_targets=[
                MolecularTargetResponse(
                    id=mt.id,
                    name=mt.name,
                    full_name=mt.full_name,
                    description=mt.description
                ) for mt in study.molecular_targets
            ],
            outcomes=[
                OutcomeResponse(
                    id=o.id,
                    title=o.title,
                    description=o.description,
                    type=o.type,
                    time_frame=o.time_frame
                ) for o in study.outcomes
            ],
            results=[
                ResultResponse(
                    id=r.id,
                    title=r.title,
                    group_name=r.group_name,
                    sample_size=r.sample_size,
                    value=r.value,
                    unit=r.unit,
                    mean_value=r.mean_value,
                    median_value=r.median_value,
                    ci_lower=r.ci_lower,
                    ci_upper=r.ci_upper,
                    p_value=r.p_value,
                    hazard_ratio=r.hazard_ratio,
                    result_type=r.result_type,
                    publication_date=r.publication_date
                ) for r in study.results
            ],
            publications=[
                PublicationResponse(
                    id=p.id,
                    authors=p.authors,
                    title=p.title,
                    journal=p.journal,
                    publication_year=p.publication_year,
                    doi=p.doi,
                    pmid=p.pmid,
                    abstract=p.abstract
                ) for p in study.publications
            ],
            safety_data=[
                SafetyDataResponse(
                    id=sd.id,
                    event_name=sd.event_name,
                    event_type=sd.event_type,
                    experimental_group_events=sd.experimental_group_events,
                    control_group_events=sd.control_group_events
                ) for sd in study.safety_data
            ],
            created_at=study.created_at,
            updated_at=study.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"获取研究详情失败: {str(e)}"
        )


@router.get("/filter-options", response_model=FilterOptionsResponse, summary="获取筛选选项")
async def get_filter_options(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    获取所有可用的筛选选项
    """
    try:
        options = await crud.study.get_filter_options(db)
        return FilterOptionsResponse(**options)
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"获取筛选选项失败: {str(e)}"
        )


@router.get("/nct/{nct_id}", response_model=StudyDetailResponse, summary="根据NCT ID获取研究")
async def get_study_by_nct_id(
    nct_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user)
) -> Any:
    """
    根据NCT ID获取研究详情
    """
    try:
        study = await crud.study.get_by_nct_id(db, nct_id)
        if not study:
            raise HTTPException(
                status_code=404,
                detail="研究不存在"
            )
        
        # 使用现有的详情接口
        return await get_study_detail(study.id, db, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"获取研究失败: {str(e)}"
        )


@router.post("/advanced-search", response_model=StudyListResponse, summary="高级搜索")
async def advanced_search(
    search_request: StudySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user)
) -> Any:
    """
    高级搜索接口
    
    支持复杂的搜索条件和筛选
    """
    try:
        # 构建筛选条件
        filters = {
            "phase": search_request.phase,
            "status": search_request.status,
            "study_type": search_request.study_type,
            "start_date_from": search_request.start_date_from,
            "start_date_to": search_request.start_date_to,
        }
        
        # 添加其他筛选条件
        if search_request.condition:
            filters["condition"] = search_request.condition
        if search_request.intervention:
            filters["intervention"] = search_request.intervention
        if search_request.molecular_target:
            filters["molecular_target"] = search_request.molecular_target
        if search_request.sponsor:
            filters["sponsor"] = search_request.sponsor
        
        # 搜索研究
        studies, total = await crud.study.search_studies(
            db=db,
            query=search_request.query,
            filters=filters,
            page=search_request.pagination.page,
            size=search_request.pagination.size,
            sort_by=search_request.sort.sort_by,
            sort_order=search_request.sort.sort_order
        )
        
        # 转换响应数据
        study_responses = []
        for study in studies:
            # 获取关联数据（简要）
            conditions = await crud.condition.get_by_study(db, study.id)
            interventions = await crud.intervention.get_by_study(db, study.id)
            publications = await crud.publication.get_by_study(db, study.id)
            
            study_response = StudyDetailResponse(
                id=study.id,
                nct_id=study.nct_id,
                official_title=study.official_title,
                acronym=study.acronym,
                phase=study.phase,
                status=study.status,
                start_date=study.start_date,
                completion_date=study.completion_date,
                enrollment=study.enrollment,
                sponsor_name=study.sponsor_name,
                conditions=[c.name for c in conditions],
                interventions=[i.name for i in interventions],
                latest_publication_year=max([p.publication_year for p in publications if p.publication_year], default=None),
                created_at=study.created_at,
                updated_at=study.updated_at
            )
            study_responses.append(study_response)
        
        return StudyListResponse.create(
            studies=study_responses,
            total=total,
            page=search_request.pagination.page,
            size=search_request.pagination.size
        )
        
    except Exception as e:
        return ErrorResponse(
            code=500,
            message=f"高级搜索失败: {str(e)}"
        )