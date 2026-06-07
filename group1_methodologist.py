"""
group1_methodologist.py
========================
Layer 1 — Clinical Trial Methodologist OS

Endpoints for design reasoning, sample-size calculation, statistical
design strategy, and interim-analysis planning.
"""

from math import log

from fastapi import APIRouter
from scipy.stats import norm
from statsmodels.stats.power import TTestIndPower, NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

from shared_models import (
    DesignRecommendRequest,
    DesignRecommendV2Request,
    TTestRequest,
    ProportionRequest,
    NonInferiorityBinaryRequest,
    NonInferiorityContinuousRequest,
    SurvivalRequest,
    SurvivalNonInferiorityRequest,
    DesignDiscussionRequest,
    DesignDiscussionResponse,
    DesignTradeoffRequest,
    DesignTradeoffResponse,
    DesignSelectionRequest,
    DesignSelectionResponse,
    DesignArchitectureRequest,
    DesignArchitectureResponse,
    AdvancedStatisticalDesignRequest,
    AdvancedStatisticalDesignResponse,
    AssumptionAnalysisRequest,
    AssumptionAnalysisResponse,
    BiasAnalysisRequest,
    BiasAnalysisResponse,
    MethodologistCritiqueRequest,
    MethodologistCritiqueResponse,
    StatisticalConsequenceRequest,
    StatisticalConsequenceResponse,
    InterimAnalysisRequest,
    InterimAnalysisResponse,
    InterimAnalysisV2Request,
    InterimAnalysisV2Response,
    InterimAnalysisV3Request,
    InterimAnalysisV3Response,
)

router = APIRouter()


# =========================
# Design Recommendation
# =========================

@router.post("/design/recommend", tags=["Methodologist"])
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
        "success rate",
    ]

    survival_keywords = [
        "overall survival",
        "os",
        "pfs",
        "dfs",
        "time to event",
        "survival",
    ]

    continuous_keywords = [
        "hba1c",
        "blood pressure",
        "ldl",
        "bmi",
        "weight",
        "quality of life",
        "score",
    ]

    for keyword in binary_keywords:
        if keyword in text:
            return {
                "endpoint_type": "binary",
                "recommended_method": "two-proportion superiority",
                "sample_size_api": "/sample-size/proportion",
                "reasoning": "Primary endpoint appears to be a proportion.",
            }

    for keyword in survival_keywords:
        if keyword in text:
            return {
                "endpoint_type": "survival",
                "recommended_method": "log-rank test",
                "sample_size_api": "/sample-size/survival",
                "reasoning": "Primary endpoint appears to be time-to-event.",
            }

    for keyword in continuous_keywords:
        if keyword in text:
            return {
                "endpoint_type": "continuous",
                "recommended_method": "two-sample t-test",
                "sample_size_api": "/sample-size/ttest",
                "reasoning": "Primary endpoint appears to be continuous.",
            }

    return {
        "endpoint_type": "unknown",
        "recommended_method": "manual_review",
        "reasoning": "Unable to automatically classify endpoint.",
    }


@router.post("/design/recommend-v2", tags=["Methodologist"])
def recommend_design_v2(req: DesignRecommendV2Request):

    text = req.study_description.lower()

    design = "unknown"
    endpoint_type = "unknown"
    sample_size_method = "manual_review"
    analysis_method = "manual_review"
    estimand = "treatment_policy"

    # randomized trial
    if "randomized" in text or "randomised" in text or "rct" in text:
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
        sample_size_method = "two-proportion superiority"
        analysis_method = "logistic regression"

    # continuous endpoint
    elif (
        "hba1c" in text
        or "blood pressure" in text
        or "ldl" in text
        or "weight" in text
    ):
        endpoint_type = "continuous"
        sample_size_method = "two-sample t-test"
        analysis_method = "ancova"

    # survival endpoint
    elif (
        "overall survival" in text
        or "progression-free survival" in text
        or "disease-free survival" in text
        or "time to event" in text
    ):
        endpoint_type = "survival"
        sample_size_method = "log-rank test"
        analysis_method = "cox proportional hazards"

    return {
        "design": design,
        "endpoint_type": endpoint_type,
        "sample_size_method": sample_size_method,
        "analysis_method": analysis_method,
        "estimand": estimand,
    }


# =========================
# T-Test Sample Size
# =========================

