-- 肿瘤治疗进展查询系统 - 数据库设计
-- 数据库: PostgreSQL 15+
-- 创建日期: 2025-12-30

-- =====================================================
-- 1. 创建数据库和基本配置
-- =====================================================

-- 创建数据库（命令行执行）
-- CREATE DATABASE oncology_db WITH ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- 2. 用户和权限相关表
-- =====================================================

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    institution VARCHAR(200),
    title VARCHAR(100),
    specialty VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 用户角色表
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- 用户会话表
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_session_token (session_token),
    INDEX idx_expires_at (expires_at)
);

-- =====================================================
-- 3. 研究主数据表
-- =====================================================

-- 研究主表
CREATE TABLE studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nct_id VARCHAR(20) UNIQUE NOT NULL,
    official_title TEXT NOT NULL,
    brief_title VARCHAR(500),
    acronym VARCHAR(100),
    
    -- 研究类型和阶段
    study_type VARCHAR(50), -- Interventional, Observational, Expanded Access
    phase VARCHAR(20), -- Phase 1, Phase 2, Phase 3, Phase 4, N/A
    
    -- 研究状态
    status VARCHAR(50), -- Not yet recruiting, Recruiting, Active, Completed, Terminated
    status_verified_date DATE,
    
    -- 时间信息
    start_date DATE,
    completion_date DATE,
    primary_completion_date DATE,
    verification_date DATE,
    last_update_submitted DATE,
    
    -- 描述信息
    brief_summary TEXT,
    detailed_description TEXT,
    
    -- 研究设计
    study_design TEXT,
    allocation VARCHAR(50), -- Randomized, Non-Randomized, Single Group
    intervention_model VARCHAR(50), -- Parallel, Crossover, Factorial
    primary_purpose VARCHAR(50), -- Treatment, Prevention, Diagnostic
    masking VARCHAR(100), -- Double Blind, Single Blind, Open Label
    
    -- 终点信息
    primary_endpoint TEXT,
    secondary_endpoint TEXT,
    
    -- 入组信息
    enrollment INTEGER,
    enrollment_type VARCHAR(20), -- Actual, Anticipated, Estimated
    
    -- 申办方信息
    sponsor_name VARCHAR(500),
    sponsor_class VARCHAR(100), -- Industry, NIH, Other
    collaborator TEXT,
    
    -- 研究者信息
    principal_investigator VARCHAR(200),
    
    -- 数据来源
    data_source VARCHAR(100), -- ClinicalTrials.gov, PubMed, ASCO, ESMO
    data_source_id VARCHAR(100),
    
    -- 系统字段
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    -- 约束和索引
    CONSTRAINT chk_nct_format CHECK (nct_id ~* '^NCT\d{8}$'),
    INDEX idx_nct_id (nct_id),
    INDEX idx_status (status),
    INDEX idx_phase (phase),
    INDEX idx_start_date (start_date),
    INDEX idx_completion_date (completion_date),
    INDEX idx_study_type (study_type),
    INDEX idx_sponsor (sponsor_name),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at)
);

-- =====================================================
-- 4. 研究相关数据表
-- =====================================================

-- 干预措施表（药物/治疗方法）
CREATE TABLE interventions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    type VARCHAR(100), -- Drug, Device, Biological, Radiation, Procedure
    description TEXT,
    other_name TEXT,
    
    -- 药物详细信息
    drug_name_generic VARCHAR(500),
    drug_name_brand VARCHAR(500),
    drug_class VARCHAR(200),
    mechanism_of_action TEXT,
    
    -- 剂量信息
    dosage_form VARCHAR(100),
    dosage_route VARCHAR(100),
    dosage_frequency VARCHAR(100),
    dosage_strength VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_name (name),
    INDEX idx_type (type)
);

