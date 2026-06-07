from scipy.stats import norm
from math import log
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from statsmodels.stats.power import TTestIndPower, NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

app = FastAPI(
    servers=[
        {
            "url": "https://clinicaltrialapi-dqml.onrender.com"
        }
    ]
)

def search_clinicaltrials(
    query: str
):

    try:

        url = (
            "https://clinicaltrials.gov/api/v2/studies"
        )

        params = {
            "query.term": query,
            "pageSize": 5
        }

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        studies = data.get(
            "studies",
            []
        )

        results = []

        for study in studies:

            protocol = study.get(
                "protocolSection",
                {}
            )

            identification = protocol.get(
                "identificationModule",
                {}
            )

            title = identification.get(
                "briefTitle"
            )

            if title:

                results.append(title)

        return results

    except Exception as e:

        print(
            "ClinicalTrials Error:",
            str(e)
        )

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


# =========================
# Design Selection Engine
# =========================

class DesignSelectionRequest(BaseModel):

    research_question: str


class DesignSelectionResponse(BaseModel):

    research_question: str

    options: list = []

    recommendation: str | None = None


# =========================
# Design Architecture Engine
# =========================

class DesignArchitectureRequest(BaseModel):

    research_question: str


class DesignArchitectureResponse(BaseModel):

    research_question: str

    architecture_options: list = []

    recommendation: str | None = None


# =========================
# Advanced Statistical Design Engine
# =========================

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

# =========================
# Interim Analysis V3
# =========================

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

# =========================
# ClinicalTrials.gov V2
# =========================

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

# =========================
# REDCap Builder V3
# =========================

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

# =========================
# TTE V3
# =========================

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

# =========================
# Disease Knowledge Engine
# =========================

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


# =========================
# Hepatology Trial Intelligence
# =========================

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


# =========================
# Root Endpoint
# =========================

@app.get("/")
def root():
    return {
        "message": "Rachel Clinical Trial API"
    }


# =========================
# Design Recommendation
# =========================

@app.post("/design/recommend")
def recommend_design(req: DesignRecommendRequest):

    text = req.study_description.lower()
    print("INPUT:", text)

    binary_keywords = [
        "response",
        "response rate",
        "orr",
        "svr",
        "mortality",
        "remission",
        "clinical cure",
        "success rate"
    ]

    survival_keywords = [
        "overall survival",
        "os",
        "pfs",
        "dfs",
        "time to event",
        "survival"
    ]

    continuous_keywords = [
        "hba1c",
        "blood pressure",
        "ldl",
        "bmi",
        "weight",
        "quality of life",
        "score"
    ]

    for keyword in binary_keywords:
        if keyword in text:
            return {
                "endpoint_type": "binary",
                "recommended_method": "two-proportion superiority",
                "sample_size_api": "/sample-size/proportion",
                "reasoning": "Primary endpoint appears to be a proportion."
            }

    for keyword in survival_keywords:
        if keyword in text:
            return {
                "endpoint_type": "survival",
                "recommended_method": "log-rank test",
                "sample_size_api": "/sample-size/survival",
                "reasoning": "Primary endpoint appears to be time-to-event."
            }

    for keyword in continuous_keywords:
        if keyword in text:
            return {
                "endpoint_type": "continuous",
                "recommended_method": "two-sample t-test",
                "sample_size_api": "/sample-size/ttest",
                "reasoning": "Primary endpoint appears to be continuous."
            }

    return {
        "endpoint_type": "unknown",
        "recommended_method": "manual_review",
        "reasoning": "Unable to automatically classify endpoint."
    }

@app.post("/design/recommend-v2")
def recommend_design_v2(
    req: DesignRecommendV2Request
):

    text = req.study_description.lower()

    design = "unknown"
    endpoint_type = "unknown"
    sample_size_method = "manual_review"
    analysis_method = "manual_review"
    estimand = "treatment_policy"

    # randomized trial
    if (
        "randomized" in text
        or "randomised" in text
        or "rct" in text
    ):
        design = "parallel-group RCT"

    # binary endpoint
    if (
        "response" in text
        or "orr" in text
        or "remission" in text
        or "cure" in text
        or "fibrosis improvement" in text
    ):
        endpoint_type = "binary"
        sample_size_method = (
            "two-proportion superiority"
        )
        analysis_method = (
            "logistic regression"
        )

    # continuous endpoint
    elif (
        "hba1c" in text
        or "blood pressure" in text
        or "ldl" in text
        or "weight" in text
    ):
        endpoint_type = "continuous"
        sample_size_method = (
            "two-sample t-test"
        )
        analysis_method = (
            "ancova"
        )

    # survival endpoint
    elif (
        "overall survival" in text
        or "progression-free survival" in text
        or "disease-free survival" in text
        or "time to event" in text
    ):
        endpoint_type = "survival"
        sample_size_method = (
            "log-rank test"
        )
        analysis_method = (
            "cox proportional hazards"
        )

    return {
        "design": design,
        "endpoint_type": endpoint_type,
        "sample_size_method":
            sample_size_method,
        "analysis_method":
            analysis_method,
        "estimand": estimand
    }

# =========================
# T-Test Sample Size
# =========================

@app.post("/sample-size/ttest")
def calculate_ttest(req: TTestRequest):

    analysis = TTestIndPower()

    n = analysis.solve_power(
        effect_size=req.effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=req.ratio
    )

    justification = (
        f"A two-sample t-test requires approximately "
        f"{round(n)} participants per group to achieve "
        f"{req.power:.0%} power at a two-sided alpha of "
        f"{req.alpha}."
    )

    return {
        "endpoint_type": "continuous",
        "method": "two-sample t-test",
        "alpha": req.alpha,
        "power": req.power,
        "sample_size_per_group": round(n, 2),
        "protocol_justification": justification
    }


# =========================
# Proportion Sample Size
# =========================

@app.post("/sample-size/proportion")
def calculate_proportion(req: ProportionRequest):

    effect_size = proportion_effectsize(
        req.p1,
        req.p2
    )

    analysis = NormalIndPower()

    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=1
    )

    total_n = n * 2

    adjusted_total_n = total_n / (1 - req.dropout_rate)

    justification = (
        f"A total of {round(total_n)} participants "
        f"({round(n)} per group) are required to detect "
        f"a difference in proportions of "
        f"{req.p1:.0%} versus {req.p2:.0%}, "
        f"using a two-sided alpha of {req.alpha} "
        f"and power of {req.power:.0%}. "
        f"Assuming a dropout rate of "
        f"{req.dropout_rate:.0%}, "
        f"the adjusted target enrollment is "
        f"{round(adjusted_total_n)} participants."
    )

    return {
        "endpoint_type": "binary",
        "method": "two-proportion z-test",
        "p1": req.p1,
        "p2": req.p2,
        "alpha": req.alpha,
        "power": req.power,
        "dropout_rate": req.dropout_rate,
        "sample_size_per_group": round(n, 2),
        "total_sample_size": round(total_n, 2),
        "adjusted_total_sample_size": round(adjusted_total_n),
        "protocol_justification": justification
    }

@app.post("/sample-size/noninferiority/binary")
def calculate_noninferiority_binary(
    req: NonInferiorityBinaryRequest
):

    effect_size = proportion_effectsize(
        req.control_rate,
        req.control_rate - req.margin
    )

    analysis = NormalIndPower()

    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=1
    )

    total_n = n * 2

    adjusted_total_n = total_n / (
        1 - req.dropout_rate
    )

    justification = (
        f"A non-inferiority design was assumed. "
        f"The control response rate was "
        f"{req.control_rate:.0%}. "
        f"A non-inferiority margin of "
        f"{req.margin:.0%} was specified. "
        f"Using a one-sided alpha of "
        f"{req.alpha} and power of "
        f"{req.power:.0%}, "
        f"{round(n)} participants per group "
        f"are required. "
        f"Assuming a dropout rate of "
        f"{req.dropout_rate:.0%}, "
        f"the adjusted target enrollment is "
        f"{round(adjusted_total_n)} participants."
    )

    return {
        "design": "non-inferiority",
        "endpoint_type": "binary",
        "control_rate": req.control_rate,
        "treatment_rate": req.treatment_rate,
        "margin": req.margin,
        "alpha": req.alpha,
        "power": req.power,
        "dropout_rate": req.dropout_rate,
        "sample_size_per_group": round(n, 2),
        "total_sample_size": round(total_n, 2),
        "adjusted_total_sample_size": round(
            adjusted_total_n
        ),
        "protocol_justification": justification
    }

@app.post("/sample-size/noninferiority/continuous")
def calculate_noninferiority_continuous(
    req: NonInferiorityContinuousRequest
):

    effect_size = req.margin / req.sd

    analysis = TTestIndPower()

    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=1
    )

    total_n = n * 2

    adjusted_total_n = total_n / (
        1 - req.dropout_rate
    )

    justification = (
        f"A continuous non-inferiority design was assumed. "
        f"A non-inferiority margin of {req.margin} "
        f"and standard deviation of {req.sd} "
        f"were specified. "
        f"Using a one-sided alpha of {req.alpha} "
        f"and power of {req.power:.0%}, "
        f"{round(n)} participants per group are required. "
        f"Assuming a dropout rate of "
        f"{req.dropout_rate:.0%}, "
        f"the adjusted target enrollment is "
        f"{round(adjusted_total_n)} participants."
    )

    return {
        "design": "non-inferiority",
        "endpoint_type": "continuous",
        "mean_difference": req.mean_difference,
        "sd": req.sd,
        "margin": req.margin,
        "alpha": req.alpha,
        "power": req.power,
        "dropout_rate": req.dropout_rate,
        "sample_size_per_group": round(n, 2),
        "total_sample_size": round(total_n, 2),
        "adjusted_total_sample_size": round(
            adjusted_total_n
        ),
        "protocol_justification": justification
    }

