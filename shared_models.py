"""
Shared layer for the Clinical Trial API.

Contains:
  - search_clinicaltrials() helper
  - All Pydantic request/response models

Imported by every Action Group app so models are defined ONCE.
"""

import requests
from pydantic import BaseModel


# =========================
# Shared helper
# =========================

def search_clinicaltrials(query: str):
    try:
        url = "https://clinicaltrials.gov/api/v2/studies"
        params = {"query.term": query, "pageSize": 5}
        response = requests.get(url, params=params, timeout=20)
        data = response.json()
        studies = data.get("studies", [])
        results = []
        for study in studies:
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            title = identification.get("briefTitle")
            if title:
                results.append(title)
        return results
    except Exception as e:
        print("ClinicalTrials Error:", str(e))
        return []


# =========================
# Request Models
# =========================

class TTestRequest(BaseModel):
    effect_size: float
    alpha: float = 0.05
    power: float = 0.80
    ratio: float = 1.0


class ProportionRequest(BaseModel):
    p1: float
    p2: float
    alpha: float = 0.05
    power: float = 0.80
    dropout_rate: float = 0.0


class DesignRecommendRequest(BaseModel):
    study_description: str


class NonInferiorityBinaryRequest(BaseModel):
    control_rate: float
    treatment_rate: float
    margin: float
    alpha: float = 0.025
    power: float = 0.80
    dropout_rate: float = 0.0


class NonInferiorityContinuousRequest(BaseModel):
    mean_difference: float = 0.0
    sd: float
    margin: float
    alpha: float = 0.025
    power: float = 0.80
    dropout_rate: float = 0.0


class SurvivalRequest(BaseModel):
    hazard_ratio: float
    alpha: float = 0.05
    power: float = 0.80
    dropout_rate: float = 0.0


class ProtocolSampleSizeRequest(BaseModel):
    study_type: str
    sample_size_per_group: int
    total_sample_size: int
    dropout_rate: float = 0.0


class ProtocolEndpointsRequest(BaseModel):
    disease: str
    intervention: str
    primary_objective: str


class ProtocolEstimandRequest(BaseModel):
    treatment: str
    population: str
    endpoint: str


class SAPRequest(BaseModel):
    endpoint_type: str
    endpoint_name: str


class DesignRecommendV2Request(BaseModel):
    study_description: str


class SurvivalNonInferiorityRequest(BaseModel):
    hazard_ratio_margin: float
    alpha: float = 0.025
    power: float = 0.80
    dropout_rate: float = 0.0


class TrialSpecification(BaseModel):
    study_title: str | None = None
    study_design: str | None = None
    disease: str | None = None
    population: str | None = None
    intervention: str | None = None
    comparator: str | None = None
    primary_endpoint: str | None = None
    secondary_endpoints: list[str] = []
    endpoint_type: str | None = None
    estimand: str | None = None
    analysis_method: str | None = None
    sample_size_method: str | None = None
    recommended_sample_size_api: str | None = None
    recommended_protocol_api: str | None = None
    recommended_sap_api: str | None = None
    recommended_estimand_api: str | None = None
    similar_trials: list[str] = []
    endpoint_strategy_summary: str | None = None
    recommended_endpoint_type: str | None = None
    required_sample_size_inputs: list[str] = []
    alpha: float = 0.05
    power: float = 0.80


class StudyConceptRequest(BaseModel):
    study_description: str


class DesignDiscussionRequest(BaseModel):
    research_question: str


class DesignDiscussionResponse(BaseModel):
    research_question: str
    similar_trials: list[str] = []
    endpoint_options: list = []
    common_endpoint_types: list[str] = []
    common_sample_size_methods: list[str] = []
    recommendation: str | None = None


class AnalogousTrialRequest(BaseModel):
    research_question: str


class AnalogousTrialResponse(BaseModel):
    research_question: str
    similar_trials: list[str] = []
    common_endpoint_types: list[str] = []
    common_sample_size_methods: list[str] = []
    recommendation: str | None = None


