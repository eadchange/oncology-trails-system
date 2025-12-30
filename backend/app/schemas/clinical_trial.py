"""
临床研究相关数据模式
"""

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
n
from .common import BaseResponse, PaginationParams, SortParams


class StudyBase(BaseModel):
    """
    研究基础模型
    """
    nct_id: str = Field(..., description="NCT编号")
    official_title: str = Field(..., description="官方标题")
    brief_title: Optional[str] = Field(default=None, description="简短标题")
    acronym: Optional[str] = Field(default=None, description="研究缩写")
    
    # 研究类型和阶段
    study_type: Optional[str] = Field(default=None, description="研究类型")
    phase: Optional[str] = Field(default=None, description="研究阶段")
    
    # 研究状态
    status: Optional[str] = Field(default=None, description="研究状态")
    status_verified_date: Optional[date] = Field(default=None, description="状态验证日期")
    
    # 时间信息
    start_date: Optional[date] = Field(default=None, description="开始日期")
    completion_date: Optional[date] = Field(default=None, description="完成日期")
    primary_completion_date: Optional[date] = Field(default=None, description="主要完成日期")
    
    # 描述信息
    brief_summary: Optional[str] = Field(default=None, description="简要摘要")
    detailed_description: Optional[str] = Field(default=None, description="详细描述")
    
    # 入组信息
    enrollment: Optional[int] = Field(default=None, description="入组人数")
    
    # 申办方信息
    sponsor_name: Optional[str] = Field(default=None, description="申办方名称")
    sponsor_class: Optional[str] = Field(default=None, description="申办方类别")
    
    class Config:
        from_attributes = True


class InterventionResponse(BaseModel):
    """
    干预措施响应模型
    """
    id: str = Field(..., description="ID")
    name: str = Field(..., description="干预措施名称")
    type: Optional[str] = Field(default=None, description="干预类型")
    description: Optional[str] = Field(default=None, description="描述")
    drug_name_generic: Optional[str] = Field(default=None, description="通用名")
    drug_name_brand: Optional[str] = Field(default=None, description="商品名")
    drug_class: Optional[str] = Field(default=None, description="药物类别")
    
    class Config:
        from_attributes = True


class ConditionResponse(BaseModel):
    """
    疾病/瘤种响应模型
    """
    id: str = Field(..., description="ID")
    name: str = Field(..., description="疾病名称")
    mesh_term: Optional[str] = Field(default=None, description="MeSH词")
    category_level1: Optional[str] = Field(default=None, description="大类")
    category_level2: Optional[str] = Field(default=None, description="中类")
    category_level3: Optional[str] = Field(default=None, description="小类")
    stage: Optional[str] = Field(default=None, description="分期")
    
    class Config:
        from_attributes = True


class MolecularTargetResponse(BaseModel):
    """
    分子靶标响应模型
    """
    id: str = Field(..., description="ID")
    name: str = Field(..., description="靶标名称")
    full_name: Optional[str] = Field(default=None, description="全称")
    description: Optional[str] = Field(default=None, description="描述")
    
    class Config:
        from_attributes = True


class OutcomeResponse(BaseModel):
    """
    研究终点响应模型
    """
    id: str = Field(..., description="ID")
    title: str = Field(..., description="终点标题")
    description: Optional[str] = Field(default=None, description="描述")
    type: Optional[str] = Field(default=None, description="终点类型")
    time_frame: Optional[str] = Field(default=None, description="时间框架")
    
    class Config:
        from_attributes = True


class ResultResponse(BaseModel):
    """
    研究结果响应模型
    """
    id: str = Field(..., description="ID")
    title: Optional[str] = Field(default=None, description="结果标题")
    group_name: Optional[str] = Field(default=None, description="组名")
    sample_size: Optional[int] = Field(default=None, description="样本量")
    value: Optional[str] = Field(default=None, description="结果值")
    unit: Optional[str] = Field(default=None, description="单位")
    mean_value: Optional[float] = Field(default=None, description="均值")
    median_value: Optional[float] = Field(default=None, description="中位数")
    ci_lower: Optional[float] = Field(default=None, description="置信区间下限")
    ci_upper: Optional[float] = Field(default=None, description="置信区间上限")
    p_value: Optional[str] = Field(default=None, description="P值")
    hazard_ratio: Optional[float] = Field(default=None, description="风险比")
    result_type: Optional[str] = Field(default=None, description="结果类型")
    publication_date: Optional[date] = Field(default=None, description="发表日期")
    
    class Config:
        from_attributes = True


class SafetyDataResponse(BaseModel):
    """
    安全性数据响应模型
    """
    id: str = Field(..., description="ID")
    event_name: Optional[str] = Field(default=None, description="事件名称")
    event_type: Optional[str] = Field(default=None, description="事件类型")
    experimental_group_events: Optional[int] = Field(default=None, description="实验组事件数")
    control_group_events: Optional[int] = Field(default=None, description="对照组事件数")
    
    class Config:
        from_attributes = True