@app.post("/sample-size/survival")
def calculate_survival(req: SurvivalRequest):

    z_alpha = norm.ppf(
        1 - req.alpha / 2
    )

    z_beta = norm.ppf(
        req.power
    )

    required_events = (
        (z_alpha + z_beta) ** 2
    ) / (
        log(req.hazard_ratio) ** 2
    )

    adjusted_events = (
        required_events /
        (1 - req.dropout_rate)
    )

    justification = (
        f"A survival superiority design was assumed. "
        f"Using a hazard ratio of "
        f"{req.hazard_ratio}, "
        f"a two-sided alpha of "
        f"{req.alpha}, "
        f"and power of "
        f"{req.power:.0%}, "
        f"{round(required_events)} events "
        f"are required. "
        f"Assuming a dropout rate of "
        f"{req.dropout_rate:.0%}, "
        f"the adjusted required events "
        f"are {round(adjusted_events)}."
    )

    return {
        "endpoint_type": "survival",
        "method": "log-rank",
        "hazard_ratio": req.hazard_ratio,
        "alpha": req.alpha,
        "power": req.power,
        "dropout_rate": req.dropout_rate,
        "required_events": round(
            required_events,
            2
        ),
        "adjusted_required_events": round(
            adjusted_events,
            2
        ),
        "protocol_justification": justification
    }

@app.post("/protocol/sample-size")
def generate_sample_size_protocol(
    req: ProtocolSampleSizeRequest
):

    protocol_text = (
        f"Sample Size Justification\n\n"
        f"The sample size was calculated using a "
        f"{req.study_type} design. "
        f"A total of {req.sample_size_per_group} "
        f"participants per group are required. "
        f"The planned total sample size is "
        f"{req.total_sample_size} participants. "
        f"To account for an anticipated dropout rate "
        f"of {req.dropout_rate:.0%}, the enrollment "
        f"target was adjusted accordingly."
    )

    return {
        "protocol_text": protocol_text
    }

@app.post("/protocol/endpoints")
def generate_protocol_endpoints(
    req: ProtocolEndpointsRequest
):

    primary_endpoint = (
        f"Assessment of {req.primary_objective} "
        f"in participants with {req.disease} "
        f"receiving {req.intervention}."
    )

    secondary_endpoints = [
        "Change in disease-related biomarkers.",
        "Change in laboratory parameters.",
        "Safety and tolerability outcomes."
    ]

    exploratory_endpoints = [
        "Patient-reported outcomes.",
        "Health-related quality of life.",
        "Exploratory biomarker analyses."
    ]

    return {
        "primary_endpoint": primary_endpoint,
        "secondary_endpoints": secondary_endpoints,
        "exploratory_endpoints": exploratory_endpoints
    }

@app.post("/protocol/estimand")
def generate_estimand(
    req: ProtocolEstimandRequest
):

    estimand_text = (
        f"The treatment policy estimand evaluates "
        f"the effect of {req.treatment} "
        f"in {req.population} "
        f"on the endpoint "
        f"'{req.endpoint}', "
        f"regardless of treatment discontinuation "
        f"or use of rescue medication."
    )

    return {
        "estimand_type": "treatment_policy",
        "population": req.population,
        "treatment": req.treatment,
        "endpoint": req.endpoint,
        "estimand_text": estimand_text
    }

@app.post("/sap/statistical-analysis-plan")
def generate_sap(
    req: SAPRequest
):

    endpoint_type = req.endpoint_type.lower()

    if endpoint_type == "binary":

        return {
            "analysis_population":
                "Intention-to-treat",

            "primary_analysis":
                "Logistic regression",

            "missing_data":
                "Multiple imputation",

            "sensitivity_analysis":
                "Per-protocol analysis"
        }

    if endpoint_type == "continuous":

        return {
            "analysis_population":
                "Intention-to-treat",

            "primary_analysis":
                "ANCOVA",

            "missing_data":
                "Multiple imputation",

            "sensitivity_analysis":
                "Mixed model repeated measures"
        }

    if endpoint_type == "survival":

        return {
            "analysis_population":
                "Intention-to-treat",

            "primary_analysis":
                "Log-rank test and Cox model",

            "missing_data":
                "Censoring rules predefined",

            "sensitivity_analysis":
                "Per-protocol analysis"
        }

    return {
        "message":
            "Endpoint type not supported"
    }

@app.post("/sample-size/noninferiority/survival")
def calculate_survival_noninferiority(
    req: SurvivalNonInferiorityRequest
):

    z_alpha = norm.ppf(
        1 - req.alpha
    )

    z_beta = norm.ppf(
        req.power
    )

    required_events = (
        (z_alpha + z_beta) ** 2
    ) / (
        log(req.hazard_ratio_margin) ** 2
    )

    adjusted_events = (
        required_events /
        (1 - req.dropout_rate)
    )

    justification = (
        f"A survival non-inferiority design was assumed. "
        f"A hazard ratio margin of "
        f"{req.hazard_ratio_margin} "
        f"was specified. "
        f"Using a one-sided alpha of "
        f"{req.alpha} and power of "
        f"{req.power:.0%}, "
        f"{round(required_events)} events "
        f"are required. "
        f"Assuming a dropout rate of "
        f"{req.dropout_rate:.0%}, "
        f"the adjusted required events are "
        f"{round(adjusted_events)}."
    )

    return {
        "design": "non-inferiority",
        "endpoint_type": "survival",
        "hazard_ratio_margin":
            req.hazard_ratio_margin,
        "alpha": req.alpha,
        "power": req.power,
        "dropout_rate": req.dropout_rate,
        "required_events":
            round(required_events, 2),
        "adjusted_required_events":
            round(adjusted_events, 2),
        "protocol_justification":
            justification
    }

@app.post(
    "/orchestrator/design-discussion",
    response_model=DesignDiscussionResponse
)
def design_discussion(
    req: DesignDiscussionRequest
):

    text = req.research_question.lower()

    similar_trials = []

    endpoint_options = []

    common_endpoint_types = []

    common_sample_size_methods = []

    recommendation = None

    # HBV functional cure example

    if (
        "functional cure" in text
        or "hbsag loss" in text
        or "stop therapy" in text
        or "stop treatment" in text
    ):

        similar_trials = [
            "FINITE",
            "Nuc-STOP",
            "HBV-STOP"
        ]

        endpoint_options = [

            {
                "endpoint":
                    "HBsAg loss at Week 96",

                "endpoint_type":
                    "binary",

                "sample_size_method":
                    "two-proportion superiority"
            },

            {
                "endpoint":
                    "Time to HBsAg loss",

                "endpoint_type":
                    "survival",

                "sample_size_method":
                    "log-rank test"
            }
        ]

        common_endpoint_types = [
            "binary",
            "survival"
        ]

        common_sample_size_methods = [
            "two-proportion superiority",
            "log-rank test"
        ]

        recommendation = (
            "Time to HBsAg loss"
        )

    return DesignDiscussionResponse(

        research_question=
            req.research_question,

        similar_trials=
            similar_trials,

        endpoint_options=
            endpoint_options,

        common_endpoint_types=
            common_endpoint_types,

        common_sample_size_methods=
            common_sample_size_methods,

        recommendation=
            recommendation
    )

@app.post(
    "/orchestrator/analogous-trials",
    response_model=AnalogousTrialResponse
)
def analogous_trials(
    req: AnalogousTrialRequest
):

    text = req.research_question.lower()

    similar_trials = []

    common_endpoint_types = []

    common_sample_size_methods = []

    recommendation = None

    # HBV functional cure

    if (
        "functional cure" in text
        or "hbsag loss" in text
        or "stop therapy" in text
        or "stop treatment" in text
        or "na withdrawal" in text
    ):

        similar_trials = [
            "FINITE",
            "Nuc-STOP",
            "HBV-STOP"
        ]

        common_endpoint_types = [
            "binary",
            "survival"
        ]

        common_sample_size_methods = [
            "two-proportion superiority",
            "log-rank test"
        ]

        recommendation = (
            "Most analogous trials used "
            "binary endpoints. "
            "Survival endpoints may be preferred "
            "when timing of functional cure is "
            "clinically important."
        )

    # Metabolic disease

    elif (
        "hba1c" in text
        or "diabetes" in text
        or "obesity" in text
        or "weight loss" in text
    ):

        similar_trials = [
            "STEP",
            "SURPASS"
        ]

        common_endpoint_types = [
            "continuous"
        ]

        common_sample_size_methods = [
            "two-sample t-test",
            "ANCOVA"
        ]

        recommendation = (
            "Continuous endpoints are commonly "
            "used in metabolic disease studies."
        )

    return AnalogousTrialResponse(

        research_question=
            req.research_question,

        similar_trials=
            similar_trials,

        common_endpoint_types=
            common_endpoint_types,

        common_sample_size_methods=
            common_sample_size_methods,

        recommendation=
            recommendation
    )

