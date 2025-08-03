-- On Pulse Solutions Outreach System
-- Complete Database Schema v1.1 - Fixed Order
-- Last Updated: 2024

-- Drop existing schema if needed (uncomment to use)
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- =====================================================
-- PART 1: CREATE ALL TABLES (NO INDEXES YET)
-- =====================================================

-- 1. Main leads table
CREATE TABLE IF NOT EXISTS leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    title VARCHAR(100),
    company_name VARCHAR(255),
    domain VARCHAR(255),
    revenue INTEGER,
    employees INTEGER,
    industry VARCHAR(100),
    location VARCHAR(100),
    state_code VARCHAR(2),
    icp_score INTEGER,
    icp_breakdown JSONB,
    persona VARCHAR(50),
    campaign_angle VARCHAR(50),
    sequence_position INTEGER DEFAULT 0,
    last_email_sent TIMESTAMP,
    next_email_date DATE,
    sequence_status VARCHAR(20) DEFAULT 'active',
    apollo_person_data JSONB,
    apollo_org_data JSONB,
    perplexity_context JSONB,
    linkedin_data JSONB,
    data_quality_score DECIMAL(3,2),
    workflow_run_id UUID,
    batch_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Search history
CREATE TABLE IF NOT EXISTS search_history (
    search_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_hash VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(100),
    page_number INTEGER,
    leads_found INTEGER,
    leads_qualified INTEGER,
    search_params JSONB,
    apollo_credits_used INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 3. Suppression list
CREATE TABLE IF NOT EXISTS suppression_list (
    suppression_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255),
    domain VARCHAR(255),
    company_name VARCHAR(255),
    suppression_type VARCHAR(50),
    reason TEXT,
    source VARCHAR(50),
    added_date TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- 4. Override rules
CREATE TABLE IF NOT EXISTS override_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_type VARCHAR(50),
    scope VARCHAR(20),
    value VARCHAR(255),
    score_override INTEGER,
    campaign_override VARCHAR(50),
    reason TEXT,
    expires_at TIMESTAMP,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Campaign performance
CREATE TABLE IF NOT EXISTS campaign_performance (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    campaign_angle VARCHAR(50) NOT NULL,
    persona VARCHAR(50),
    industry VARCHAR(100),
    emails_sent INTEGER DEFAULT 0,
    unique_opens INTEGER DEFAULT 0,
    unique_clicks INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    positive_replies INTEGER DEFAULT 0,
    negative_replies INTEGER DEFAULT 0,
    meeting_requests INTEGER DEFAULT 0,
    ers_requests INTEGER DEFAULT 0,
    evgp_conversions INTEGER DEFAULT 0,
    open_rate DECIMAL(5,2),
    reply_rate DECIMAL(5,2),
    positive_rate DECIMAL(5,2),
    thompson_weight DECIMAL(5,4),
    sample_size INTEGER,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, campaign_angle, persona, industry)
);

-- 6. Campaign playbooks
CREATE TABLE IF NOT EXISTS campaign_playbooks (
    playbook_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_angle VARCHAR(50) NOT NULL,
    email_position INTEGER NOT NULL,
    variant VARCHAR(10) NOT NULL,
    guidelines JSONB NOT NULL,
    subject_patterns TEXT[],
    opening_approaches TEXT[],
    cta_styles TEXT[],
    performance_score DECIMAL(5,2),
    total_sends INTEGER DEFAULT 0,
    total_opens INTEGER DEFAULT 0,
    total_replies INTEGER DEFAULT 0,
    positive_replies INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'baseline',
    promoted_from_json BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    UNIQUE(campaign_angle, email_position, variant)
);

-- 7. Thompson Sampling weights
CREATE TABLE IF NOT EXISTS thompson_sampling_weights (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    campaign_angle VARCHAR(50) NOT NULL,
    successes INTEGER DEFAULT 1,
    failures INTEGER DEFAULT 1,
    current_weight DECIMAL(5,4),
    sample_size INTEGER,
    confidence_level DECIMAL(3,2),
    last_sampled_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, campaign_angle)
);

