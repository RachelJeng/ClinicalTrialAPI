from scipy.stats import norm
from math import log
from fastapi import FastAPI
from pydantic import BaseModel
from statsmodels.stats.power import TTestIndPower, NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

app = FastAPI()


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
    if (
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
    if (
        "overall survival" in text
        or "os" in text
        or "pfs" in text
        or "dfs" in text
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