class EvidenceReviewRequest(BaseModel):
    research_question: str


class EvidenceReviewResponse(BaseModel):
    research_question: str
    evidence_sources: list[str] = []
    similar_trials: list[str] = []
    similar_publications: list[str] = []
    similar_protocols: list[str] = []
    common_endpoints: list[str] = []
    common_analysis_methods: list[str] = []
    common_sample_size_methods: list[str] = []
    design_patterns: list[str] = []
    strengths: list[str] = []
    limitations: list[str] = []
    evidence_summary: str | None = None
    recommendation: str | None = None


class QueryIntelligenceRequest(BaseModel):
    research_question: str


class QueryIntelligenceResponse(BaseModel):
    research_question: str
    disease: str | None = None
    intervention: str | None = None
    outcome: str | None = None
    search_terms: list[str] = []


class ResearchQuestionRequest(BaseModel):
    research_question: str


class ResearchQuestionResponse(BaseModel):
    query_intelligence: dict
    evidence_review: dict
    design_discussion: dict
    recommended_trial_specification: dict


class DesignTradeoffRequest(BaseModel):
    research_question: str


class DesignTradeoffResponse(BaseModel):
    research_question: str
    options: list = []
    recommendation: str | None = None


class FeasibilityRequest(BaseModel):
    sample_size: int
    annual_eligible_patients: int
    consent_rate: float = 0.5
    number_of_sites: int = 1


class FeasibilityResponse(BaseModel):
    estimated_recruitment_rate: float
    estimated_accrual_years: float
    feasibility_rating: str
    recommendation: str


class FeasibilityOptimizationRequest(BaseModel):
    sample_size: int
    annual_eligible_patients: int
    consent_rate: float = 0.5
    number_of_sites: int = 1


class FeasibilityOptimizationResponse(BaseModel):
    current_accrual_years: float
    optimization_options: list = []


class BudgetRequest(BaseModel):
    sample_size: int
    number_of_sites: int = 1
    follow_up_years: float = 1.0


class BudgetResponse(BaseModel):
    coordinator_cost: float
    crc_cost: float
    lab_cost: float
    monitoring_cost: float
    statistics_cost: float
    publication_cost: float
    estimated_total_budget: float


class DesignSelectionRequest(BaseModel):
    research_question: str


class DesignSelectionResponse(BaseModel):
    research_question: str
    options: list = []
    recommendation: str | None = None


class DesignArchitectureRequest(BaseModel):
    research_question: str


class DesignArchitectureResponse(BaseModel):
    research_question: str
    architecture_options: list = []
    recommendation: str | None = None


class AdvancedStatisticalDesignRequest(BaseModel):
    research_question: str
    endpoint_type: str
    study_design: str


class AdvancedStatisticalDesignResponse(BaseModel):
    multiplicity_strategy: str
    alpha_control_strategy: str
    adaptive_reestimation: str
    competing_risk_strategy: str
    multistate_model_recommendation: str
    joint_model_recommendation: str
    bayesian_borrowing: str
    external_control_strategy: str
    recommendation: str


class AssumptionAnalysisRequest(BaseModel):
    parameter: str
    assumption: float
    source: str | None = None


class AssumptionAnalysisResponse(BaseModel):
    parameter: str
    assumption: float
    confidence_level: str
    risk_level: str
    optimistic_scenario: float
    expected_scenario: float
    conservative_scenario: float
    recommendation: str


class BiasAnalysisRequest(BaseModel):
    study_design: str
    endpoint_type: str


class BiasAnalysisResponse(BaseModel):
    biases: list = []
    recommendation: str


class MethodologistCritiqueRequest(BaseModel):
    study_design: str
    endpoint_type: str
    sample_size: int | None = None


class MethodologistCritiqueResponse(BaseModel):
    statistician_review: list = []
    irb_review: list = []
    dsmb_review: list = []
    journal_review: list = []