-- 疾病/瘤种表
CREATE TABLE conditions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    mesh_term VARCHAR(500),
    icd10_code VARCHAR(20),
    
    -- 分类信息
    category_level1 VARCHAR(200), -- 大类（如：肿瘤）
    category_level2 VARCHAR(200), -- 中类（如：肺癌）
    category_level3 VARCHAR(200), -- 小类（如：非小细胞肺癌）
    
    -- 分期信息
    stage VARCHAR(100),
    stage_description TEXT,
    
    -- 分子标志物
    biomarker TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_name (name),
    INDEX idx_category (category_level1, category_level2),
    INDEX idx_mesh_term (mesh_term)
);

-- 分子靶标表
CREATE TABLE molecular_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL, -- EGFR, ALK, PD-L1, etc.
    full_name VARCHAR(500),
    description TEXT,
    
    -- 检测方法
    detection_method VARCHAR(200),
    detection_criteria TEXT,
    
    -- 结果
    positive_criteria VARCHAR(200),
    negative_criteria VARCHAR(200),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_name (name)
);

-- 研究终点表
CREATE TABLE outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type VARCHAR(50), -- Primary, Secondary, Other
    time_frame VARCHAR(200),
    measure VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_type (type)
);

-- 研究结果表
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    outcome_id UUID REFERENCES outcomes(id) ON DELETE SET NULL,
    
    -- 结果描述
    title VARCHAR(500),
    description TEXT,
    
    -- 分组信息
    group_name VARCHAR(200),
    group_description TEXT,
    sample_size INTEGER,
    
    -- 数值结果
    value VARCHAR(200),
    unit VARCHAR(100),
    
    -- 统计信息
    mean_value DECIMAL(10,4),
    median_value DECIMAL(10,4),
    std_deviation DECIMAL(10,4),
    min_value DECIMAL(10,4),
    max_value DECIMAL(10,4),
    
    -- 置信区间
    ci_lower DECIMAL(10,4),
    ci_upper DECIMAL(10,4),
    confidence_level INTEGER DEFAULT 95,
    
    -- P值
    p_value VARCHAR(50),
    
    -- HR/OR
    hazard_ratio DECIMAL(10,4),
    odds_ratio DECIMAL(10,4),
    
    -- 结果类型
    result_type VARCHAR(100), -- OS, PFS, ORR, DCR, etc.
    
    -- 数据来源
    data_source VARCHAR(100),
    publication_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_outcome_id (outcome_id),
    INDEX idx_result_type (result_type),
    INDEX idx_publication_date (publication_date)
);

-- 亚组分析结果表
CREATE TABLE subgroup_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    result_id UUID REFERENCES results(id) ON DELETE CASCADE,
    
    -- 亚组定义
    subgroup_name VARCHAR(200),
    subgroup_criteria TEXT,
    
    -- 亚组结果
    sample_size INTEGER,
    event_count INTEGER,
    hazard_ratio DECIMAL(10,4),
    ci_lower DECIMAL(10,4),
    ci_upper DECIMAL(10,4),
    p_value VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_result_id (result_id)
);

-- 安全性数据表
CREATE TABLE safety_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    
    -- 不良事件信息
    event_name VARCHAR(500),
    event_type VARCHAR(200), -- AE, SAE, AESI
    event_category VARCHAR(200),
    
    -- 发生率
    experimental_group_n INTEGER,
    experimental_group_events INTEGER,
    control_group_n INTEGER,
    control_group_events INTEGER,
    
    -- 严重程度
    severity_grade1 INTEGER,
    severity_grade2 INTEGER,
    severity_grade3 INTEGER,
    severity_grade4 INTEGER,
    severity_grade5 INTEGER,
    
    -- 管理建议
    management TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_event_name (event_name)
);

-- =====================================================
-- 5. 参考文献相关表
-- =====================================================