@router.post("/sample-size/ttest", tags=["Statistics"])
def calculate_ttest(req: TTestRequest):

    analysis = TTestIndPower()

    n = analysis.solve_power(
        effect_size=req.effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=req.ratio,
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
        "protocol_justification": justification,
    }


# =========================
# Proportion Sample Size
# =========================

@router.post("/sample-size/proportion", tags=["Statistics"])
def calculate_proportion(req: ProportionRequest):

    effect_size = proportion_effectsize(req.p1, req.p2)

    analysis = NormalIndPower()

    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=1,
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
        "protocol_justification": justification,
    }


@router.post("/sample-size/noninferiority/binary", tags=["Statistics"])
def calculate_noninferiority_binary(req: NonInferiorityBinaryRequest):

    effect_size = proportion_effectsize(
        req.control_rate,
        req.control_rate - req.margin,
    )

    analysis = NormalIndPower()

    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=1,
    )

    total_n = n * 2

    adjusted_total_n = total_n / (1 - req.dropout_rate)

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
        "adjusted_total_sample_size": round(adjusted_total_n),
        "protocol_justification": justification,
    }


@router.post("/sample-size/noninferiority/continuous")
def calculate_noninferiority_continuous(req: NonInferiorityContinuousRequest):

    effect_size = req.margin / req.sd

    analysis = TTestIndPower()

    n = analysis.solve_power(
        effect_size=effect_size,
        alpha=req.alpha,
        power=req.power,
        ratio=1,
    )

    total_n = n * 2

    adjusted_total_n = total_n / (1 - req.dropout_rate)

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
        "adjusted_total_sample_size": round(adjusted_total_n),
        "protocol_justification": justification,
    }


@router.post("/sample-size/survival", tags=["Statistics"])
def calculate_survival(req: SurvivalRequest):

    z_alpha = norm.ppf(1 - req.alpha / 2)
    z_beta = norm.ppf(req.power)

    required_events = ((z_alpha + z_beta) ** 2) / (log(req.hazard_ratio) ** 2)

    adjusted_events = required_events / (1 - req.dropout_rate)

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
        "required_events": round(required_events, 2),
        "adjusted_required_events": round(adjusted_events, 2),
        "protocol_justification": justification,
    }


@router.post("/sample-size/noninferiority/survival")
def calculate_survival_noninferiority(req: SurvivalNonInferiorityRequest):

    z_alpha = norm.ppf(1 - req.alpha)
    z_beta = norm.ppf(req.power)

    required_events = ((z_alpha + z_beta) ** 2) / (
        log(req.hazard_ratio_margin) ** 2
    )

    adjusted_events = required_events / (1 - req.dropout_rate)

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
        "hazard_ratio_margin": req.hazard_ratio_margin,
        "alpha": req.alpha,
        "power": req.power,
        "dropout_rate": req.dropout_rate,
        "required_events": round(required_events, 2),
        "adjusted_required_events": round(adjusted_events, 2),
        "protocol_justification": justification,
    }


# =========================
# Design Discussion
# =========================

@router.post(
    "/orchestrator/design-discussion",
    response_model=DesignDiscussionResponse,
    tags=["Methodologist"],
)
def design_discussion(req: DesignDiscussionRequest):

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

        similar_trials = ["FINITE", "Nuc-STOP", "HBV-STOP"]

        endpoint_options = [
            {
                "endpoint": "HBsAg loss at Week 96",
                "endpoint_type": "binary",
                "sample_size_method": "two-proportion superiority",
            },
            {
                "endpoint": "Time to HBsAg loss",
                "endpoint_type": "survival",
                "sample_size_method": "log-rank test",
            },
        ]

        common_endpoint_types = ["binary", "survival"]

        common_sample_size_methods = [
            "two-proportion superiority",
            "log-rank test",
        ]

        recommendation = "Time to HBsAg loss"

    return DesignDiscussionResponse(
        research_question=req.research_question,
        similar_trials=similar_trials,
        endpoint_options=endpoint_options,
        common_endpoint_types=common_endpoint_types,
        common_sample_size_methods=common_sample_size_methods,
        recommendation=recommendation,
    )


# =========================
# Design Tradeoff
# =========================