@app.post(
    "/orchestrator/evidence-review",
    response_model=EvidenceReviewResponse
)
def evidence_review(
    req: EvidenceReviewRequest
):

    text = req.research_question.lower()

    evidence_sources = []

    similar_trials = []

    similar_publications = []

    similar_protocols = []

    common_endpoints = []

    common_analysis_methods = []

    common_sample_size_methods = []

    design_patterns = []

    strengths = []

    limitations = []

    evidence_summary = None

    recommendation = None

    if (
        "functional cure" in text
        or "hbsag loss" in text
        or "stop therapy" in text
        or "stop treatment" in text
    ):

        evidence_sources = [
            "ClinicalTrials.gov",
            "PubMed",
            "Published Protocols"
        ]

        query = "hepatitis b"

        if "functional cure" in text:
            query = "hbsag loss hepatitis b"

        similar_trials = search_clinicaltrials(
            query
        )

        similar_publications = [
            "FINITE publication",
            "HBV-STOP publication"
        ]

        similar_protocols = [
            "FINITE protocol"
        ]

        common_endpoints = [
            "HBsAg loss at fixed timepoint",
            "Time to HBsAg loss"
        ]

        common_analysis_methods = [
            "Logistic regression",
            "Cox proportional hazards"
        ]

        common_sample_size_methods = [
            "Two-proportion superiority",
            "Log-rank test"
        ]

        design_patterns = [
            "Fixed follow-up endpoint assessment",
            "Off-treatment observation period",
            "Functional cure endpoint strategy"
        ]

        strengths = [
            "Clinically meaningful endpoint",
            "Simple interpretation",
            "Commonly used in HBV studies"
        ]

        limitations = [
            "Functional cure events are rare",
            "Long follow-up required",
            "Endpoint timing may be ignored"
        ]

        evidence_summary = (
            "Most published HBV withdrawal studies "
            "used binary functional cure endpoints. "
            "A smaller number used time-to-event "
            "approaches."
        )

        recommendation = (
            "Consider both binary and survival "
            "endpoint strategies."
        )

    return EvidenceReviewResponse(

        research_question=
            req.research_question,

        evidence_sources=
            evidence_sources,

        similar_trials=
            similar_trials,

        similar_publications=
            similar_publications,

        similar_protocols=
            similar_protocols,

        common_endpoints=
            common_endpoints,

        common_analysis_methods=
            common_analysis_methods,

        common_sample_size_methods=
            common_sample_size_methods,

        design_patterns=
            design_patterns,

        strengths=
            strengths,

        limitations=
            limitations,

        evidence_summary=
            evidence_summary,

        recommendation=
            recommendation
    )

@app.post(
    "/orchestrator/query-intelligence",
    response_model=QueryIntelligenceResponse
)
def query_intelligence(
    req: QueryIntelligenceRequest
):

    text = req.research_question.lower()

    disease = None

    intervention = None

    outcome = None

    search_terms = []

    if (
        "functional cure" in text
        or "hbsag loss" in text
        or "stop therapy" in text
        or "stop treatment" in text
    ):

        disease = "chronic hepatitis b"

        intervention = "NA withdrawal"

        outcome = "functional cure"

        search_terms = [
            "hepatitis b withdrawal",
            "nucleos(t)ide discontinuation",
            "hbsag loss",
            "functional cure"
        ]

    return QueryIntelligenceResponse(

        research_question=
            req.research_question,

        disease=
            disease,

        intervention=
            intervention,

        outcome=
            outcome,

        search_terms=
            search_terms
    )

@app.post(
    "/orchestrator/research-question",
    response_model=ResearchQuestionResponse
)
def research_question(
    req: ResearchQuestionRequest
):

    text = req.research_question.lower()

    # ------------------
    # Query Intelligence
    # ------------------

    disease = None

    intervention = None

    outcome = None

    search_terms = []

    if (
        "functional cure" in text
        or "hbsag loss" in text
        or "stop therapy" in text
        or "stop treatment" in text
    ):

        disease = "chronic hepatitis b"

        intervention = "NA withdrawal"

        outcome = "functional cure"

        search_terms = [
            "hepatitis b withdrawal",
            "nucleos(t)ide discontinuation",
            "hbsag loss",
            "functional cure"
        ]

    query_intelligence = {
        "disease": disease,
        "intervention": intervention,
        "outcome": outcome,
        "search_terms": search_terms
    }

    # ------------------
    # Evidence Review
    # ------------------

    similar_trials = search_clinicaltrials(
        "hepatitis b"
    )

    evidence_review = {
        "similar_trials": similar_trials
    }

    # ------------------
    # Design Discussion
    # ------------------

    design_discussion = {
        "recommended_endpoint":
            "Time to HBsAg loss",

        "endpoint_options": [
            "HBsAg loss at Week 96",
            "Time to HBsAg loss"
        ]
    }

    # ------------------
    # Trial Specification
    # ------------------

    recommended_trial_specification = {

        "study_design":
            "parallel-group RCT",

        "endpoint_type":
            "survival",

        "analysis_method":
            "cox proportional hazards",

        "sample_size_method":
            "log-rank test"
    }

    return ResearchQuestionResponse(

        query_intelligence=
            query_intelligence,

        evidence_review=
            evidence_review,

        design_discussion=
            design_discussion,

        recommended_trial_specification=
            recommended_trial_specification
    )

@app.post(
    "/orchestrator/design-tradeoff",
    response_model=DesignTradeoffResponse
)
def design_tradeoff(
    req: DesignTradeoffRequest
):

    text = req.research_question.lower()

    options = []

    recommendation = None

    # Relapse example

    if (
        "relapse" in text
        or "recurrence" in text
    ):

        options = [

            {
                "endpoint":
                    "Relapse by Month 6",

                "endpoint_type":
                    "binary",

                "advantages": [
                    "Simple interpretation",
                    "Easy sample size calculation",
                    "Common clinical trial design"
                ],

                "disadvantages": [
                    "Ignores timing information",
                    "Day 7 and Day 180 relapse are treated equally"
                ],

                "statistical_efficiency":
                    "moderate",

                "operational_feasibility":
                    "high",

                "sample_size_impact":
                    "often larger sample size"
            },

            {
                "endpoint":
                    "Time to relapse",

                "endpoint_type":
                    "survival",

                "advantages": [
                    "Uses timing information",
                    "More efficient use of events",
                    "Clinically informative"
                ],

                "disadvantages": [
                    "More complex assumptions",
                    "Requires survival analysis expertise"
                ],

                "statistical_efficiency":
                    "high",

                "operational_feasibility":
                    "moderate",

                "sample_size_impact":
                    "often lower event requirement"
            }
        ]

        recommendation = (
            "If the key question is whether relapse occurs, "
            "use a binary endpoint. "
            "If timing of relapse is clinically important, "
            "use a survival endpoint."
        )

    return DesignTradeoffResponse(

        research_question=
            req.research_question,

        options=
            options,

        recommendation=
            recommendation
    )

@app.post(
    "/orchestrator/feasibility-analysis",
    response_model=FeasibilityResponse
)
def feasibility_analysis(
    req: FeasibilityRequest
):

    estimated_recruitment_rate = (
        req.annual_eligible_patients
        * req.consent_rate
        * req.number_of_sites
    )

    if estimated_recruitment_rate == 0:

        estimated_accrual_years = 999

    else:

        estimated_accrual_years = (
            req.sample_size
            / estimated_recruitment_rate
        )

    if estimated_accrual_years <= 2:

        feasibility_rating = "excellent"

        recommendation = (
            "Recruitment appears highly feasible."
        )

    elif estimated_accrual_years <= 5:

        feasibility_rating = "moderate"

        recommendation = (
            "Recruitment is feasible but may "
            "require careful planning."
        )

    else:

        feasibility_rating = "poor"

        recommendation = (
            "Consider multicenter recruitment, "
            "broader eligibility criteria, "
            "or alternative endpoints."
        )

    return FeasibilityResponse(

        estimated_recruitment_rate=
            estimated_recruitment_rate,

        estimated_accrual_years=
            round(
                estimated_accrual_years,
                2
            ),

        feasibility_rating=
            feasibility_rating,

        recommendation=
            recommendation
    )