-- 参考文献表
CREATE TABLE publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    
    -- 文献基本信息
    authors TEXT,
    title TEXT NOT NULL,
    journal VARCHAR(500),
    publication_year INTEGER,
    volume VARCHAR(50),
    issue VARCHAR(50),
    pages VARCHAR(50),
    
    -- 标识符
    doi VARCHAR(200),
    pmid VARCHAR(20),
    pmcid VARCHAR(20),
    
    -- 摘要和全文
    abstract TEXT,
    full_text_url TEXT,
    
    -- 发表类型
    publication_type VARCHAR(100), -- Journal Article, Conference Paper, etc.
    
    -- 会议信息
    conference_name VARCHAR(500),
    conference_date DATE,
    conference_location VARCHAR(200),
    
    -- 数据阶段
    data_stage VARCHAR(100), -- Interim, Final, Updated
    
    -- 系统字段
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_study_id (study_id),
    INDEX idx_pmid (pmid),
    INDEX idx_doi (doi),
    INDEX idx_publication_year (publication_year),
    INDEX idx_journal (journal)
);

-- 文献作者表
CREATE TABLE publication_authors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publication_id UUID NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    author_name VARCHAR(200) NOT NULL,
    author_order INTEGER,
    affiliation TEXT,
    
    INDEX idx_publication_id (publication_id),
    INDEX idx_author_name (author_name)
);

-- =====================================================
-- 6. 用户交互相关表
-- =====================================================

-- 用户收藏表
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (user_id, study_id),
    INDEX idx_user_id (user_id),
    INDEX idx_study_id (study_id)
);

-- 浏览历史表
CREATE TABLE user_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    study_id UUID NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    viewed_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_study_id (study_id),
    INDEX idx_viewed_at (viewed_at)
);

-- 用户搜索历史表
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    filters JSONB DEFAULT '{}',
    result_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- 用户反馈表
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    study_id UUID REFERENCES studies(id) ON DELETE CASCADE,
    
    feedback_type VARCHAR(50), -- error, suggestion, question
    feedback_text TEXT NOT NULL,
    
    -- 反馈状态
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, resolved
    
    -- 处理信息
    assigned_to UUID REFERENCES users(id),
    response_text TEXT,
    resolved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_study_id (study_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- =====================================================
-- 7. 系统配置和日志表
-- =====================================================

-- 系统配置表
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50), -- string, number, boolean, json
    description TEXT,
    is_editable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_config_key (config_key)
);

-- 系统日志表
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_data JSONB,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at),
    INDEX idx_resource (resource_type, resource_id)
);

-- 数据同步日志表
CREATE TABLE data_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_source VARCHAR(100) NOT NULL, -- ClinicalTrials.gov, PubMed, etc.
    sync_type VARCHAR(50), -- full, incremental
    
    -- 同步统计
    total_records INTEGER,
    new_records INTEGER,
    updated_records INTEGER,
    deleted_records INTEGER,
    error_records INTEGER,
    
    -- 时间信息
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    
    -- 状态
    status VARCHAR(50), -- running, completed, failed
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_data_source (data_source),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
);

-- =====================================================
-- 8. 插入初始数据
-- =====================================================

-- 插入系统角色
INSERT INTO roles (name, description, permissions) VALUES 
('admin', '系统管理员', '{"all": true}'),
('data_editor', '数据编辑员', '{"read": true, "write": true}'),
('viewer', '普通用户', '{"read": true}');

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description) VALUES 
('site_name', '肿瘤治疗进展查询系统', 'string', '网站名称'),
('site_description', '专业的肿瘤临床研究进展查询平台', 'string', '网站描述'),
('data_sync_interval_hours', '24', 'number', '数据同步间隔（小时）'),
('max_search_results', '1000', 'number', '最大搜索结果数'),
('session_timeout_minutes', '480', 'number', '会话超时时间（分钟）'),
('password_min_length', '8', 'number', '密码最小长度'),
('max_login_attempts', '5', 'number', '最大登录尝试次数');

-- =====================================================
-- 9. 创建视图（用于复杂查询优化）
-- =====================================================

-- 研究概览视图
CREATE VIEW study_overview AS
SELECT 
    s.id,
    s.nct_id,
    s.official_title,
    s.acronym,
    s.phase,
    s.status,
    s.start_date,
    s.completion_date,
    s.enrollment,
    s.sponsor_name,
    s.primary_endpoint,
    s.created_at,
    s.updated_at,
    
    -- 关联疾病
    ARRAY_AGG(DISTINCT c.name) AS conditions,
    
    -- 关联药物
    ARRAY_AGG(DISTINCT i.name) AS interventions,
    
    -- 关联分子靶标
    ARRAY_AGG(DISTINCT mt.name) AS molecular_targets,
    
    -- 最新发表文献
    MAX(p.publication_year) AS latest_publication_year
    