@router.post(
    "/orchestrator/design-tradeoff",
    response_model=DesignTradeoffResponse,
    tags=["Methodologist"],
)
def design_tradeoff(req: DesignTradeoffRequest):

    text = req.research_question.lower()

    options = []
    recommendation = None

    # Relapse example
    if "relapse" in text or "recurrence" in text:

        options = [
            {
                "endpoint": "Relapse by Month 6",
                "endpoint_type": "binary",
                "advantages": [
                    "Simple interpretation",
                    "Easy sample size calculation",
                    "Common clinical trial design",
                ],
                "disadvantages": [
                    "Ignores timing information",
                    "Day 7 and Day 180 relapse are treated equally",
                ],
                "statistical_efficiency": "moderate",
                "operational_feasibility": "high",
                "sample_size_impact": "often larger sample size",
            },
            {
                "endpoint": "Time to relapse",
                "endpoint_type": "survival",
                "advantages": [
                    "Uses timing information",
                    "More efficient use of events",
                    "Clinically informative",
                ],
                "disadvantages": [
                    "More complex assumptions",
                    "Requires survival analysis expertise",
                ],
                "statistical_efficiency": "high",
                "operational_feasibility": "moderate",
                "sample_size_impact": "often lower event requirement",
            },
        ]

        recommendation = (
            "If the key question is whether relapse occurs, "
            "use a binary endpoint. "
            "If timing of relapse is clinically important, "
            "use a survival endpoint."
        )

    return DesignTradeoffResponse(
        research_question=req.research_question,
        options=options,
        recommendation=recommendation,
    )


# =========================
# Design Selection
# =========================

@router.post(
    "/orchestrator/design-selection",
    response_model=DesignSelectionResponse,
    tags=["Methodologist"],
)
def design_selection(req: DesignSelectionRequest):

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
                "design": "Single Arm",
                "advantages": ["Fast", "Lower cost"],
                "disadvantages": [
                    "No concurrent control group",
                    "Weak causal inference",
                ],
                "budget_impact": "low",
                "publication_value": "moderate",
            },
            {
                "design": "Randomized Controlled Trial",
                "advantages": [
                    "Strong causal inference",
                    "Regulatory familiarity",
                ],
                "disadvantages": ["Higher cost", "Longer recruitment"],
                "budget_impact": "high",
                "publication_value": "high",
            },
            {
                "design": "Pragmatic Clinical Trial",
                "advantages": [
                    "Real-world relevance",
                    "Generalizable results",
                ],
                "disadvantages": ["Operational complexity"],
                "budget_impact": "moderate",
                "publication_value": "high",
            },
            {
                "design": "Target Trial Emulation",
                "advantages": ["Uses existing data", "Lower cost"],
                "disadvantages": [
                    "Residual confounding",
                    "Requires observational data",
                ],
                "budget_impact": "low",
                "publication_value": "moderate",
            },
        ]

        recommendation = (
            "Randomized Controlled Trial "
            "remains the preferred design "
            "when causal treatment effect "
            "estimation is the primary goal."
        )

    return DesignSelectionResponse(
        research_question=req.research_question,
        options=options,
        recommendation=recommendation,
    )


# =========================
# Design Architecture Engine
# =========================

@router.post(
    "/orchestrator/design-architecture",
    response_model=DesignArchitectureResponse,
    tags=["Methodologist"],
)
def design_architecture(req: DesignArchitectureRequest):

    options = [
        {
            "architecture": "Parallel-group RCT",
            "why_use": "Strong causal inference",
            "why_not": "Higher cost and longer recruitment",
            "operational_complexity": "moderate",
            "statistical_complexity": "moderate",
            "publication_potential": "high",
        },
        {
            "architecture": "Adaptive Trial",
            "why_use": "Efficient use of resources",
            "why_not": "Requires complex planning",
            "operational_complexity": "high",
            "statistical_complexity": "high",
            "publication_potential": "very high",
        },
        {
            "architecture": "Platform Trial",
            "why_use": "Multiple interventions evaluated simultaneously",
            "why_not": "Substantial infrastructure required",
            "operational_complexity": "very high",
            "statistical_complexity": "very high",
            "publication_potential": "very high",
        },
        {
            "architecture": "Cluster RCT",
            "why_use": "Useful when individual randomization is difficult",
            "why_not": "Requires ICC adjustment",
            "operational_complexity": "high",
            "statistical_complexity": "high",
            "publication_potential": "high",
        },
        {
            "architecture": "Stepped Wedge Trial",
            "why_use": "Facilitates phased implementation",
            "why_not": "Complex analysis",
            "operational_complexity": "high",
            "statistical_complexity": "high",
            "publication_potential": "high",
        },
    ]

    recommendation = (
        "Parallel-group RCT remains the default architecture. "
        "Adaptive and platform designs should be considered when "
        "multiple interventions or efficiency gains are priorities."
    )

    return DesignArchitectureResponse(
        research_question=req.research_question,
        architecture_options=options,
        recommendation=recommendation,
    )