@app.post(
    "/orchestrator/study-concept",
    response_model=TrialSpecification
)
def orchestrate_study_concept(
    req: StudyConceptRequest
):

    text = req.study_description.lower()
    print(text)

    # -------------------------
    # TrialSpecification fields
    # -------------------------

    study_design = "unknown"

    disease = None

    population = None

    intervention = None

    comparator = None

    primary_endpoint = None

    endpoint_type = "unknown"

    estimand = "treatment_policy"

    analysis_method = "manual_review"

    sample_size_method = "manual_review"

    recommended_sample_size_api = None

    recommended_protocol_api = None

    recommended_sap_api = None

    recommended_estimand_api = None

    similar_trials = []

    endpoint_strategy_summary = None

    recommended_endpoint_type = None

    required_sample_size_inputs = []

    # -------------------------
    # Study Design
    # -------------------------

    if (
        "randomized" in text
        or "randomised" in text
        or "rct" in text
    ):
        study_design = "parallel-group RCT"

    # -------------------------
    # Disease
    # -------------------------

    if "masld" in text:
        disease = "MASLD"
        population = "MASLD patients"

    # -------------------------
    # Intervention
    # -------------------------

    if "semaglutide" in text:
        intervention = "semaglutide"

    # -------------------------
    # Comparator
    # -------------------------

    if "standard care" in text:
        comparator = "standard care"

    if "placebo" in text:
        comparator = "placebo"

    # -------------------------
    # Endpoint
    # -------------------------

    if "fibrosis improvement" in text:

        primary_endpoint = (
            "fibrosis improvement at week 48"
        )

        endpoint_type = "binary"

        analysis_method = (
            "logistic regression"
        )

        sample_size_method = (
            "two-proportion superiority"
        )

        recommended_sample_size_api = (
            "/sample-size/proportion"
        )

        recommended_protocol_api = (
            "/protocol/endpoints"
        )

        recommended_sap_api = (
            "/sap/statistical-analysis-plan"
        )

        recommended_estimand_api = (
            "/protocol/estimand"
        )

        similar_trials = [
            "FINITE",
            "Nuc-STOP",
            "HBV-STOP"
        ]

        endpoint_strategy_summary = (
            "Binary endpoint strategy commonly used "
            "for functional cure studies."
        )

        recommended_endpoint_type = "binary"

        required_sample_size_inputs = [
            "p1",
            "p2",
            "alpha",
            "power"
        ]

    elif "hba1c" in text:

        primary_endpoint = (
            "change in HbA1c"
        )

        endpoint_type = "continuous"

        analysis_method = (
            "ANCOVA"
        )

        sample_size_method = (
            "two-sample t-test"
        )

        recommended_sample_size_api = (
            "/sample-size/ttest"
        )

        recommended_protocol_api = (
            "/protocol/endpoints"
        )

        recommended_sap_api = (
            "/sap/statistical-analysis-plan"
        )

        recommended_estimand_api = (
            "/protocol/estimand"
        )

        endpoint_strategy_summary = (
            "Continuous endpoint strategy commonly "
            "used for metabolic outcome studies."
        )

        recommended_endpoint_type = "continuous"

        required_sample_size_inputs = [
            "effect_size",
            "alpha",
            "power"
        ]

    elif (
        "overall survival" in text
        or "progression-free survival" in text
    ):

        primary_endpoint = (
            "time-to-event endpoint"
        )

        endpoint_type = "survival"

        analysis_method = (
            "cox proportional hazards"
        )

        sample_size_method = (
            "log-rank test"
        )

        recommended_sample_size_api = (
            "/sample-size/survival"
        )

        recommended_protocol_api = (
            "/protocol/endpoints"
        )

        recommended_sap_api = (
            "/sap/statistical-analysis-plan"
        )

        recommended_estimand_api = (
            "/protocol/estimand"
        )

        endpoint_strategy_summary = (
            "Time-to-event endpoint strategy "
            "recommended when timing is clinically important."
        )

        recommended_endpoint_type = "survival"

        required_sample_size_inputs = [
            "hazard_ratio",
            "alpha",
            "power"
        ]

    print(
        "DEBUG:",
        disease,
        population,
        intervention,
        comparator,
        primary_endpoint
    )

    return TrialSpecification(

        study_design=study_design,

        disease=disease,

        population=population,

        intervention=intervention,

        comparator=comparator,

        primary_endpoint=primary_endpoint,

        endpoint_type=endpoint_type,

        estimand=estimand,

        analysis_method=analysis_method,

        sample_size_method=sample_size_method,

        recommended_sample_size_api=recommended_sample_size_api,

        recommended_protocol_api=recommended_protocol_api,

        recommended_sap_api=recommended_sap_api,

        recommended_estimand_api=recommended_estimand_api,

        similar_trials=similar_trials,

        endpoint_strategy_summary=endpoint_strategy_summary,

        recommended_endpoint_type=recommended_endpoint_type,

        required_sample_size_inputs=required_sample_size_inputs
        )

@app.post(
    "/orchestrator/feasibility-optimization",
    response_model=FeasibilityOptimizationResponse
)
def feasibility_optimization(
    req: FeasibilityOptimizationRequest
):

    recruitment_rate = (
        req.annual_eligible_patients
        * req.consent_rate
        * req.number_of_sites
    )

    if recruitment_rate == 0:

        current_accrual_years = 999

    else:

        current_accrual_years = (
            req.sample_size
            / recruitment_rate
        )

    optimization_options = []

    # Increase sites

    optimization_options.append({

        "strategy":
            "Increase to 5 sites",

        "estimated_accrual_years":
            round(
                current_accrual_years / 5,
                2
            )
    })

    optimization_options.append({

        "strategy":
            "Increase to 10 sites",

        "estimated_accrual_years":
            round(
                current_accrual_years / 10,
                2
            )
    })

    # Improve consent

    improved_rate = (
        req.annual_eligible_patients
        * 0.8
        * req.number_of_sites
    )

    optimization_options.append({

        "strategy":
            "Improve consent rate to 80%",

        "estimated_accrual_years":
            round(
                req.sample_size
                / improved_rate,
                2
            )
    })

    # Reduce sample size

    optimization_options.append({

        "strategy":
            "Reduce sample size by 30% through alternative endpoint strategy",

        "estimated_accrual_years":
            round(
                (req.sample_size * 0.7)
                / recruitment_rate,
                2
            )
    })

    return FeasibilityOptimizationResponse(

        current_accrual_years=
            round(
                current_accrual_years,
                2
            ),

        optimization_options=
            optimization_options
    )

@app.post(
    "/orchestrator/budget-estimation",
    response_model=BudgetResponse
)
def budget_estimation(
    req: BudgetRequest
):

    coordinator_cost = (
        50000
        * req.follow_up_years
    )

    crc_cost = (
        req.sample_size
        * 200
    )

    lab_cost = (
        req.sample_size
        * 500
    )

    monitoring_cost = (
        req.number_of_sites
        * 10000
    )

    statistics_cost = 25000

    publication_cost = 10000

    estimated_total_budget = (

        coordinator_cost

        + crc_cost

        + lab_cost

        + monitoring_cost

        + statistics_cost

        + publication_cost
    )

    return BudgetResponse(

        coordinator_cost=
            coordinator_cost,

        crc_cost=
            crc_cost,

        lab_cost=
            lab_cost,

        monitoring_cost=
            monitoring_cost,

        statistics_cost=
            statistics_cost,

        publication_cost=
            publication_cost,

        estimated_total_budget=
            estimated_total_budget
    )

@app.post(
    "/orchestrator/design-selection",
    response_model=DesignSelectionResponse
)
def design_selection(
    req: DesignSelectionRequest
):

    text = req.research_question.lower()

    options = []

    recommendation = None

    # Treatment effect question

    if (
        "improve" in text
        or "effect" in text
        or "efficacy" in text
        or "functional cure" in text
    ):

        options = [

            {
                "design":
                    "Single Arm",

                "advantages": [
                    "Fast",
                    "Lower cost"
                ],

                "disadvantages": [
                    "No concurrent control group",
                    "Weak causal inference"
                ],

                "budget_impact":
                    "low",

                "publication_value":
                    "moderate"
            },

            {
                "design":
                    "Randomized Controlled Trial",

                "advantages": [
                    "Strong causal inference",
                    "Regulatory familiarity"
                ],

                "disadvantages": [
                    "Higher cost",
                    "Longer recruitment"
                ],

                "budget_impact":
                    "high",

                "publication_value":
                    "high"
            },

            {
                "design":
                    "Pragmatic Clinical Trial",

                "advantages": [
                    "Real-world relevance",
                    "Generalizable results"
                ],

                "disadvantages": [
                    "Operational complexity"
                ],

                "budget_impact":
                    "moderate",

                "publication_value":
                    "high"
            },

            {
                "design":
                    "Target Trial Emulation",

                "advantages": [
                    "Uses existing data",
                    "Lower cost"
                ],

                "disadvantages": [
                    "Residual confounding",
                    "Requires observational data"
                ],

                "budget_impact":
                    "low",

                "publication_value":
                    "moderate"
            }
        ]

        recommendation = (
            "Randomized Controlled Trial "
            "remains the preferred design "
            "when causal treatment effect "
            "estimation is the primary goal."
        )

    return DesignSelectionResponse(

        research_question=
            req.research_question,

        options=
            options,

        recommendation=
            recommendation
    )

# =========================
# Design Architecture Engine
# =========================