class StatisticalConsequenceRequest(BaseModel):
    option_a: str
    option_b: str


class StatisticalConsequenceResponse(BaseModel):
    comparison: list = []
    recommendation: str


class TrialLandscapeRequest(BaseModel):
    research_question: str


class TrialLandscapeResponse(BaseModel):
    research_question: str
    similar_trials: list[str] = []
    ongoing_trials: list[str] = []
    completed_trials: list[str] = []
    key_design_patterns: list[str] = []
    recommendation: str | None = None


class UnmetNeedResponse(BaseModel):
    research_question: str
    evidence_gap: str | None = None
    clinical_gap: str | None = None
    geographic_gap: str | None = None
    implementation_gap: str | None = None
    recommendation: str | None = None


class DesignPatternResponse(BaseModel):
    research_question: str
    common_designs: list[str] = []
    common_endpoints: list[str] = []
    common_followup: list[str] = []
    common_analysis_methods: list[str] = []
    common_sample_size_methods: list[str] = []
    recommendation: str | None = None


class EndpointIntelligenceResponse(BaseModel):
    research_question: str
    common_endpoints: list[str] = []
    endpoint_frequency: dict = {}
    control_rate_range: str | None = None
    event_rate_range: str | None = None
    effect_size_range: str | None = None
    recommendation: str | None = None


class InterimAnalysisRequest(BaseModel):
    study_design: str
    endpoint_type: str
    sample_size: int
    follow_up_years: float = 1.0


class InterimAnalysisV2Request(BaseModel):
    study_design: str
    endpoint_type: str
    sample_size: int
    follow_up_years: float


class InterimAnalysisV3Request(BaseModel):
    study_design: str
    endpoint_type: str
    sample_size: int
    follow_up_years: float
    event_driven: bool = False


class InterimAnalysisResponse(BaseModel):
    interim_analysis_recommended: bool
    dsmb_recommended: bool
    recommended_interims: int
    stopping_boundary: str | None = None
    rationale: str | None = None


class InterimAnalysisV2Response(BaseModel):
    information_fraction: str
    stopping_boundary: str
    futility_analysis: bool
    dsmb_required: bool
    recommendation: str


class InterimAnalysisV3Response(BaseModel):
    information_fraction: str
    alpha_spending_strategy: str
    event_trigger: str
    futility_rule: str
    early_success_rule: str
    dsmb_required: bool
    dsmb_meeting_frequency: str
    recommendation: str


class ClinicalTrialsGovRequest(BaseModel):
    study_title: str
    disease: str
    population: str
    intervention: str
    comparator: str | None = None
    primary_endpoint: str
    study_design: str


class ClinicalTrialsGovResponse(BaseModel):
    brief_title: str
    official_title: str
    brief_summary: str
    detailed_description: str
    primary_outcome_measure: str
    eligibility_criteria: str


class ClinicalTrialsGovV2Request(BaseModel):
    trial_specification: TrialSpecification


class ClinicalTrialsGovV2Response(BaseModel):
    brief_title: str
    official_title: str
    brief_summary: str
    detailed_description: str
    primary_outcome_measure: str
    eligibility_criteria: str


class CRFBuilderRequest(BaseModel):
    disease: str
    intervention: str
    primary_endpoint: str


class REDCapBuilderRequest(BaseModel):
    disease: str
    intervention: str
    primary_endpoint: str


class CRFBuilderResponse(BaseModel):
    screening_fields: list[str] = []
    baseline_fields: list[str] = []
    followup_fields: list[str] = []
    safety_fields: list[str] = []
    endpoint_fields: list[str] = []


class REDCapBuilderResponse(BaseModel):
    form_name: str
    variable_definitions: list = []


class REDCapBuilderV3Request(BaseModel):
    disease: str
    intervention: str
    primary_endpoint: str


class REDCapBuilderV3Response(BaseModel):
    visit_schedule: list[str] = []
    forms: list = []
    variable_metadata: list = []


