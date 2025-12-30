"""
ClinicalTrials.gov 数据抓取器
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import async_timeout
from loguru import logger


@dataclass
class StudyData:
    """研究数据"""
    nct_id: str
    official_title: str
    brief_title: Optional[str] = None
    acronym: Optional[str] = None
    study_type: Optional[str] = None
    phase: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    enrollment: Optional[int] = None
    sponsor_name: Optional[str] = None
    brief_summary: Optional[str] = None
    detailed_description: Optional[str] = None
    primary_endpoint: Optional[str] = None
    secondary_endpoint: Optional[str] = None
    conditions: List[Dict[str, Any]] = None
    interventions: List[Dict[str, Any]] = None
    eligibility: Optional[Dict[str, Any]] = None
    contacts: List[Dict[str, Any]] = None
    locations: List[Dict[str, Any]] = None
    publications: List[Dict[str, Any]] = None


class ClinicalTrialsScraper:
    """ClinicalTrials.gov 数据抓取器"""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    
    def __init__(self):
        self.session = None
        self.semaphore = asyncio.Semaphore(10)  # 限制并发数
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'OncologyTrialsSystem/1.0'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def search_studies(
        self,
        query: str = "",
        conditions: List[str] = None,
        interventions: List[str] = None,
        sponsor: str = None,
        phase: List[str] = None,
        status: List[str] = None,
        study_type: List[str] = None,
        start_date_from: str = None,
        start_date_to: str = None,
        limit: int = 1000
    ) -> List[str]:
        """
        搜索研究
        
        Args:
            query: 搜索关键词
            conditions: 疾病条件列表
            interventions: 干预措施列表
            sponsor: 申办方
            phase: 研究阶段列表
            status: 研究状态列表
            study_type: 研究类型列表
            start_date_from: 开始日期（从）
            start_date_to: 开始日期（到）
            limit: 返回数量限制
            
        Returns:
            NCT ID列表
        """
        params = {
            "query.cond": query,
            "query.titles": query,
            "pageSize": min(limit, 1000),
            "format": "json"
        }
        
        # 添加筛选条件
        if conditions:
            params["query.cond"] = " OR ".join(conditions)
        
        if interventions:
            params["query.intr"] = " OR ".join(interventions)
        
        if sponsor:
            params["query.spons"] = sponsor
        
        if phase:
            params["query.phase"] = " OR ".join(phase)
        
        if status:
            params["query.status"] = " OR ".join(status)
        
        if study_type:
            params["query.type"] = " OR ".join(study_type)
        
        nct_ids = []
        next_page_token = None
        
        while len(nct_ids) < limit:
            if next_page_token:
                params["pageToken"] = next_page_token
            
            try:
                async with self.semaphore:
                    async with self.session.get(
                        f"{self.BASE_URL}/studies",
                        params=params
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # 提取NCT ID
                            for study in data.get("studies", []):
                                nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
                                if nct_id:
                                    nct_ids.append(nct_id)
                            
                            # 检查是否有下一页
                            next_page_token = data.get("nextPageToken")
                            if not next_page_token:
                                break
                        else:
                            logger.error(f"搜索失败: {response.status}")
                            break
                            
            except Exception as e:
                logger.error(f"搜索请求失败: {e}")
                break
        
        return nct_ids[:limit]
    
    async def get_study_detail(self, nct_id: str) -> Optional[StudyData]:
        """
        获取研究详情
        
        Args:
            nct_id: NCT编号
            
        Returns:
            研究数据或None
        """
        try:
            async with self.semaphore:
                async with self.session.get(
                    f"{self.BASE_URL}/studies/{nct_id}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_study_data(data)
                    else:
                        logger.warning(f"获取研究详情失败: {nct_id}, 状态码: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"获取研究详情失败: {nct_id}, 错误: {e}")
            return None
    
    def _parse_study_data(self, data: Dict[str, Any]) -> StudyData:
        """解析研究数据"""
        protocol_section = data.get("protocolSection", {})
        
        # 基本信息
        identification = protocol_section.get("identificationModule", {})
        nct_id = identification.get("nctId", "")
        official_title = identification.get("officialTitle", "")
        brief_title = identification.get("briefTitle")
        acronym = identification.get("acronym")
        
        # 状态信息
        status = protocol_section.get("statusModule", {})
        study_status = status.get("overallStatus")
        start_date = status.get("startDateStruct", {}).get("date")
        completion_date = status.get("completionDateStruct", {}).get("date")
        
        # 设计信息
        design = protocol_section.get("designModule", {})
        study_type = design.get("studyType")
        phase = design.get("phases", [])
        if phase:
            phase = phase[0] if isinstance(phase, list) else phase
        else:
            phase = None
        
        # 描述信息
        description = protocol_section.get("descriptionModule", {})
        brief_summary = description.get("briefSummary")
        detailed_description = description.get("detailedDescription")
        
        # 条件
        conditions = protocol_section.get("conditionsModule", {}).get("conditions", [])
        conditions_list = [{"name": cond} for cond in conditions]
        
        # 干预措施
        arms_interventions = protocol_section.get("armsInterventionsModule", {})
        interventions = []
        for intervention in arms_interventions.get("interventions", []):
            interventions.append({
                "type": intervention.get("type"),
                "name": intervention.get("name"),
                "description": intervention.get("description")
            })
        
        # 申办方
        sponsors = protocol_section.get("sponsorsCollaboratorsModule", {})
        sponsor_name = None
        if sponsors.get("leadSponsor"):
            sponsor_name = sponsors["leadSponsor"].get("name")
        
        # 入组信息
        design = protocol_section.get("designModule", {})
        enrollment_info = design.get("enrollmentInfo", {})
        enrollment = enrollment_info.get("count")
        
        # 终点
        outcomes = protocol_section.get("outcomesModule", {})
        primary_endpoint = None
        secondary_endpoint = None
        
        primary_outcomes = outcomes.get("primaryOutcomes", [])
        if primary_outcomes:
            primary_endpoint = primary_outcomes[0].get("description")
        
        secondary_outcomes = outcomes.get("secondaryOutcomes", [])
        if secondary_outcomes:
            secondary_endpoint = secondary_outcomes[0].get("description")
        
        return StudyData(
            nct_id=nct_id,
            official_title=official_title,
            brief_title=brief_title,
            acronym=acronym,
            study_type=study_type,
            phase=phase,
            status=study_status,
            start_date=start_date,
            completion_date=completion_date,
            enrollment=enrollment,
            sponsor_name=sponsor_name,
            brief_summary=brief_summary,
            detailed_description=detailed_description,
            primary_endpoint=primary_endpoint,
            secondary_endpoint=secondary_endpoint,
            conditions=conditions_list,
            interventions=interventions
        )
    
    async def get_studies_by_date_range(
        self,
        start_date: str,
        end_date: str,
        limit: int = 1000
    ) -> List[str]:
        """
        根据日期范围获取研究
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 数量限制
            
        Returns:
            NCT ID列表
        """
        return await self.search_studies(
            start_date_from=start_date,
            start_date_to=end_date,
            limit=limit
        )
    
    async def get_updated_studies(
        self,
        last_update_date: str,
        limit: int = 1000
    ) -> List[str]:
        """
        获取指定日期后更新的研究
        
        Args:
            last_update_date: 最后更新日期 (YYYY-MM-DD)
            limit: 数量限制
            
        Returns:
            NCT ID列表
        """
        params = {
            "query.lastUpdatePostDateStruct": last_update_date,
            "pageSize": min(limit, 1000),
            "format": "json"
        }
        
        nct_ids = []
        next_page_token = None
        
        while len(nct_ids) < limit:
            if next_page_token:
                params["pageToken"] = next_page_token
            
            try:
                async with self.semaphore:
                    async with self.session.get(
                        f"{self.BASE_URL}/studies",
                        params=params
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for study in data.get("studies", []):
                                nct_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
                                if nct_id:
                                    nct_ids.append(nct_id)
                            
                            next_page_token = data.get("nextPageToken")
                            if not next_page_token:
                                break
                        else:
                            logger.error(f"获取更新研究失败: {response.status}")
                            break
                            
            except Exception as e:
                logger.error(f"获取更新研究请求失败: {e}")
                break
        
        return nct_ids[:limit]


# 使用示例
async def example():
    """使用示例"""
    async with ClinicalTrialsScraper() as scraper:
        # 搜索肺癌相关研究
        nct_ids = await scraper.search_studies(
            query="lung cancer",
            phase=["Phase 3"],
            status=["COMPLETED"],
            limit=100
        )
        print(f"找到 {len(nct_ids)} 个研究")
        
        # 获取研究详情
        for nct_id in nct_ids[:5]:
            study = await scraper.get_study_detail(nct_id)
            if study:
                print(f"{study.nct_id}: {study.official_title}")


if __name__ == "__main__":
    asyncio.run(example())