@app.post(
    "/orchestrator/design-architecture",
    response_model=DesignArchitectureResponse
)
def design_architecture(
    req: DesignArchitectureRequest
):

    options = [

        {
            "architecture":
                "Parallel-group RCT",

            "why_use":
                "Strong causal inference",

            "why_not":
                "Higher cost and longer recruitment",

            "operational_complexity":
                "moderate",

            "statistical_complexity":
                "moderate",

            "publication_potential":
                "high"
        },

        {
            "architecture":
                "Adaptive Trial",

            "why_use":
                "Efficient use of resources",

            "why_not":
                "Requires complex planning",

            "operational_complexity":
                "high",

            "statistical_complexity":
                "high",

            "publication_potential":
                "very high"
        },

        {
            "architecture":
                "Platform Trial",

            "why_use":
                "Multiple interventions evaluated simultaneously",

            "why_not":
                "Substantial infrastructure required",

            "operational_complexity":
                "very high",

            "statistical_complexity":
                "very high",

            "publication_potential":
                "very high"
        },

        {
            "architecture":
                "Cluster RCT",

            "why_use":
                "Useful when individual randomization is difficult",

            "why_not":
                "Requires ICC adjustment",

            "operational_complexity":
                "high",

            "statistical_complexity":
                "high",

            "publication_potential":
                "high"
        },

        {
            "architecture":
                "Stepped Wedge Trial",

            "why_use":
                "Facilitates phased implementation",

            "why_not":
                "Complex analysis",

            "operational_complexity":
                "high",

            "statistical_complexity":
                "high",

            "publication_potential":
                "high"
        }
    ]

    recommendation = (
        "Parallel-group RCT remains the default architecture. "
        "Adaptive and platform designs should be considered when "
        "multiple interventions or efficiency gains are priorities."
    )

    return DesignArchitectureResponse(

        research_question=
            req.research_question,

        architecture_options=
            options,

        recommendation=
            recommendation
    )

# =========================
# Advanced Statistical Design Engine
# =========================

@app.post(
    "/orchestrator/advanced-statistical-design",
    response_model=AdvancedStatisticalDesignResponse
)
def advanced_statistical_design(
    req: AdvancedStatisticalDesignRequest
):

    multiplicity_strategy = (
        "Hierarchical Testing"
    )

    alpha_control_strategy = (
        "Family-wise Error Control"
    )

    adaptive_reestimation = (
        "Consider adaptive sample size re-estimation if recruitment uncertainty exists."
    )

    competing_risk_strategy = (
        "Fine-Gray model should be considered when competing risks are present."
    )

    multistate_model_recommendation = (
        "Consider multi-state models when disease transitions are clinically relevant."
    )

    joint_model_recommendation = (
        "Consider joint modeling when longitudinal biomarkers and time-to-event outcomes coexist."
    )

    bayesian_borrowing = (
        "Historical borrowing may be considered if external evidence is robust."
    )

    external_control_strategy = (
        "External controls may be considered when randomization is infeasible."
    )

    recommendation = (
        "Advanced statistical design considerations should be prespecified in the SAP and protocol."
    )

    return AdvancedStatisticalDesignResponse(

        multiplicity_strategy=
            multiplicity_strategy,

        alpha_control_strategy=
            alpha_control_strategy,

        adaptive_reestimation=
            adaptive_reestimation,

        competing_risk_strategy=
            competing_risk_strategy,

        multistate_model_recommendation=
            multistate_model_recommendation,

        joint_model_recommendation=
            joint_model_recommendation,

        bayesian_borrowing=
            bayesian_borrowing,

        external_control_strategy=
            external_control_strategy,

        recommendation=
            recommendation
    )


@app.post(
    "/orchestrator/disease-knowledge",
    response_model=DiseaseKnowledgeResponse
)
def disease_knowledge(
    req: DiseaseKnowledgeRequest
):

    disease = req.disease.lower()

    if disease == "hbv":

        return DiseaseKnowledgeResponse(
            disease=req.disease,
            common_endpoints=[
                "HBsAg Loss",
                "Functional Cure",
                "Clinical Relapse",
                "Virological Relapse"
            ],
            common_designs=[
                "Single Arm",
                "RCT",
                "Target Trial Emulation"
            ],
            common_analysis_methods=[
                "Logistic Regression",
                "Cox Regression",
                "Competing Risk"
            ],
            common_biases=[
                "Restart-treatment Bias",
                "Informative Censoring"
            ],
            key_trials=[
                "FINITE",
                "HBV-STOP",
                "Nuc-STOP"
            ],
            publication_considerations=[
                "Functional cure remains a high-impact endpoint.",
                "Time-to-HBsAg loss may improve publication value."
            ]
        )

    return DiseaseKnowledgeResponse(
        disease=req.disease,
        common_endpoints=[],
        common_designs=[],
        common_analysis_methods=[],
        common_biases=[],
        key_trials=[],
        publication_considerations=[]
    )

