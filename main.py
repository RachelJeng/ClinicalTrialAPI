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