"""
临床研究相关数据模型
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean, 
    Date, 
    DateTime, 
    ForeignKey, 
    Integer, 
    Numeric, 
    String, 
    Text,
    ARRAY,
    JSONB
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Study(Base):
    """
    临床研究主表
    """
    
    __tablename__ = "studies"
    
    # 基本信息
    nct_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="NCT编号")
    official_title: Mapped[str] = mapped_column(Text, nullable=False, comment="官方标题")
    brief_title: Mapped[Optional[str]] = mapped_column(String(500), comment="简短标题")
    acronym: Mapped[Optional[str]] = mapped_column(String(100), comment="研究缩写")
    
    # 研究类型和阶段
    study_type: Mapped[Optional[str]] = mapped_column(String(50), comment="研究类型")
    phase: Mapped[Optional[str]] = mapped_column(String(20), comment="研究阶段")
    
    # 研究状态
    status: Mapped[Optional[str]] = mapped_column(String(50), comment="研究状态")
    status_verified_date: Mapped[Optional[date]] = mapped_column(Date, comment="状态验证日期")
    
    # 时间信息
    start_date: Mapped[Optional[date]] = mapped_column(Date, comment="开始日期")
    completion_date: Mapped[Optional[date]] = mapped_column(Date, comment="完成日期")
    primary_completion_date: Mapped[Optional[date]] = mapped_column(Date, comment="主要完成日期")
    verification_date: Mapped[Optional[date]] = mapped_column(Date, comment="验证日期")
    last_update_submitted: Mapped[Optional[date]] = mapped_column(Date, comment="最后更新提交日期")
    
    # 描述信息
    brief_summary: Mapped[Optional[str]] = mapped_column(Text, comment="简要摘要")
    detailed_description: Mapped[Optional[str]] = mapped_column(Text, comment="详细描述")
    
    # 研究设计
    study_design: Mapped[Optional[str]] = mapped_column(Text, comment="研究设计")
    allocation: Mapped[Optional[str]] = mapped_column(String(50), comment="分配方式")
    intervention_model: Mapped[Optional[str]] = mapped_column(String(50), comment="干预模型")
    primary_purpose: Mapped[Optional[str]] = mapped_column(String(50), comment="主要目的")
    masking: Mapped[Optional[str]] = mapped_column(String(100), comment="盲法")
    
    # 终点信息
    primary_endpoint: Mapped[Optional[str]] = mapped_column(Text, comment="主要终点")
    secondary_endpoint: Mapped[Optional[str]] = mapped_column(Text, comment="次要终点")
    
    # 入组信息
    enrollment: Mapped[Optional[int]] = mapped_column(Integer, comment="入组人数")
    enrollment_type: Mapped[Optional[str]] = mapped_column(String(20), comment="入组类型")
    
    # 申办方信息
    sponsor_name: Mapped[Optional[str]] = mapped_column(String(500), comment="申办方名称")
    sponsor_class: Mapped[Optional[str]] = mapped_column(String(100), comment="申办方类别")
    collaborator: Mapped[Optional[str]] = mapped_column(Text, comment="合作方")
    
    # 研究者信息
    principal_investigator: Mapped[Optional[str]] = mapped_column(String(200), comment="主要研究者")
    
    # 数据来源
    data_source: Mapped[Optional[str]] = mapped_column(String(100), comment="数据来源")
    data_source_id: Mapped[Optional[str]] = mapped_column(String(100), comment="数据源ID")
    
    # 系统字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    
    # 关系
    interventions = relationship("Intervention", back_populates="study", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="study", cascade="all, delete-orphan")
    molecular_targets = relationship("MolecularTarget", back_populates="study", cascade="all, delete-orphan")
    outcomes = relationship("Outcome", back_populates="study", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="study", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="study", cascade="all, delete-orphan")
    safety_data = relationship("SafetyData", back_populates="study", cascade="all, delete-orphan")


class Intervention(Base):
    """
    干预措施表（药物/治疗方法）
    """
    
    __tablename__ = "interventions"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False, comment="干预措施名称")
    type: Mapped[Optional[str]] = mapped_column(String(100), comment="干预类型")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    other_name: Mapped[Optional[str]] = mapped_column(Text, comment="其他名称")
    
    # 药物详细信息
    drug_name_generic: Mapped[Optional[str]] = mapped_column(String(500), comment="通用名")
    drug_name_brand: Mapped[Optional[str]] = mapped_column(String(500), comment="商品名")
    drug_class: Mapped[Optional[str]] = mapped_column(String(200), comment="药物类别")
    mechanism_of_action: Mapped[Optional[str]] = mapped_column(Text, comment="作用机制")
    
    # 剂量信息
    dosage_form: Mapped[Optional[str]] = mapped_column(String(100), comment="剂型")
    dosage_route: Mapped[Optional[str]] = mapped_column(String(100), comment="给药途径")
    dosage_frequency: Mapped[Optional[str]] = mapped_column(String(100), comment="给药频率")
    dosage_strength: Mapped[Optional[str]] = mapped_column(String(100), comment="剂量强度")
    
    # 关系
    study = relationship("Study", back_populates="interventions")


class Condition(Base):
    """
    疾病/瘤种表
    """
    
    __tablename__ = "conditions"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False, comment="疾病名称")
    mesh_term: Mapped[Optional[str]] = mapped_column(String(500), comment="MeSH词")
    icd10_code: Mapped[Optional[str]] = mapped_column(String(20), comment="ICD10编码")
    
    # 分类信息
    category_level1: Mapped[Optional[str]] = mapped_column(String(200), comment="大类")
    category_level2: Mapped[Optional[str]] = mapped_column(String(200), comment="中类")
    category_level3: Mapped[Optional[str]] = mapped_column(String(200), comment="小类")
    
    # 分期信息
    stage: Mapped[Optional[str]] = mapped_column(String(100), comment="分期")
    stage_description: Mapped[Optional[str]] = mapped_column(Text, comment="分期描述")
    
    # 分子标志物
    biomarker: Mapped[Optional[str]] = mapped_column(Text, comment="生物标志物")
    
    # 关系
    study = relationship("Study", back_populates="conditions")


class MolecularTarget(Base):
    """
    分子靶标表
    """
    
    __tablename__ = "molecular_targets"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="靶标名称")
    full_name: Mapped[Optional[str]] = mapped_column(String(500), comment="全称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    
    # 检测方法
    detection_method: Mapped[Optional[str]] = mapped_column(String(200), comment="检测方法")
    detection_criteria: Mapped[Optional[str]] = mapped_column(Text, comment="检测标准")
    
    # 结果
    positive_criteria: Mapped[Optional[str]] = mapped_column(String(200), comment="阳性标准")
    negative_criteria: Mapped[Optional[str]] = mapped_column(String(200), comment="阴性标准")
    
    # 关系
    study = relationship("Study", back_populates="molecular_targets")


class Outcome(Base):
    """
    研究终点表
    """
    
    __tablename__ = "outcomes"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="终点标题")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="描述")
    type: Mapped[Optional[str]] = mapped_column(String(50), comment="终点类型")
    time_frame: Mapped[Optional[str]] = mapped_column(String(200), comment="时间框架")
    measure: Mapped[Optional[str]] = mapped_column(String(500), comment="测量方法")
    
    # 关系
    study = relationship("Study", back_populates="outcomes")
    results = relationship("Result", back_populates="outcome")


class Result(Base):
    """
    研究结果表
    """
    
    __tablename__ = "results"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    outcome_id: Mapped[Optional[str]] = mapped_column(ForeignKey("outcomes.id"), nullable=True)
    
    # 结果描述
    title: Mapped[Optional[str]] = mapped_column(String(500), comment="结果标题")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="结果描述")
    
    # 分组信息
    group_name: Mapped[Optional[str]] = mapped_column(String(200), comment="组名")
    group_description: Mapped[Optional[str]] = mapped_column(Text, comment="组描述")
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, comment="样本量")
    
    # 数值结果
    value: Mapped[Optional[str]] = mapped_column(String(200), comment="结果值")
    unit: Mapped[Optional[str]] = mapped_column(String(100), comment="单位")
    
    # 统计信息
    mean_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="均值")
    median_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="中位数")
    std_deviation: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="标准差")
    min_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="最小值")
    max_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="最大值")
    
    # 置信区间
    ci_lower: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="置信区间下限")
    ci_upper: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="置信区间上限")
    confidence_level: Mapped[Optional[int]] = mapped_column(Integer, default=95, comment="置信水平")
    
    # P值
    p_value: Mapped[Optional[str]] = mapped_column(String(50), comment="P值")
    
    # HR/OR
    hazard_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="风险比")
    odds_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="比值比")
    
    # 结果类型
    result_type: Mapped[Optional[str]] = mapped_column(String(100), comment="结果类型")
    
    # 数据来源
    data_source: Mapped[Optional[str]] = mapped_column(String(100), comment="数据来源")
    publication_date: Mapped[Optional[date]] = mapped_column(Date, comment="发表日期")
    
    # 关系
    study = relationship("Study", back_populates="results")
    outcome = relationship("Outcome", back_populates="results")


class SubgroupAnalysis(Base):
    """
    亚组分析结果表
    """
    
    __tablename__ = "subgroup_analyses"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    result_id: Mapped[Optional[str]] = mapped_column(ForeignKey("results.id"), nullable=True)
    
    # 亚组定义
    subgroup_name: Mapped[Optional[str]] = mapped_column(String(200), comment="亚组名称")
    subgroup_criteria: Mapped[Optional[str]] = mapped_column(Text, comment="亚组标准")
    
    # 亚组结果
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, comment="样本量")
    event_count: Mapped[Optional[int]] = mapped_column(Integer, comment="事件数")
    hazard_ratio: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="风险比")
    ci_lower: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="置信区间下限")
    ci_upper: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), comment="置信区间上限")
    p_value: Mapped[Optional[str]] = mapped_column(String(50), comment="P值")


class SafetyData(Base):
    """
    安全性数据表
    """
    
    __tablename__ = "safety_data"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    
    # 不良事件信息
    event_name: Mapped[Optional[str]] = mapped_column(String(500), comment="事件名称")
    event_type: Mapped[Optional[str]] = mapped_column(String(200), comment="事件类型")
    event_category: Mapped[Optional[str]] = mapped_column(String(200), comment="事件类别")
    
    # 发生率
    experimental_group_n: Mapped[Optional[int]] = mapped_column(Integer, comment="实验组人数")
    experimental_group_events: Mapped[Optional[int]] = mapped_column(Integer, comment="实验组事件数")
    control_group_n: Mapped[Optional[int]] = mapped_column(Integer, comment="对照组人数")
    control_group_events: Mapped[Optional[int]] = mapped_column(Integer, comment="对照组事件数")
    
    # 严重程度
    severity_grade1: Mapped[Optional[int]] = mapped_column(Integer, comment="1级不良事件数")
    severity_grade2: Mapped[Optional[int]] = mapped_column(Integer, comment="2级不良事件数")
    severity_grade3: Mapped[Optional[int]] = mapped_column(Integer, comment="3级不良事件数")
    severity_grade4: Mapped[Optional[int]] = mapped_column(Integer, comment="4级不良事件数")
    severity_grade5: Mapped[Optional[int]] = mapped_column(Integer, comment="5级不良事件数")
    
    # 管理建议
    management: Mapped[Optional[str]] = mapped_column(Text, comment="管理建议")
    
    # 关系
    study = relationship("Study", back_populates="safety_data")


class Publication(Base):
    """
    参考文献表
    """
    
    __tablename__ = "publications"
    
    study_id: Mapped[str] = mapped_column(ForeignKey("studies.id"), nullable=False)
    
    # 文献基本信息
    authors: Mapped[Optional[str]] = mapped_column(Text, comment="作者")
    title: Mapped[str] = mapped_column(Text, nullable=False, comment="标题")
    journal: Mapped[Optional[str]] = mapped_column(String(500), comment="期刊")
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, comment="发表年份")
    volume: Mapped[Optional[str]] = mapped_column(String(50), comment="卷")
    issue: Mapped[Optional[str]] = mapped_column(String(50), comment="期")
    pages: Mapped[Optional[str]] = mapped_column(String(50), comment="页码")
    
    # 标识符
    doi: Mapped[Optional[str]] = mapped_column(String(200), comment="DOI")
    pmid: Mapped[Optional[str]] = mapped_column(String(20), comment="PMID")
    pmcid: Mapped[Optional[str]] = mapped_column(String(20), comment="PMCID")
    
    # 摘要和全文
    abstract: Mapped[Optional[str]] = mapped_column(Text, comment="摘要")
    full_text_url: Mapped[Optional[str]] = mapped_column(Text, comment="全文链接")
    
    # 发表类型
    publication_type: Mapped[Optional[str]] = mapped_column(String(100), comment="发表类型")
    
    # 会议信息
    conference_name: Mapped[Optional[str]] = mapped_column(String(500), comment="会议名称")
    conference_date: Mapped[Optional[date]] = mapped_column(Date, comment="会议日期")
    conference_location: Mapped[Optional[str]] = mapped_column(String(200), comment="会议地点")
    
    # 数据阶段
    data_stage: Mapped[Optional[str]] = mapped_column(String(100), comment="数据阶段")
    
    # 系统字段
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    
    # 关系
    study = relationship("Study", back_populates="publications")
    authors = relationship("PublicationAuthor", back_populates="publication", cascade="all, delete-orphan")


class PublicationAuthor(Base):
    """
    文献作者表
    """
    
    __tablename__ = "publication_authors"
    
    publication_id: Mapped[str] = mapped_column(ForeignKey("publications.id"), nullable=False)
    author_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="作者姓名")
    author_order: Mapped[Optional[int]] = mapped_column(Integer, comment="作者顺序")
    affiliation: Mapped[Optional[str]] = mapped_column(Text, comment="所属机构")
    
    # 关系
    publication = relationship("Publication", back_populates="authors")