@app.post(
    "/orchestrator/hepatology-intelligence",
    response_model=HepatologyIntelligenceResponse
)
def hepatology_intelligence(
    req: HepatologyIntelligenceRequest
):

    disease = req.disease.lower()

    if disease == "hbv":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Functional Cure",
                "Finite Therapy",
                "Relapse Prediction",
                "Biomarker-guided Stopping"
            ],

            preferred_endpoints=[
                "HBsAg Loss",
                "Functional Cure",
                "Time-to-HBsAg Loss"
            ],

            preferred_architectures=[
                "Adaptive Trial",
                "Biomarker-guided Trial",
                "Target Trial Emulation"
            ],

            preferred_statistics=[
                "Competing Risk",
                "Joint Models",
                "Dynamic Treatment Regimes"
            ],

            sample_size_considerations=[
                "Functional cure rate",
                "Relapse rate",
                "Dropout rate"
            ],

            interim_analysis_considerations=[
                "DSMB",
                "Event-driven monitoring"
            ],

            tte_considerations=[
                "IPTW",
                "MSM",
                "CCW"
            ],

            emerging_biomarkers=[
                "HBcrAg",
                "HBV RNA",
                "qHBsAg"
            ],

            emerging_therapeutics=[
                "siRNA",
                "ASO",
                "CAM",
                "Therapeutic Vaccine"
            ],

            precision_hepatology=[
                "Biomarker-guided stopping",
                "Relapse prediction"
            ],

            reviewer_attack_points=[
                "Restart-treatment bias",
                "Informative censoring",
                "Immortal time bias"
            ],

            publication_opportunities=[
                "Functional cure",
                "Biomarker-guided withdrawal"
            ]
        )

    # =========================
    # MASLD / MASH
    # =========================

    elif disease in ["masld", "mash"]:

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Fibrosis Improvement",
                "MASH Resolution",
                "Histology-free Endpoints"
            ],

            preferred_endpoints=[
                "Fibrosis Improvement",
                "MASH Resolution",
                "MRI-PDFF",
                "ELF Score"
            ],

            preferred_architectures=[
                "Adaptive Trial",
                "Adaptive Enrichment",
                "Master Protocol"
            ],

            preferred_statistics=[
                "Bayesian Adaptive Design",
                "Joint Models",
                "Adaptive Re-estimation"
            ],

            sample_size_considerations=[
                "Fibrosis response rate",
                "Biopsy attrition rate"
            ],

            interim_analysis_considerations=[
                "DSMB",
                "Futility Assessment"
            ],

            tte_considerations=[
                "IPTW",
                "MSM"
            ],

            emerging_biomarkers=[
                "ELF",
                "PRO-C3",
                "AI Pathology"
            ],

            emerging_therapeutics=[
                "THR-beta Agonists",
                "GLP-1",
                "Combination Therapy"
            ],

            precision_hepatology=[
                "Risk Enrichment",
                "Fibrosis Stratification"
            ],

            reviewer_attack_points=[
                "Missing Histology",
                "Biopsy Attrition"
            ],

            publication_opportunities=[
                "Histology-free Endpoints",
                "Combination Therapy"
            ]
        )

    # =========================
    # HCC
    # =========================

    elif disease == "hcc":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Recurrence Prevention",
                "Advanced HCC",
                "Immunotherapy Sequencing"
            ],

            preferred_endpoints=[
                "Overall Survival",
                "Progression-Free Survival",
                "Recurrence-Free Survival"
            ],

            preferred_architectures=[
                "Platform Trial",
                "Adaptive Trial",
                "Master Protocol"
            ],

            preferred_statistics=[
                "Competing Risk",
                "Multi-state Models",
                "Joint Frailty Models"
            ],

            sample_size_considerations=[
                "Event Rate",
                "Overall Survival"
            ],

            interim_analysis_considerations=[
                "Event-driven Monitoring",
                "DSMB"
            ],

            tte_considerations=[
                "IPTW",
                "CCW"
            ],

            emerging_biomarkers=[
                "ctDNA",
                "MRD"
            ],

            emerging_therapeutics=[
                "IO+IO",
                "IO+TKI"
            ],

            precision_hepatology=[
                "ctDNA-guided Therapy"
            ],

            reviewer_attack_points=[
                "Post-progression Therapy",
                "Competing Risk"
            ],

            publication_opportunities=[
                "ctDNA-guided Strategies",
                "Platform Trials"
            ]
        )

    # =========================
    # CIRRHOSIS
    # =========================

    elif disease == "cirrhosis":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Decompensation Prevention",
                "ACLF Prevention"
            ],

            preferred_endpoints=[
                "Decompensation",
                "Transplant-free Survival",
                "Overall Survival"
            ],

            preferred_architectures=[
                "Event-driven RCT"
            ],

            preferred_statistics=[
                "Competing Risk",
                "Multi-state Models"
            ],

            sample_size_considerations=[
                "Decompensation Rate"
            ],

            interim_analysis_considerations=[
                "Event-driven DSMB"
            ],

            tte_considerations=[
                "IPTW"
            ],

            emerging_biomarkers=[
                "Frailty Metrics"
            ],

            emerging_therapeutics=[
                "Disease-modifying Strategies"
            ],

            precision_hepatology=[
                "Risk Stratification"
            ],

            reviewer_attack_points=[
                "Competing Risk",
                "Informative Censoring"
            ],

            publication_opportunities=[
                "Decompensation Prevention"
            ]
        )

    # =========================
    # PORTAL HYPERTENSION
    # =========================

    elif disease == "portal hypertension":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "HVPG Reduction",
                "Variceal Bleeding Prevention"
            ],

            preferred_endpoints=[
                "HVPG",
                "Variceal Bleeding",
                "Decompensation"
            ],

            preferred_architectures=[
                "RCT"
            ],

            preferred_statistics=[
                "Competing Risk"
            ],

            sample_size_considerations=[
                "Bleeding Event Rate"
            ],

            interim_analysis_considerations=[
                "Safety Monitoring"
            ],

            tte_considerations=[
                "IPTW"
            ],

            emerging_biomarkers=[
                "Non-invasive Portal Pressure Markers"
            ],

            emerging_therapeutics=[
                "Portal Pressure Modulators"
            ],

            precision_hepatology=[
                "HVPG-guided Therapy"
            ],

            reviewer_attack_points=[
                "Death as Competing Risk",
                "Transplant as Competing Risk"
            ],

            publication_opportunities=[
                "HVPG-guided Strategies"
            ]
        )

    # =========================
    # PBC
    # =========================

    elif disease == "pbc":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Biochemical Response",
                "Long-term Outcomes"
            ],

            preferred_endpoints=[
                "ALP",
                "Bilirubin"
            ],

            preferred_architectures=[
                "Parallel-group RCT"
            ],

            preferred_statistics=[
                "ANCOVA"
            ],

            sample_size_considerations=[
                "ALP Response Rate"
            ],

            interim_analysis_considerations=[
                "DSMB"
            ],

            tte_considerations=[],

            emerging_biomarkers=[
                "ELF"
            ],

            emerging_therapeutics=[
                "FXR Agonists",
                "PPAR Agonists"
            ],

            precision_hepatology=[],

            reviewer_attack_points=[
                "Surrogate Endpoint Validity"
            ],

            publication_opportunities=[
                "Long-term Outcome Studies"
            ]
        )

    # =========================
    # AIH
    # =========================

    elif disease == "aih":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Remission",
                "Relapse Prevention"
            ],

            preferred_endpoints=[
                "Biochemical Remission",
                "Histologic Remission"
            ],

            preferred_architectures=[
                "Registry",
                "Pragmatic Trial"
            ],

            preferred_statistics=[
                "Bayesian Design"
            ],

            sample_size_considerations=[
                "Rare Disease Recruitment"
            ],

            interim_analysis_considerations=[],

            tte_considerations=[],

            emerging_biomarkers=[
                "Immune Signatures"
            ],

            emerging_therapeutics=[
                "Steroid-sparing Strategies"
            ],

            precision_hepatology=[],

            reviewer_attack_points=[
                "Small Sample Size"
            ],

            publication_opportunities=[
                "Rare Disease Methodology"
            ]
        )

    # =========================
    # ALD
    # =========================

    elif disease == "ald":

        return HepatologyIntelligenceResponse(

            disease=req.disease,

            clinical_questions=[
                "Alcoholic Hepatitis",
                "Abstinence Intervention"
            ],

            preferred_endpoints=[
                "Overall Survival",
                "Liver-related Outcomes"
            ],

            preferred_architectures=[
                "Pragmatic Trial"
            ],

            preferred_statistics=[
                "Competing Risk"
            ],

            sample_size_considerations=[
                "Survival Event Rate"
            ],

            interim_analysis_considerations=[
                "Safety Monitoring"
            ],

            tte_considerations=[
                "IPTW"
            ],

            emerging_biomarkers=[
                "Alcohol Use Biomarkers"
            ],

            emerging_therapeutics=[
                "Anti-inflammatory Strategies"
            ],

            precision_hepatology=[],

            reviewer_attack_points=[
                "Adherence Bias",
                "Survivor Bias"
            ],

            publication_opportunities=[
                "Alcohol Abstinence Strategies"
            ]
        )

    return HepatologyIntelligenceResponse(

        disease=req.disease,

        clinical_questions=[],

        preferred_endpoints=[],

        preferred_architectures=[],

        preferred_statistics=[],

        sample_size_considerations=[],

        interim_analysis_considerations=[],

        tte_considerations=[],

        emerging_biomarkers=[],

        emerging_therapeutics=[],

        precision_hepatology=[],

        reviewer_attack_points=[],

        publication_opportunities=[]
    )

@app.post(
    "/orchestrator/assumption-analysis",
    response_model=AssumptionAnalysisResponse
)
def assumption_analysis(
    req: AssumptionAnalysisRequest
):

    confidence = "moderate"

    risk = "moderate"

    optimistic = round(
        req.assumption * 1.5,
        4
    )

    expected = req.assumption

    conservative = round(
        req.assumption * 0.5,
        4
    )

    recommendation = (
        "Sensitivity analyses should be "
        "performed using optimistic and "
        "conservative assumptions."
    )

    return AssumptionAnalysisResponse(
        parameter=req.parameter,
        assumption=req.assumption,
        confidence_level=confidence,
        risk_level=risk,
        optimistic_scenario=optimistic,
        expected_scenario=expected,
        conservative_scenario=conservative,
        recommendation=recommendation
    )

@app.post(
    "/orchestrator/bias-analysis",
    response_model=BiasAnalysisResponse
)
def bias_analysis(
    req: BiasAnalysisRequest
):

    biases = []

    design = req.study_design.lower()

    if "single" in design:

        biases.extend([
            {
                "bias":
                    "selection bias",
                "severity":
                    "high",
                "mitigation":
                    "randomized control group"
            },
            {
                "bias":
                    "historical control bias",
                "severity":
                    "high",
                "mitigation":
                    "concurrent control"
            }
        ])

    elif "rct" in design:

        biases.extend([
            {
                "bias":
                    "attrition bias",
                "severity":
                    "moderate",
                "mitigation":
                    "retention strategy"
            }
        ])

    elif "tte" in design:

        biases.extend([
            {
                "bias":
                    "immortal time bias",
                "severity":
                    "high",
                "mitigation":
                    "target trial alignment"
            }
        ])

    return BiasAnalysisResponse(
        biases=biases,
        recommendation=
            "Bias mitigation strategies should be documented."
    )

@app.post(
    "/orchestrator/methodologist-critique",
    response_model=MethodologistCritiqueResponse
)
def methodologist_critique(
    req: MethodologistCritiqueRequest
):

    statistician = []

    irb = []

    dsmb = []

    journal = []

    if req.sample_size:

        if req.sample_size < 50:

            statistician.append(
                "Potentially underpowered study."
            )

    if req.endpoint_type == "composite":

        journal.append(
            "Composite endpoint may have limited clinical interpretability."
        )

    irb.append(
        "Assess participant burden and visit schedule."
    )

    dsmb.append(
        "Review safety monitoring requirements."
    )

    return MethodologistCritiqueResponse(
        statistician_review=statistician,
        irb_review=irb,
        dsmb_review=dsmb,
        journal_review=journal
    )

@app.post(
    "/orchestrator/statistical-consequence",
    response_model=StatisticalConsequenceResponse
)
def statistical_consequence(
    req: StatisticalConsequenceRequest
):

    comparison = []

    if (
        req.option_a.lower() == "binary"
        and
        req.option_b.lower() == "survival"
    ):

        comparison = [

            {
                "domain":
                    "sample_size",

                "binary":
                    "often larger",

                "survival":
                    "event-driven"
            },

            {
                "domain":
                    "information",

                "binary":
                    "timing ignored",

                "survival":
                    "timing preserved"
            },

            {
                "domain":
                    "analysis",

                "binary":
                    "logistic regression",

                "survival":
                    "cox model"
            }
        ]

    return StatisticalConsequenceResponse(
        comparison=comparison,
        recommendation=
            "Use survival endpoints when timing is clinically important."
    )

@app.post(
    "/orchestrator/trial-landscape",
    response_model=TrialLandscapeResponse
)
def trial_landscape(
    req: TrialLandscapeRequest
):

    text = req.research_question.lower()

    similar_trials = []

    ongoing_trials = []

    completed_trials = []

    patterns = []

    recommendation = None

    if (
        "functional cure" in text
        or "hbsag loss" in text
        or "na withdrawal" in text
    ):

        similar_trials = [
            "FINITE",
            "HBV-STOP",
            "Nuc-STOP"
        ]

        completed_trials = similar_trials

        patterns = [
            "off-treatment follow-up",
            "functional cure endpoint",
            "relapse monitoring"
        ]

        recommendation = (
            "Several analogous HBV withdrawal studies exist."
        )

    return TrialLandscapeResponse(
        research_question=req.research_question,
        similar_trials=similar_trials,
        ongoing_trials=ongoing_trials,
        completed_trials=completed_trials,
        key_design_patterns=patterns,
        recommendation=recommendation
    )