class BrochureRequest(BaseModel):
    disease: str
    intervention: str
    study_rationale: str


class BrochureResponse(BaseModel):
    scientific_rationale: str
    unmet_need: str
    expected_impact: str


class AdvancedSAPRequest(BaseModel):
    endpoint_type: str
    endpoint_name: str


class AdvancedSAPResponse(BaseModel):
    analysis_population: str
    primary_analysis: str
    multiplicity_strategy: str
    covariate_adjustment: list[str] = []
    subgroup_analysis: list[str] = []
    missing_data_strategy: str
    sensitivity_analysis: list[str] = []


class TTERequest(BaseModel):
    research_question: str


class TTEV2Request(BaseModel):
    research_question: str


class TTEV3Request(BaseModel):
    research_question: str


class TTEResponse(BaseModel):
    eligibility_criteria: str
    time_zero: str
    treatment_strategy: str
    follow_up: str
    causal_contrast: str
    recommended_method: str


class TTEV2Response(BaseModel):
    eligibility_criteria: str
    time_zero: str
    treatment_strategy: str
    follow_up: str
    causal_contrast: str
    recommended_method: str
    sensitivity_analysis: str


class TTEV3Response(BaseModel):
    eligibility_criteria: str
    time_zero: str
    treatment_strategy: str
    follow_up: str
    causal_contrast: str
    recommended_method: str
    cloning_censoring_weighting: bool
    positivity_diagnostics: str
    weight_diagnostics: str
    sequential_exchangeability: str
    target_trial_bias_report: list[str] = []


class DiseaseKnowledgeRequest(BaseModel):
    disease: str


class DiseaseKnowledgeResponse(BaseModel):
    disease: str
    common_endpoints: list
    common_designs: list
    common_analysis_methods: list
    common_biases: list
    key_trials: list
    publication_considerations: list


class HepatologyIntelligenceRequest(BaseModel):
    disease: str


class HepatologyIntelligenceResponse(BaseModel):
    disease: str
    clinical_questions: list
    preferred_endpoints: list
    preferred_architectures: list
    preferred_statistics: list
    sample_size_considerations: list
    interim_analysis_considerations: list
    tte_considerations: list
    emerging_biomarkers: list
    emerging_therapeutics: list
    precision_hepatology: list
    reviewer_attack_points: list
    publication_opportunities: list


class IntelligenceUpdateRequest(BaseModel):
    disease: str
    update_domain: str = "all"


class IntelligenceUpdateResponse(BaseModel):
    disease: str
    update_domain: str
    intelligence_sources: list
    new_biomarkers: list
    new_therapeutics: list
    new_trial_designs: list
    new_statistical_methods: list
    publication_relevance: list
    potential_impact: list


class ResearchOpportunityRequest(BaseModel):
    disease: str
    research_focus: str | None = None


class ResearchOpportunityResponse(BaseModel):
    disease: str
    evidence_gap: list
    clinical_gap: list
    biomarker_gap: list
    therapeutic_gap: list
    trial_design_gap: list
    publication_opportunities: list
    competitive_density: str
    strategic_priority_score: int
    recommended_next_studies: list


class PrecisionHepatologyRequest(BaseModel):
    disease: str


class PrecisionHepatologyResponse(BaseModel):
    disease: str
    enrichment_strategies: list
    biomarker_strategies: list
    genetic_strategies: list
    immune_strategies: list
    ctDNA_strategies: list
    risk_prediction_strategies: list
    precision_trial_concepts: list


class FutureMethodologyRequest(BaseModel):
    disease: str


class FutureMethodologyResponse(BaseModel):
    disease: str
    emerging_trial_designs: list
    emerging_statistical_methods: list
    digital_biomarker_trends: list
    ai_trial_design_trends: list
    synthetic_control_trends: list
    federated_trial_trends: list
    adoption_timeline: list
    future_impact_assessment: list