-- 8. Email engagement
CREATE TABLE IF NOT EXISTS email_engagement (
    engagement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(lead_id),
    campaign_angle VARCHAR(50),
    email_position INTEGER,
    playbook_id UUID REFERENCES campaign_playbooks(playbook_id),
    subject_line TEXT,
    preview_text TEXT,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    replied_at TIMESTAMP,
    unsubscribed_at TIMESTAMP,
    bounced_at TIMESTAMP,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    instantly_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. Reply classifications
CREATE TABLE IF NOT EXISTS reply_classifications (
    reply_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(lead_id),
    engagement_id UUID REFERENCES email_engagement(engagement_id),
    reply_text TEXT,
    reply_date TIMESTAMP,
    interest_level VARCHAR(20),
    sentiment VARCHAR(20),
    reply_type VARCHAR(50),
    objection_category VARCHAR(50),
    next_action VARCHAR(50),
    priority_level VARCHAR(20),
    classification_confidence DECIMAL(3,2),
    classified_by VARCHAR(50),
    classification_prompt_version VARCHAR(20),
    human_reviewed BOOLEAN DEFAULT FALSE,
    review_notes TEXT,
    classified_at TIMESTAMP DEFAULT NOW()
);

-- 10. Workflow runs
CREATE TABLE IF NOT EXISTS workflow_runs (
    workflow_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_number INTEGER NOT NULL,
    date DATE NOT NULL,
    scheduled_time TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    industry VARCHAR(100),
    location VARCHAR(100),
    search_params JSONB,
    campaign_weights JSONB,
    leads_pulled INTEGER DEFAULT 0,
    leads_qualified INTEGER DEFAULT 0,
    leads_rejected INTEGER DEFAULT 0,
    duplicates_found INTEGER DEFAULT 0,
    total_cost DECIMAL(10,2),
    cost_breakdown JSONB,
    cost_per_lead DECIMAL(10,4),
    status VARCHAR(20) DEFAULT 'pending',
    current_step VARCHAR(50),
    error_log JSONB,
    checkpoints JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 11. Workflow costs
CREATE TABLE IF NOT EXISTS workflow_costs (
    cost_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id UUID REFERENCES workflow_runs(workflow_run_id),
    date DATE NOT NULL,
    apollo_searches INTEGER DEFAULT 0,
    apollo_enrichments INTEGER DEFAULT 0,
    apollo_costs DECIMAL(10,4) DEFAULT 0,
    neverbounce_validations INTEGER DEFAULT 0,
    neverbounce_costs DECIMAL(10,4) DEFAULT 0,
    perplexity_queries INTEGER DEFAULT 0,
    perplexity_costs DECIMAL(10,4) DEFAULT 0,
    scrapingdog_profiles INTEGER DEFAULT 0,
    scrapingdog_costs DECIMAL(10,4) DEFAULT 0,
    openai_tokens INTEGER DEFAULT 0,
    openai_costs DECIMAL(10,4) DEFAULT 0,
    total_cost DECIMAL(10,2),
    leads_processed INTEGER,
    cost_per_lead DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 12. Workflow schedule
CREATE TABLE IF NOT EXISTS workflow_schedule (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    batch_number INTEGER NOT NULL,
    scheduled_time TIME NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(100),
    search_page INTEGER DEFAULT 1,
    campaign_weight_mode VARCHAR(20),
    fixed_weight_percentage INTEGER,
    campaign_weights JSONB,
    leads_per_workflow INTEGER DEFAULT 30,
    loops_per_workflow INTEGER DEFAULT 3,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, batch_number)
);

-- 13. Industry research cache
CREATE TABLE IF NOT EXISTS industry_research_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    research_query TEXT,
    perplexity_response JSONB,
    exit_multiples TEXT,
    industry_challenges TEXT[],
    regulatory_changes TEXT[],
    consolidation_activity TEXT,
    operational_problems TEXT[],
    success_stories TEXT[],
    growth_outlook TEXT,
    research_date DATE,
    expires_at TIMESTAMP,
    usage_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 14. Company intelligence cache
CREATE TABLE IF NOT EXISTS company_intelligence_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    apollo_data JSONB,
    linkedin_data JSONB,
    perplexity_data JSONB,
    revenue INTEGER,
    employees INTEGER,
    years_in_business INTEGER,
    industry VARCHAR(100),
    last_updated TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 15. Daily performance summary
CREATE TABLE IF NOT EXISTS daily_performance_summary (
    summary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE UNIQUE NOT NULL,
    total_workflows_run INTEGER,
    total_leads_pulled INTEGER,
    total_leads_qualified INTEGER,
    total_emails_sent INTEGER,
    total_opens INTEGER,
    total_replies INTEGER,
    positive_replies INTEGER,
    meetings_booked INTEGER,
    ers_requests INTEGER,
    evgp_conversions INTEGER,
    total_api_costs DECIMAL(10,2),
    cost_per_qualified_lead DECIMAL(10,4),
    cost_per_positive_reply DECIMAL(10,4),
    qualification_rate DECIMAL(5,2),
    open_rate DECIMAL(5,2),
    reply_rate DECIMAL(5,2),
    positive_reply_rate DECIMAL(5,2),
    best_campaign VARCHAR(50),
    worst_campaign VARCHAR(50),
    campaign_metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 16. A/B test results
CREATE TABLE IF NOT EXISTS ab_test_results (
    test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(100),
    test_type VARCHAR(50),
    variant_a JSONB,
    variant_b JSONB,
    variant_a_sends INTEGER,
    variant_a_opens INTEGER,
    variant_a_replies INTEGER,
    variant_b_sends INTEGER,
    variant_b_opens INTEGER,
    variant_b_replies INTEGER,
    statistical_significance DECIMAL(3,2),
    confidence_level DECIMAL(3,2),
    winner VARCHAR(10),
    start_date DATE,
    end_date DATE,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 17. System alerts
CREATE TABLE IF NOT EXISTS system_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(50),
    component VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    details JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 18. API usage tracking
CREATE TABLE IF NOT EXISTS api_usage_tracking (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    api_provider VARCHAR(50),
    requests_made INTEGER,
    requests_successful INTEGER,
    requests_failed INTEGER,
    rate_limit_hits INTEGER DEFAULT 0,
    credits_used INTEGER,
    credits_remaining INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, api_provider)
);

-- =====================================================
-- PART 2: CREATE ALL VIEWS
-- =====================================================

CREATE OR REPLACE VIEW active_sequence_leads AS
SELECT 
    l.lead_id,
    l.email,
    l.company_name,
    l.sequence_position,
    l.next_email_date,
    l.campaign_angle,
    cp.guidelines
FROM leads l
LEFT JOIN campaign_playbooks cp ON 
    cp.campaign_angle = l.campaign_angle 
    AND cp.email_position = l.sequence_position + 1
    AND cp.status = 'validated'
WHERE l.sequence_status = 'active'
    AND l.next_email_date <= CURRENT_DATE;

CREATE OR REPLACE VIEW todays_sending_queue AS
SELECT 
    COUNT(*) as total_to_send,
    campaign_angle,
    sequence_position,
    COUNT(*) as count_at_position
FROM leads
WHERE sequence_status = 'active'
    AND next_email_date = CURRENT_DATE
GROUP BY campaign_angle, sequence_position
ORDER BY sequence_position;

CREATE OR REPLACE VIEW campaign_performance_trends AS
SELECT 
    date,
    campaign_angle,
    SUM(emails_sent) as total_sent,
    AVG(open_rate) as avg_open_rate,
    AVG(reply_rate) as avg_reply_rate,
    AVG(positive_rate) as avg_positive_rate,
    SUM(evgp_conversions) as total_conversions
FROM campaign_performance
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY date, campaign_angle
ORDER BY date DESC, campaign_angle;

-- =====================================================
-- PART 3: CREATE ALL FUNCTIONS
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_next_email_date(
    current_position INTEGER,
    last_sent TIMESTAMP
) RETURNS DATE AS $$
BEGIN
    IF current_position <= 4 THEN
        RETURN DATE(last_sent) + INTERVAL '3 days';
    ELSE
        RETURN DATE(last_sent) + INTERVAL '4 days';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- PART 4: CREATE ALL TRIGGERS
-- =====================================================

DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
CREATE TRIGGER update_leads_updated_at 
    BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_campaign_performance_updated_at ON campaign_performance;
CREATE TRIGGER update_campaign_performance_updated_at 
    BEFORE UPDATE ON campaign_performance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_playbooks_updated_at ON campaign_playbooks;
CREATE TRIGGER update_playbooks_updated_at 
    BEFORE UPDATE ON campaign_playbooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_schedule_updated_at ON workflow_schedule;
CREATE TRIGGER update_schedule_updated_at 
    BEFORE UPDATE ON workflow_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- PART 5: CREATE ALL INDEXES
-- =====================================================

-- Leads table indexes
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_domain ON leads(domain);
CREATE INDEX IF NOT EXISTS idx_leads_icp ON leads(icp_score);
CREATE INDEX IF NOT EXISTS idx_leads_campaign ON leads(campaign_angle);
CREATE INDEX IF NOT EXISTS idx_leads_sequence ON leads(sequence_status, next_email_date);
CREATE INDEX IF NOT EXISTS idx_leads_workflow ON leads(workflow_run_id);

-- Search history indexes
CREATE INDEX IF NOT EXISTS idx_search_hash ON search_history(search_hash);
CREATE INDEX IF NOT EXISTS idx_search_params ON search_history(industry, location, page_number);

-- Suppression list indexes
CREATE INDEX IF NOT EXISTS idx_suppression_email ON suppression_list(email);
CREATE INDEX IF NOT EXISTS idx_suppression_domain ON suppression_list(domain);
CREATE INDEX IF NOT EXISTS idx_suppression_company ON suppression_list(company_name);

-- Override rules indexes
CREATE INDEX IF NOT EXISTS idx_override_lookup ON override_rules(scope, value);
CREATE INDEX IF NOT EXISTS idx_override_type ON override_rules(rule_type);

-- Campaign performance indexes
CREATE INDEX IF NOT EXISTS idx_campaign_perf_date ON campaign_performance(date, campaign_angle);

-- Playbook indexes
CREATE INDEX IF NOT EXISTS idx_playbook_lookup ON campaign_playbooks(campaign_angle, email_position, status);

-- Email engagement indexes
CREATE INDEX IF NOT EXISTS idx_engagement_lead ON email_engagement(lead_id);
CREATE INDEX IF NOT EXISTS idx_engagement_replied ON email_engagement(replied_at);
CREATE INDEX IF NOT EXISTS idx_engagement_campaign ON email_engagement(campaign_angle, email_position);

-- Reply classification indexes
CREATE INDEX IF NOT EXISTS idx_reply_lead ON reply_classifications(lead_id);
CREATE INDEX IF NOT EXISTS idx_reply_action ON reply_classifications(next_action, priority_level);
CREATE INDEX IF NOT EXISTS idx_reply_interest ON reply_classifications(interest_level);

-- Workflow indexes
CREATE INDEX IF NOT EXISTS idx_workflow_date ON workflow_runs(date, batch_number);
CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflow_runs(status);
CREATE INDEX IF NOT EXISTS idx_cost_date ON workflow_costs(date);
CREATE INDEX IF NOT EXISTS idx_cost_workflow ON workflow_costs(workflow_run_id);
CREATE INDEX IF NOT EXISTS idx_schedule_date ON workflow_schedule(date, scheduled_time);
CREATE INDEX IF NOT EXISTS idx_schedule_status ON workflow_schedule(status);

-- Cache indexes
CREATE INDEX IF NOT EXISTS idx_research_cache ON industry_research_cache(industry, location);
CREATE INDEX IF NOT EXISTS idx_research_expiry ON industry_research_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_company_domain ON company_intelligence_cache(domain);
CREATE INDEX IF NOT EXISTS idx_company_expiry ON company_intelligence_cache(expires_at);

-- System indexes
CREATE INDEX IF NOT EXISTS idx_alert_unresolved ON system_alerts(resolved, severity);
CREATE INDEX IF NOT EXISTS idx_alert_type ON system_alerts(alert_type, component);
CREATE INDEX IF NOT EXISTS idx_usage_date ON api_usage_tracking(date);

-- Composite/partial indexes
CREATE INDEX IF NOT EXISTS idx_leads_active_sequence 
    ON leads(sequence_status, next_email_date) 
    WHERE sequence_status = 'active';

CREATE INDEX IF NOT EXISTS idx_engagement_recent 
    ON email_engagement(sent_at) 
    WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days';

CREATE INDEX IF NOT EXISTS idx_replies_pending 
    ON reply_classifications(next_action, priority_level) 
    WHERE next_action IN ('follow_up', 'notify_founder', 'book_meeting');

-- =====================================================
-- PART 6: INSERT INITIAL DATA
-- =====================================================

INSERT INTO thompson_sampling_weights (date, campaign_angle, successes, failures, current_weight)
VALUES 
    (CURRENT_DATE, 'fear', 1, 1, 0.20),
    (CURRENT_DATE, 'legacy', 1, 1, 0.20),
    (CURRENT_DATE, 'peer', 1, 1, 0.20),
    (CURRENT_DATE, 'authority', 1, 1, 0.20),
    (CURRENT_DATE, 'diagnostic', 1, 1, 0.20)
ON CONFLICT DO NOTHING;

-- =====================================================
-- SCHEMA COMPLETE
-- =====================================================