@app.post(
    "/orchestrator/unmet-need",
    response_model=UnmetNeedResponse
)
def unmet_need(
    req: TrialLandscapeRequest
):

    text = req.research_question.lower()

    evidence_gap = None
    clinical_gap = None
    geographic_gap = None
    implementation_gap = None
    recommendation = None

    if (
        "functional cure" in text
        or "hbsag loss" in text
    ):

        evidence_gap = (
            "Limited randomized evidence exists."
        )

        clinical_gap = (
            "Functional cure remains uncommon."
        )

        geographic_gap = (
            "Asian data remain limited."
        )

        implementation_gap = (
            "Optimal patient selection remains unclear."
        )

        recommendation = (
            "Additional studies remain justified."
        )

    return UnmetNeedResponse(
        research_question=req.research_question,
        evidence_gap=evidence_gap,
        clinical_gap=clinical_gap,
        geographic_gap=geographic_gap,
        implementation_gap=implementation_gap,
        recommendation=recommendation
    )

@app.post(
    "/orchestrator/design-patterns",
    response_model=DesignPatternResponse
)
def design_patterns(
    req: TrialLandscapeRequest
):

    text = req.research_question.lower()

    designs = []
    endpoints = []
    followup = []
    analyses = []
    sample_size_methods = []
    recommendation = None

    if (
        "functional cure" in text
        or "hbsag loss" in text
    ):

        designs = [
            "single arm",
            "randomized trial"
        ]

        endpoints = [
            "HBsAg loss",
            "Time to HBsAg loss"
        ]

        followup = [
            "48 weeks",
            "96 weeks",
            "144 weeks"
        ]

        analyses = [
            "logistic regression",
            "cox regression"
        ]

        sample_size_methods = [
            "two-proportion superiority",
            "log-rank test"
        ]

        recommendation = (
            "Binary and survival endpoint strategies are both commonly used."
        )

    return DesignPatternResponse(
        research_question=req.research_question,
        common_designs=designs,
        common_endpoints=endpoints,
        common_followup=followup,
        common_analysis_methods=analyses,
        common_sample_size_methods=sample_size_methods,
        recommendation=recommendation
    )

@app.post(
    "/orchestrator/endpoint-intelligence",
    response_model=EndpointIntelligenceResponse
)
def endpoint_intelligence(
    req: TrialLandscapeRequest
):

    text = req.research_question.lower()

    endpoints = []

    endpoint_frequency = {}

    control_rate_range = None

    event_rate_range = None

    effect_size_range = None

    recommendation = None

    if (
        "functional cure" in text
        or "hbsag loss" in text
    ):

        endpoints = [
            "HBsAg loss",
            "Time to HBsAg loss"
        ]

        endpoint_frequency = {
            "HBsAg loss": 80,
            "Time to HBsAg loss": 20
        }

        control_rate_range = "4%-13%"

        effect_size_range = "5%-10%"

        recommendation = (
            "HBsAg loss remains the most commonly used endpoint."
        )

    return EndpointIntelligenceResponse(
        research_question=req.research_question,
        common_endpoints=endpoints,
        endpoint_frequency=endpoint_frequency,
        control_rate_range=control_rate_range,
        effect_size_range=effect_size_range,
        recommendation=recommendation
    )

@app.post(
    "/orchestrator/interim-analysis",
    response_model=InterimAnalysisResponse
)
def interim_analysis(
    req: InterimAnalysisRequest
):

    interim_analysis_recommended = False

    dsmb_recommended = False

    recommended_interims = 0

    stopping_boundary = None

    # -------------------------
    # Interim Analysis Logic
    # -------------------------

    if (
        req.sample_size >= 300
        or req.endpoint_type.lower() == "survival"
        or req.follow_up_years >= 2
    ):

        interim_analysis_recommended = True

        recommended_interims = 1

        stopping_boundary = "O'Brien-Fleming"

    # -------------------------
    # DSMB Recommendation
    # -------------------------

    if (
        req.endpoint_type.lower() == "survival"
        or req.sample_size >= 500
    ):

        dsmb_recommended = True

    # -------------------------
    # Additional Rules
    # -------------------------

    if (
        req.sample_size >= 1000
    ):

        recommended_interims = 2

    # -------------------------
    # Rationale
    # -------------------------

    rationale = (
        "Large sample size, survival endpoints, "
        "or prolonged follow-up may justify "
        "interim monitoring and DSMB oversight."
    )

    return InterimAnalysisResponse(

        interim_analysis_recommended=
            interim_analysis_recommended,

        dsmb_recommended=
            dsmb_recommended,

        recommended_interims=
            recommended_interims,

        stopping_boundary=
            stopping_boundary,

        rationale=
            rationale
    )

@app.post(
    "/orchestrator/interim-analysis-v2",
    response_model=InterimAnalysisV2Response
)
def interim_analysis_v2(
    req: InterimAnalysisV2Request
):

    return InterimAnalysisV2Response(

        information_fraction=
            "50%",

        stopping_boundary=
            "O'Brien-Fleming",

        futility_analysis=
            True,

        dsmb_required=
            (
                req.sample_size >= 300
                or
                req.endpoint_type.lower() == "survival"
            ),

        recommendation=
            "One interim analysis at 50% information fraction is recommended."
    )

# =========================
# Interim Analysis V3
# =========================

@app.post(
    "/orchestrator/interim-analysis-v3",
    response_model=InterimAnalysisV3Response
)
def interim_analysis_v3(
    req: InterimAnalysisV3Request
):

    alpha_spending_strategy = (
        "O'Brien-Fleming"
    )

    if req.sample_size >= 1000:

        alpha_spending_strategy = (
            "Lan-DeMets"
        )

    event_trigger = (
        "50% information fraction"
    )

    if req.event_driven:

        event_trigger = (
            "100 events"
        )

    futility_rule = (
        "Review conditional efficacy trend at interim analysis."
    )

    early_success_rule = (
        "Early stopping permitted if efficacy boundary crossed."
    )

    dsmb_required = (
        req.sample_size >= 300
        or
        req.endpoint_type.lower() == "survival"
    )

    dsmb_meeting_frequency = (
        "Every 6 months"
    )

    recommendation = (
        "Interim monitoring strategy should be prespecified in the protocol and SAP."
    )

    return InterimAnalysisV3Response(

        information_fraction=
            "50%",

        alpha_spending_strategy=
            alpha_spending_strategy,

        event_trigger=
            event_trigger,

        futility_rule=
            futility_rule,

        early_success_rule=
            early_success_rule,

        dsmb_required=
            dsmb_required,

        dsmb_meeting_frequency=
            dsmb_meeting_frequency,

        recommendation=
            recommendation
    )

@app.post(
    "/orchestrator/clinicaltrialsgov-package",
    response_model=ClinicalTrialsGovResponse
)
def clinicaltrialsgov_package(
    req: ClinicalTrialsGovRequest
):

    brief_title = req.study_title

    official_title = (
        f"A {req.study_design} evaluating "
        f"{req.intervention} in "
        f"{req.disease}"
    )

    brief_summary = (
        f"This study evaluates "
        f"{req.intervention} "
        f"in participants with "
        f"{req.disease}."
    )

    detailed_description = (
        f"The purpose of this study is to evaluate "
        f"the efficacy and safety of "
        f"{req.intervention} "
        f"in participants with "
        f"{req.disease}. "
        f"The primary endpoint is "
        f"{req.primary_endpoint}."
    )

    primary_outcome_measure = (
        req.primary_endpoint
    )

    eligibility_criteria = (
        f"Adults with "
        f"{req.disease} "
        f"meeting study eligibility criteria."
    )

    return ClinicalTrialsGovResponse(

        brief_title=
            brief_title,

        official_title=
            official_title,

        brief_summary=
            brief_summary,

        detailed_description=
            detailed_description,

        primary_outcome_measure=
            primary_outcome_measure,

        eligibility_criteria=
            eligibility_criteria
    )

# =========================
# ClinicalTrials.gov Package V2
# =========================

@app.post(
    "/orchestrator/clinicaltrialsgov-package-v2",
    response_model=ClinicalTrialsGovV2Response
)
def clinicaltrialsgov_package_v2(
    req: ClinicalTrialsGovV2Request
):

    spec = req.trial_specification

    disease = (
        spec.disease
        if spec.disease
        else "Target Disease"
    )

    intervention = (
        spec.intervention
        if spec.intervention
        else "Study Intervention"
    )

    endpoint = (
        spec.primary_endpoint
        if spec.primary_endpoint
        else "Primary Endpoint"
    )

    design = (
        spec.study_design
        if spec.study_design
        else "Clinical Trial"
    )

    brief_title = (
        f"{intervention} in {disease}"
    )

    official_title = (
        f"A {design} Evaluating "
        f"{intervention} "
        f"in Participants With "
        f"{disease}"
    )

    brief_summary = (
        f"This study evaluates "
        f"{intervention} "
        f"in participants with "
        f"{disease}. "
        f"The primary endpoint is "
        f"{endpoint}."
    )

    detailed_description = (
        f"The purpose of this study is to "
        f"evaluate the efficacy and safety of "
        f"{intervention} "
        f"in participants with "
        f"{disease}. "
        f"The primary endpoint is "
        f"{endpoint}. "
        f"The study design is "
        f"{design}."
    )

    eligibility_criteria = (
        f"Participants with "
        f"{disease} "
        f"meeting protocol eligibility criteria."
    )

    return ClinicalTrialsGovV2Response(

        brief_title=
            brief_title,

        official_title=
            official_title,

        brief_summary=
            brief_summary,

        detailed_description=
            detailed_description,

        primary_outcome_measure=
            endpoint,

        eligibility_criteria=
            eligibility_criteria
    )