FROM studies s
    LEFT JOIN conditions c ON s.id = c.study_id
    LEFT JOIN interventions i ON s.id = i.study_id
    LEFT JOIN molecular_targets mt ON s.id = mt.study_id
    LEFT JOIN publications p ON s.id = p.study_id
    
WHERE s.is_active = TRUE
    
GROUP BY s.id, s.nct_id, s.official_title, s.acronym, s.phase, 
         s.status, s.start_date, s.completion_date, s.enrollment,
         s.sponsor_name, s.primary_endpoint, s.created_at, s.updated_at;

-- 研究结果汇总视图
CREATE VIEW study_results_summary AS
SELECT 
    s.id AS study_id,
    s.nct_id,
    s.official_title,
    
    -- OS结果
    (SELECT value FROM results r 
     WHERE r.study_id = s.id AND r.result_type = 'OS' 
     ORDER BY publication_date DESC LIMIT 1) AS os_result,
    
    -- PFS结果
    (SELECT value FROM results r 
     WHERE r.study_id = s.id AND r.result_type = 'PFS' 
     ORDER BY publication_date DESC LIMIT 1) AS pfs_result,
    
    -- ORR结果
    (SELECT value FROM results r 
     WHERE r.study_id = s.id AND r.result_type = 'ORR' 
     ORDER BY publication_date DESC LIMIT 1) AS orr_result,
    
    -- 最新结果发表日期
    (SELECT MAX(publication_date) FROM results r WHERE r.study_id = s.id) AS latest_result_date
    
FROM studies s
WHERE s.is_active = TRUE;

-- =====================================================
-- 10. 创建函数和触发器
-- =====================================================

-- 更新时间戳函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要自动更新updated_at的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_studies_updated_at BEFORE UPDATE ON studies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON interventions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conditions_updated_at BEFORE UPDATE ON conditions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_results_updated_at BEFORE UPDATE ON results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publications_updated_at BEFORE UPDATE ON publications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 11. 性能优化索引
-- =====================================================

-- 全文搜索索引
CREATE INDEX idx_studies_title_search ON studies USING gin(to_tsvector('english', official_title));
CREATE INDEX idx_studies_summary_search ON studies USING gin(to_tsvector('english', brief_summary));

-- 复合索引
CREATE INDEX idx_studies_phase_status ON studies(phase, status);
CREATE INDEX idx_studies_date_range ON studies(start_date, completion_date);
CREATE INDEX idx_conditions_name_study ON conditions(name, study_id);
CREATE INDEX idx_interventions_name_study ON interventions(name, study_id);

-- JSONB索引
CREATE INDEX idx_search_history_filters ON search_history USING gin(filters);
CREATE INDEX idx_system_logs_request ON system_logs USING gin(request_data);

-- =====================================================
-- 12. 数据完整性约束
-- =====================================================

-- 确保每个研究至少有一个条件
CREATE OR REPLACE FUNCTION check_study_has_condition()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM conditions WHERE study_id = NEW.id) THEN
        RAISE EXCEPTION 'Study must have at least one condition';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 文档结束
-- =====================================================

-- 备注：
-- 1. 所有UUID字段使用gen_random_uuid()生成
-- 2. 时间戳字段使用NOW()生成UTC时间
-- 3. 外键约束确保数据完整性
-- 4. 索引优化查询性能
-- 5. 视图简化复杂查询
-- 6. 触发器自动更新时间戳

-- 数据库维护命令：
-- 查看表大小：SELECT pg_size_pretty(pg_total_relation_size('studies'));
-- 重建索引：REINDEX INDEX idx_nct_id;
-- 更新统计信息：ANALYZE studies;
-- 备份数据库：pg_dump oncology_db > backup.sql