class PublicationResponse(BaseModel):
    """
    参考文献响应模型
    """
    id: str = Field(..., description="ID")
    authors: Optional[str] = Field(default=None, description="作者")
    title: str = Field(..., description="标题")
    journal: Optional[str] = Field(default=None, description="期刊")
    publication_year: Optional[int] = Field(default=None, description="发表年份")
    doi: Optional[str] = Field(default=None, description="DOI")
    pmid: Optional[str] = Field(default=None, description="PMID")
    abstract: Optional[str] = Field(default=None, description="摘要")
    
    class Config:
        from_attributes = True


class StudyResponse(StudyBase):
    """
    研究响应模型（列表用）
    """
    id: str = Field(..., description="ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 关联数据（简要）
    conditions: List[str] = Field(default=[], description="疾病列表")
    interventions: List[str] = Field(default=[], description="干预措施列表")
    latest_publication_year: Optional[int] = Field(default=None, description="最新发表年份")
    
    class Config:
        from_attributes = True


class StudyDetailResponse(StudyBase):
    """
    研究详情响应模型
    """
    id: str = Field(..., description="ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 完整关联数据
    interventions: List[InterventionResponse] = Field(default=[], description="干预措施")
    conditions: List[ConditionResponse] = Field(default=[], description="疾病/瘤种")
    molecular_targets: List[MolecularTargetResponse] = Field(default=[], description="分子靶标")
    outcomes: List[OutcomeResponse] = Field(default=[], description="研究终点")
    results: List[ResultResponse] = Field(default=[], description="研究结果")
    publications: List[PublicationResponse] = Field(default=[], description="参考文献")
    safety_data: List[SafetyDataResponse] = Field(default=[], description="安全性数据")
    
    class Config:
        from_attributes = True


class StudySearchRequest(BaseModel):
    """
    研究搜索请求模型
    """
    # 分页参数
    pagination: PaginationParams = Field(default_factory=PaginationParams, description="分页参数")
    
    # 搜索参数
    query: Optional[str] = Field(default=None, description="搜索关键词")
    
    # 筛选参数
    nct_id: Optional[str] = Field(default=None, description="NCT编号")
    phase: Optional[List[str]] = Field(default=None, description="研究阶段")
    status: Optional[List[str]] = Field(default=None, description="研究状态")
    study_type: Optional[List[str]] = Field(default=None, description="研究类型")
    
    # 疾病筛选
    condition: Optional[str] = Field(default=None, description="疾病名称")
    condition_category: Optional[str] = Field(default=None, description="疾病分类")
    stage: Optional[str] = Field(default=None, description="肿瘤分期")
    
    # 药物筛选
    intervention: Optional[str] = Field(default=None, description="干预措施")
    drug_name: Optional[str] = Field(default=None, description="药物名称")
    drug_class: Optional[str] = Field(default=None, description="药物类别")
    
    # 分子靶标筛选
    molecular_target: Optional[str] = Field(default=None, description="分子靶标")
    
    # 时间筛选
    start_date_from: Optional[date] = Field(default=None, description="开始日期（从）")
    start_date_to: Optional[date] = Field(default=None, description="开始日期（到）")
    completion_date_from: Optional[date] = Field(default=None, description="完成日期（从）")
    completion_date_to: Optional[date] = Field(default=None, description="完成日期（到）")
    
    # 申办方筛选
    sponsor: Optional[str] = Field(default=None, description="申办方")
    
    # 排序参数
    sort: SortParams = Field(default_factory=lambda: SortParams(sort_by="updated_at", sort_order="desc"), description="排序参数")
    
    class Config:
        from_attributes = True


class StudyListResponse(BaseResponse):
    """
    研究列表响应模型
    """
    data: Dict[str, Any] = Field(default_factory=dict, description="响应数据")
    
    @classmethod
    def create(
        cls,
        studies: List[StudyResponse],
        total: int,
        page: int,
        size: int,
        **kwargs
    ) -> "StudyListResponse":
        """
        创建研究列表响应
        """
        return cls(
            data={
                "items": studies,
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
                **kwargs
            }
        )


# 筛选选项响应模型
class FilterOptionsResponse(BaseModel):
    """
    筛选选项响应模型
    """
    phases: List[str] = Field(default=[], description="研究阶段选项")
    statuses: List[str] = Field(default=[], description="研究状态选项")
    study_types: List[str] = Field(default=[], description="研究类型选项")
    condition_categories: List[str] = Field(default=[], description="疾病分类选项")
    intervention_types: List[str] = Field(default=[], description="干预类型选项")
    molecular_targets: List[str] = Field(default=[], description="分子靶标选项")
    sponsors: List[str] = Field(default=[], description="申办方选项")
    
    class Config:
        from_attributes = True