# =========================
# Advanced Statistical Design Engine
# =========================

@router.post(
    "/orchestrator/advanced-statistical-design",
    response_model=AdvancedStatisticalDesignResponse,
    tags=["Methodologist"],
)
def advanced_statistical_design(req: AdvancedStatisticalDesignRequest):

    multiplicity_strategy = "Hierarchical Testing"
    alpha_control_strategy = "Family-wise Error Control"
    adaptive_reestimation = (
        "Consider adaptive sample size re-estimation if recruitment "
        "uncertainty exists."
    )
    competing_risk_strategy = (
        "Fine-Gray model should be considered when competing risks are present."
    )
    multistate_model_recommendation = (
        "Consider multi-state models when disease transitions are clinically "
        "relevant."
    )
    joint_model_recommendation = (
        "Consider joint modeling when longitudinal biomarkers and "
        "time-to-event outcomes coexist."
    )
    bayesian_borrowing = (
        "Historical borrowing may be considered if external evidence is robust."
    )
    external_control_strategy = (
        "External controls may be considered when randomization is infeasible."
    )
    recommendation = (
        "Advanced statistical design considerations should be prespecified in "
        "the SAP and protocol."
    )

    return AdvancedStatisticalDesignResponse(
        multiplicity_strategy=multiplicity_strategy,
        alpha_control_strategy=alpha_control_strategy,
        adaptive_reestimation=adaptive_reestimation,
        competing_risk_strategy=competing_risk_strategy,
        multistate_model_recommendation=multistate_model_recommendation,
        joint_model_recommendation=joint_model_recommendation,
        bayesian_borrowing=bayesian_borrowing,
        external_control_strategy=external_control_strategy,
        recommendation=recommendation,
    )


# =========================
# Assumption Analysis
# =========================

@router.post(
    "/orchestrator/assumption-analysis",
    response_model=AssumptionAnalysisResponse,
)
def assumption_analysis(req: AssumptionAnalysisRequest):

    confidence = "moderate"
    risk = "moderate"

    optimistic = round(req.assumption * 1.5, 4)
    expected = req.assumption
    conservative = round(req.assumption * 0.5, 4)

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
        recommendation=recommendation,
    )


# =========================
# Bias Analysis
# =========================

@router.post(
    "/orchestrator/bias-analysis",
    response_model=BiasAnalysisResponse,
)
def bias_analysis(req: BiasAnalysisRequest):

    biases = []
    design = req.study_design.lower()

    if "single" in design:
        biases.extend(
            [
                {
                    "bias": "selection bias",
                    "severity": "high",
                    "mitigation": "randomized control group",
                },
                {
                    "bias": "historical control bias",
                    "severity": "high",
                    "mitigation": "concurrent control",
                },
            ]
        )
    elif "rct" in design:
        biases.extend(
            [
                {
                    "bias": "attrition bias",
                    "severity": "moderate",
                    "mitigation": "retention strategy",
                }
            ]
        )
    elif "tte" in design:
        biases.extend(
            [
                {
                    "bias": "immortal time bias",
                    "severity": "high",
                    "mitigation": "target trial alignment",
                }
            ]
        )

    return BiasAnalysisResponse(
        biases=biases,
        recommendation="Bias mitigation strategies should be documented.",
    )


# =========================
# Methodologist Critique
# =========================

@router.post(
    "/orchestrator/methodologist-critique",
    response_model=MethodologistCritiqueResponse,
)
def methodologist_critique(req: MethodologistCritiqueRequest):

    statistician = []
    irb = []
    dsmb = []
    journal = []

    if req.sample_size:
        if req.sample_size < 50:
            statistician.append("Potentially underpowered study.")

    if req.endpoint_type == "composite":
        journal.append(
            "Composite endpoint may have limited clinical interpretability."
        )

    irb.append("Assess participant burden and visit schedule.")
    dsmb.append("Review safety monitoring requirements.")

    return MethodologistCritiqueResponse(
        statistician_review=statistician,
        irb_review=irb,
        dsmb_review=dsmb,
        journal_review=journal,
    )