@app.post(
    "/orchestrator/crf-builder",
    response_model=CRFBuilderResponse
)
def crf_builder(
    req: CRFBuilderRequest
):

    screening_fields = [

        "Informed Consent",

        "Eligibility Assessment",

        "Medical History"
    ]

    baseline_fields = [

        "Age",

        "Sex",

        "Disease Duration",

        "Baseline Laboratory Values"
    ]

    followup_fields = [

        "Visit Date",

        "Medication Adherence",

        "Laboratory Assessments"
    ]

    safety_fields = [

        "Adverse Events",

        "Serious Adverse Events",

        "Treatment Discontinuation"
    ]

    endpoint_fields = [

        req.primary_endpoint
    ]

    return CRFBuilderResponse(

        screening_fields=
            screening_fields,

        baseline_fields=
            baseline_fields,

        followup_fields=
            followup_fields,

        safety_fields=
            safety_fields,

        endpoint_fields=
            endpoint_fields
    )

@app.post(
    "/orchestrator/redcap-builder-v2",
    response_model=REDCapBuilderResponse
)
def redcap_builder_v2(
    req: REDCapBuilderRequest
):

    variables = [

        {
            "field_name":
                "subject_id",

            "field_type":
                "text"
        },

        {
            "field_name":
                "visit_date",

            "field_type":
                "date"
        },

        {
            "field_name":
                "adverse_event",

            "field_type":
                "yesno"
        },

        {
            "field_name":
                "primary_endpoint",

            "field_type":
                "text"
        }
    ]

    return REDCapBuilderResponse(

        form_name=
            f"{req.disease} Study CRF",

        variable_definitions=
            variables
    )

# =========================
# REDCap Builder V3
# =========================

@app.post(
    "/orchestrator/redcap-builder-v3",
    response_model=REDCapBuilderV3Response
)
def redcap_builder_v3(
    req: REDCapBuilderV3Request
):

    visit_schedule = [

        "Screening",

        "Baseline",

        "Week 4",

        "Week 12",

        "Week 24",

        "Week 48",

        "Week 96"
    ]

    forms = [

        {
            "form_name":
                "Screening"
        },

        {
            "form_name":
                "Baseline"
        },

        {
            "form_name":
                "Follow-up"
        },

        {
            "form_name":
                "Safety"
        },

        {
            "form_name":
                "Endpoint"
        }
    ]

    variable_metadata = [

        {
            "visit":
                "Baseline",

            "form_name":
                "Baseline",

            "field_name":
                "age",

            "field_label":
                "Age at Enrollment",

            "field_type":
                "number",

            "required":
                True,

            "validation":
                "integer",

            "choices":
                ""
        },

        {
            "visit":
                "Baseline",

            "form_name":
                "Baseline",

            "field_name":
                "sex",

            "field_label":
                "Sex",

            "field_type":
                "radio",

            "required":
                True,

            "validation":
                "",

            "choices":
                "1,Male | 2,Female"
        },

        {
            "visit":
                "Week 96",

            "form_name":
                "Endpoint",

            "field_name":
                "primary_endpoint",

            "field_label":
                req.primary_endpoint,

            "field_type":
                "text",

            "required":
                True,

            "validation":
                "",

            "choices":
                ""
        }
    ]

    return REDCapBuilderV3Response(

        visit_schedule=
            visit_schedule,

        forms=
            forms,

        variable_metadata=
            variable_metadata
    )

@app.post(
    "/orchestrator/brochure-generator",
    response_model=BrochureResponse
)
def brochure_generator(
    req: BrochureRequest
):

    scientific_rationale = (

        f"{req.intervention} "

        f"may improve outcomes in "

        f"{req.disease}. "

        f"{req.study_rationale}"
    )

    unmet_need = (

        f"Current treatment strategies "

        f"for {req.disease} remain "

        f"suboptimal."
    )

    expected_impact = (

        f"The study may provide evidence "

        f"supporting future clinical "

        f"management of {req.disease}."
    )

    return BrochureResponse(

        scientific_rationale=
            scientific_rationale,

        unmet_need=
            unmet_need,

        expected_impact=
            expected_impact
    )

@app.post(
    "/orchestrator/advanced-sap",
    response_model=AdvancedSAPResponse
)
def advanced_sap(
    req: AdvancedSAPRequest
):

    endpoint_type = req.endpoint_type.lower()

    analysis_population = (
        "Intention-to-Treat"
    )

    multiplicity_strategy = (
        "Hierarchical Testing"
    )

    covariate_adjustment = [
        "Age",
        "Sex",
        "Baseline Disease Severity"
    ]

    subgroup_analysis = [
        "Age Group",
        "Sex",
        "Disease Severity"
    ]

    missing_data_strategy = (
        "Multiple Imputation"
    )

    sensitivity_analysis = [
        "Per Protocol Analysis",
        "Worst Case Analysis"
    ]

    if endpoint_type == "binary":

        primary_analysis = (
            "Logistic Regression"
        )

    elif endpoint_type == "continuous":

        primary_analysis = (
            "ANCOVA"
        )

    elif endpoint_type == "survival":

        primary_analysis = (
            "Cox Proportional Hazards Model"
        )

    else:

        primary_analysis = (
            "Manual Review"
        )

    return AdvancedSAPResponse(

        analysis_population=
            analysis_population,

        primary_analysis=
            primary_analysis,

        multiplicity_strategy=
            multiplicity_strategy,

        covariate_adjustment=
            covariate_adjustment,

        subgroup_analysis=
            subgroup_analysis,

        missing_data_strategy=
            missing_data_strategy,

        sensitivity_analysis=
            sensitivity_analysis
    )

@app.post(
    "/orchestrator/tte-design",
    response_model=TTEResponse
)
def tte_design(
    req: TTERequest
):

    text = req.research_question.lower()

    eligibility_criteria = (
        "Patients meeting study eligibility criteria."
    )

    time_zero = (
        "Date of treatment strategy assignment."
    )

    treatment_strategy = (
        "Treatment versus comparator strategy."
    )

    follow_up = (
        "Follow participants until endpoint occurrence or censoring."
    )

    causal_contrast = (
        "Treatment effect under target trial framework."
    )

    recommended_method = (
        "Inverse Probability of Treatment Weighting (IPTW)"
    )

    if (
        "survival" in text
        or "time to event" in text
    ):

        recommended_method = (
            "Marginal Structural Model (MSM)"
        )

    return TTEResponse(

        eligibility_criteria=
            eligibility_criteria,

        time_zero=
            time_zero,

        treatment_strategy=
            treatment_strategy,

        follow_up=
            follow_up,

        causal_contrast=
            causal_contrast,

        recommended_method=
            recommended_method
    )

@app.post(
    "/orchestrator/tte-design-v2",
    response_model=TTEV2Response
)
def tte_design_v2(
    req: TTEV2Request
):

    return TTEV2Response(

        eligibility_criteria=
            "Patients meeting target trial eligibility criteria.",

        time_zero=
            "Date of treatment strategy assignment.",

        treatment_strategy=
            "Treatment versus comparator.",

        follow_up=
            "Until endpoint occurrence or censoring.",

        causal_contrast=
            "Average treatment effect.",

        recommended_method=
            "IPTW",

        sensitivity_analysis=
            "Marginal Structural Model"
    )

# =========================
# TTE V3
# =========================

@app.post(
    "/orchestrator/tte-design-v3",
    response_model=TTEV3Response
)
def tte_design_v3(
    req: TTEV3Request
):

    bias_report = [

        "Immortal Time Bias Risk: Review time-zero definition.",

        "Residual Confounding Risk: Evaluate measured and unmeasured confounders.",

        "Selection Bias Risk: Assess inclusion criteria.",

        "Measurement Bias Risk: Verify outcome ascertainment."
    ]

    return TTEV3Response(

        eligibility_criteria=
            "Patients meeting target trial eligibility criteria.",

        time_zero=
            "Date of treatment strategy assignment.",

        treatment_strategy=
            "Treatment versus comparator.",

        follow_up=
            "Until endpoint occurrence or censoring.",

        causal_contrast=
            "Average treatment effect.",

        recommended_method=
            "IPTW with Marginal Structural Model",

        cloning_censoring_weighting=
            True,

        positivity_diagnostics=
            "Propensity score overlap assessment recommended.",

        weight_diagnostics=
            "Evaluate extreme weights and stabilized weights.",

        sequential_exchangeability=
            "Assess exchangeability assumptions at each decision point.",

        target_trial_bias_report=
            bias_report
    )