# =========================
# Statistical Consequence
# =========================

@router.post(
    "/orchestrator/statistical-consequence",
    response_model=StatisticalConsequenceResponse,
)
def statistical_consequence(req: StatisticalConsequenceRequest):

    comparison = []

    if req.option_a.lower() == "binary" and req.option_b.lower() == "survival":
        comparison = [
            {
                "domain": "sample_size",
                "binary": "often larger",
                "survival": "event-driven",
            },
            {
                "domain": "information",
                "binary": "timing ignored",
                "survival": "timing preserved",
            },
            {
                "domain": "analysis",
                "binary": "logistic regression",
                "survival": "cox model",
            },
        ]

    return StatisticalConsequenceResponse(
        comparison=comparison,
        recommendation=(
            "Use survival endpoints when timing is clinically important."
        ),
    )


# =========================
# Interim Analysis
# =========================

@router.post(
    "/orchestrator/interim-analysis",
    response_model=InterimAnalysisResponse,
    tags=["Statistics"],
)
def interim_analysis(req: InterimAnalysisRequest):

    interim_analysis_recommended = False
    dsmb_recommended = False
    recommended_interims = 0
    stopping_boundary = None

    # Interim Analysis Logic
    if (
        req.sample_size >= 300
        or req.endpoint_type.lower() == "survival"
        or req.follow_up_years >= 2
    ):
        interim_analysis_recommended = True
        recommended_interims = 1
        stopping_boundary = "O'Brien-Fleming"

    # DSMB Recommendation
    if req.endpoint_type.lower() == "survival" or req.sample_size >= 500:
        dsmb_recommended = True

    # Additional Rules
    if req.sample_size >= 1000:
        recommended_interims = 2

    rationale = (
        "Large sample size, survival endpoints, "
        "or prolonged follow-up may justify "
        "interim monitoring and DSMB oversight."
    )

    return InterimAnalysisResponse(
        interim_analysis_recommended=interim_analysis_recommended,
        dsmb_recommended=dsmb_recommended,
        recommended_interims=recommended_interims,
        stopping_boundary=stopping_boundary,
        rationale=rationale,
    )


@router.post(
    "/orchestrator/interim-analysis-v2",
    response_model=InterimAnalysisV2Response,
    tags=["Statistics"],
)
def interim_analysis_v2(req: InterimAnalysisV2Request):

    return InterimAnalysisV2Response(
        information_fraction="50%",
        stopping_boundary="O'Brien-Fleming",
        futility_analysis=True,
        dsmb_required=(
            req.sample_size >= 300
            or req.endpoint_type.lower() == "survival"
        ),
        recommendation=(
            "One interim analysis at 50% information fraction is recommended."
        ),
    )


# =========================
# Interim Analysis V3
# =========================

@router.post(
    "/orchestrator/interim-analysis-v3",
    response_model=InterimAnalysisV3Response,
    tags=["Statistics"],
)
def interim_analysis_v3(req: InterimAnalysisV3Request):

    alpha_spending_strategy = "O'Brien-Fleming"
    if req.sample_size >= 1000:
        alpha_spending_strategy = "Lan-DeMets"

    event_trigger = "50% information fraction"
    if req.event_driven:
        event_trigger = "100 events"

    futility_rule = (
        "Review conditional efficacy trend at interim analysis."
    )
    early_success_rule = (
        "Early stopping permitted if efficacy boundary crossed."
    )

    dsmb_required = (
        req.sample_size >= 300
        or req.endpoint_type.lower() == "survival"
    )
    dsmb_meeting_frequency = "Every 6 months"

    recommendation = (
        "Interim monitoring strategy should be prespecified in the protocol "
        "and SAP."
    )

    return InterimAnalysisV3Response(
        information_fraction="50%",
        alpha_spending_strategy=alpha_spending_strategy,
        event_trigger=event_trigger,
        futility_rule=futility_rule,
        early_success_rule=early_success_rule,
        dsmb_required=dsmb_required,
        dsmb_meeting_frequency=dsmb_meeting_frequency,
        recommendation=recommendation,
    )
