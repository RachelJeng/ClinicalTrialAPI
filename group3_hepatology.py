"""
group3_hepatology.py
====================
Layer 3 — Hepatology Research OS (Foundation + Trial Planning + core disease
intelligence)

Includes evidence/landscape foundation endpoints, feasibility/budget trial
planning, the study-concept orchestrator, and the core disease-knowledge /
hepatology-intelligence reference engines.

Note: the strategic intelligence engines (intelligence-update,
research-opportunity, precision-hepatology, future-methodology) live in
group4_intelligence.py, per the agreed Strategic Intelligence Layer split.
"""

from fastapi import APIRouter

from shared_models import (
    search_clinicaltrials,
    AnalogousTrialRequest,
    AnalogousTrialResponse,
    EvidenceReviewRequest,
    EvidenceReviewResponse,
    QueryIntelligenceRequest,
    QueryIntelligenceResponse,
    ResearchQuestionRequest,
    ResearchQuestionResponse,
    TrialLandscapeRequest,
    TrialLandscapeResponse,
    UnmetNeedResponse,
    DesignPatternResponse,
    EndpointIntelligenceResponse,
    FeasibilityRequest,
    FeasibilityResponse,
    FeasibilityOptimizationRequest,
    FeasibilityOptimizationResponse,
    BudgetRequest,
    BudgetResponse,
    StudyConceptRequest,
    TrialSpecification,
    DiseaseKnowledgeRequest,
    DiseaseKnowledgeResponse,
    HepatologyIntelligenceRequest,
    HepatologyIntelligenceResponse,
)

router = APIRouter()


# =========================
# Analogous Trials
# =========================

@router.post(
    "/orchestrator/analogous-trials",
    response_model=AnalogousTrialResponse,
    tags=["Foundation"],
)
def analogous_trials(req: AnalogousTrialRequest):

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
        similar_trials = ["FINITE", "Nuc-STOP", "HBV-STOP"]
        common_endpoint_types = ["binary", "survival"]
        common_sample_size_methods = [
            "two-proportion superiority",
            "log-rank test",
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
        similar_trials = ["STEP", "SURPASS"]
        common_endpoint_types = ["continuous"]
        common_sample_size_methods = ["two-sample t-test", "ANCOVA"]
        recommendation = (
            "Continuous endpoints are commonly "
            "used in metabolic disease studies."
        )

    return AnalogousTrialResponse(
        research_question=req.research_question,
        similar_trials=similar_trials,
        common_endpoint_types=common_endpoint_types,
        common_sample_size_methods=common_sample_size_methods,
        recommendation=recommendation,
    )


# =========================
# Evidence Review
# =========================

@router.post(
    "/orchestrator/evidence-review",
    response_model=EvidenceReviewResponse,
    tags=["Foundation"],
)
def evidence_review(req: EvidenceReviewRequest):

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
            "Published Protocols",
        ]

        query = "hepatitis b"
        if "functional cure" in text:
            query = "hbsag loss hepatitis b"

        similar_trials = search_clinicaltrials(query)

        similar_publications = [
            "FINITE publication",
            "HBV-STOP publication",
        ]

        similar_protocols = ["FINITE protocol"]

        common_endpoints = [
            "HBsAg loss at fixed timepoint",
            "Time to HBsAg loss",
        ]

        common_analysis_methods = [
            "Logistic regression",
            "Cox proportional hazards",
        ]

        common_sample_size_methods = [
            "Two-proportion superiority",
            "Log-rank test",
        ]

        design_patterns = [
            "Fixed follow-up endpoint assessment",
            "Off-treatment observation period",
            "Functional cure endpoint strategy",
        ]

        strengths = [
            "Clinically meaningful endpoint",
            "Simple interpretation",
            "Commonly used in HBV studies",
        ]

        limitations = [
            "Functional cure events are rare",
            "Long follow-up required",
            "Endpoint timing may be ignored",
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
        research_question=req.research_question,
        evidence_sources=evidence_sources,
        similar_trials=similar_trials,
        similar_publications=similar_publications,
        similar_protocols=similar_protocols,
        common_endpoints=common_endpoints,
        common_analysis_methods=common_analysis_methods,
        common_sample_size_methods=common_sample_size_methods,
        design_patterns=design_patterns,
        strengths=strengths,
        limitations=limitations,
        evidence_summary=evidence_summary,
        recommendation=recommendation,
    )


# =========================
# Query Intelligence
# =========================

@router.post(
    "/orchestrator/query-intelligence",
    response_model=QueryIntelligenceResponse,
    tags=["Foundation"],
)
def query_intelligence(req: QueryIntelligenceRequest):

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
            "functional cure",
        ]

    return QueryIntelligenceResponse(
        research_question=req.research_question,
        disease=disease,
        intervention=intervention,
        outcome=outcome,
        search_terms=search_terms,
    )


# =========================
# Research Question (composite)
# =========================

@router.post(
    "/orchestrator/research-question",
    response_model=ResearchQuestionResponse,
    tags=["Foundation"],
)
def research_question(req: ResearchQuestionRequest):

    text = req.research_question.lower()

    # Query Intelligence
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
            "functional cure",
        ]

    query_intelligence = {
        "disease": disease,
        "intervention": intervention,
        "outcome": outcome,
        "search_terms": search_terms,
    }

    # Evidence Review
    similar_trials = search_clinicaltrials("hepatitis b")
    evidence_review = {"similar_trials": similar_trials}

    # Design Discussion
    design_discussion = {
        "recommended_endpoint": "Time to HBsAg loss",
        "endpoint_options": [
            "HBsAg loss at Week 96",
            "Time to HBsAg loss",
        ],
    }

    # Trial Specification
    recommended_trial_specification = {
        "study_design": "parallel-group RCT",
        "endpoint_type": "survival",
        "analysis_method": "cox proportional hazards",
        "sample_size_method": "log-rank test",
    }

    return ResearchQuestionResponse(
        query_intelligence=query_intelligence,
        evidence_review=evidence_review,
        design_discussion=design_discussion,
        recommended_trial_specification=recommended_trial_specification,
    )


# =========================
# Trial Landscape
# =========================

@router.post(
    "/orchestrator/trial-landscape",
    response_model=TrialLandscapeResponse,
    tags=["Foundation"],
)
def trial_landscape(req: TrialLandscapeRequest):

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
        similar_trials = ["FINITE", "HBV-STOP", "Nuc-STOP"]
        completed_trials = similar_trials
        patterns = [
            "off-treatment follow-up",
            "functional cure endpoint",
            "relapse monitoring",
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
        recommendation=recommendation,
    )


# =========================
# Unmet Need
# =========================

@router.post(
    "/orchestrator/unmet-need",
    response_model=UnmetNeedResponse,
    tags=["Foundation"],
)
def unmet_need(req: TrialLandscapeRequest):

    text = req.research_question.lower()

    evidence_gap = None
    clinical_gap = None
    geographic_gap = None
    implementation_gap = None
    recommendation = None

    if "functional cure" in text or "hbsag loss" in text:
        evidence_gap = "Limited randomized evidence exists."
        clinical_gap = "Functional cure remains uncommon."
        geographic_gap = "Asian data remain limited."
        implementation_gap = "Optimal patient selection remains unclear."
        recommendation = "Additional studies remain justified."

    return UnmetNeedResponse(
        research_question=req.research_question,
        evidence_gap=evidence_gap,
        clinical_gap=clinical_gap,
        geographic_gap=geographic_gap,
        implementation_gap=implementation_gap,
        recommendation=recommendation,
    )


# =========================
# Design Patterns
# =========================

@router.post(
    "/orchestrator/design-patterns",
    response_model=DesignPatternResponse,
)
def design_patterns(req: TrialLandscapeRequest):

    text = req.research_question.lower()

    designs = []
    endpoints = []
    followup = []
    analyses = []
    sample_size_methods = []
    recommendation = None

    if "functional cure" in text or "hbsag loss" in text:
        designs = ["single arm", "randomized trial"]
        endpoints = ["HBsAg loss", "Time to HBsAg loss"]
        followup = ["48 weeks", "96 weeks", "144 weeks"]
        analyses = ["logistic regression", "cox regression"]
        sample_size_methods = [
            "two-proportion superiority",
            "log-rank test",
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
        recommendation=recommendation,
    )


# =========================
# Endpoint Intelligence
# =========================

@router.post(
    "/orchestrator/endpoint-intelligence",
    response_model=EndpointIntelligenceResponse,
)
def endpoint_intelligence(req: TrialLandscapeRequest):

    text = req.research_question.lower()

    endpoints = []
    endpoint_frequency = {}
    control_rate_range = None
    event_rate_range = None
    effect_size_range = None
    recommendation = None

    if "functional cure" in text or "hbsag loss" in text:
        endpoints = ["HBsAg loss", "Time to HBsAg loss"]
        endpoint_frequency = {
            "HBsAg loss": 80,
            "Time to HBsAg loss": 20,
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
        event_rate_range=event_rate_range,
        effect_size_range=effect_size_range,
        recommendation=recommendation,
    )


# =========================
# Feasibility Analysis
# =========================

@router.post(
    "/orchestrator/feasibility-analysis",
    response_model=FeasibilityResponse,
    tags=["Trial Planning"],
)
def feasibility_analysis(req: FeasibilityRequest):

    estimated_recruitment_rate = (
        req.annual_eligible_patients
        * req.consent_rate
        * req.number_of_sites
    )

    if estimated_recruitment_rate == 0:
        estimated_accrual_years = 999
    else:
        estimated_accrual_years = (
            req.sample_size / estimated_recruitment_rate
        )

    if estimated_accrual_years <= 2:
        feasibility_rating = "excellent"
        recommendation = "Recruitment appears highly feasible."
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
        estimated_recruitment_rate=estimated_recruitment_rate,
        estimated_accrual_years=round(estimated_accrual_years, 2),
        feasibility_rating=feasibility_rating,
        recommendation=recommendation,
    )


# =========================
# Feasibility Optimization
# =========================

@router.post(
    "/orchestrator/feasibility-optimization",
    response_model=FeasibilityOptimizationResponse,
    tags=["Trial Planning"],
)
def feasibility_optimization(req: FeasibilityOptimizationRequest):

    recruitment_rate = (
        req.annual_eligible_patients
        * req.consent_rate
        * req.number_of_sites
    )

    if recruitment_rate == 0:
        current_accrual_years = 999
    else:
        current_accrual_years = req.sample_size / recruitment_rate

    optimization_options = []

    # Increase sites
    optimization_options.append(
        {
            "strategy": "Increase to 5 sites",
            "estimated_accrual_years": round(current_accrual_years / 5, 2),
        }
    )

    optimization_options.append(
        {
            "strategy": "Increase to 10 sites",
            "estimated_accrual_years": round(current_accrual_years / 10, 2),
        }
    )

    # Improve consent
    improved_rate = (
        req.annual_eligible_patients * 0.8 * req.number_of_sites
    )

    optimization_options.append(
        {
            "strategy": "Improve consent rate to 80%",
            "estimated_accrual_years": round(
                req.sample_size / improved_rate, 2
            ),
        }
    )

    # Reduce sample size
    optimization_options.append(
        {
            "strategy": (
                "Reduce sample size by 30% through alternative endpoint "
                "strategy"
            ),
            "estimated_accrual_years": round(
                (req.sample_size * 0.7) / recruitment_rate, 2
            ),
        }
    )

    return FeasibilityOptimizationResponse(
        current_accrual_years=round(current_accrual_years, 2),
        optimization_options=optimization_options,
    )


# =========================
# Budget Estimation
# =========================

@router.post(
    "/orchestrator/budget-estimation",
    response_model=BudgetResponse,
    tags=["Trial Planning"],
)
def budget_estimation(req: BudgetRequest):

    coordinator_cost = 50000 * req.follow_up_years
    crc_cost = req.sample_size * 200
    lab_cost = req.sample_size * 500
    monitoring_cost = req.number_of_sites * 10000
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
        coordinator_cost=coordinator_cost,
        crc_cost=crc_cost,
        lab_cost=lab_cost,
        monitoring_cost=monitoring_cost,
        statistics_cost=statistics_cost,
        publication_cost=publication_cost,
        estimated_total_budget=estimated_total_budget,
    )


# =========================
# Study Concept Orchestrator
# =========================

@router.post(
    "/orchestrator/study-concept",
    response_model=TrialSpecification,
    tags=["Trial Planning"],
)
def orchestrate_study_concept(req: StudyConceptRequest):

    text = req.study_description.lower()
    print(text)

    # TrialSpecification fields
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

    # Study Design
    if "randomized" in text or "randomised" in text or "rct" in text:
        study_design = "parallel-group RCT"

    # Disease
    if "masld" in text:
        disease = "MASLD"
        population = "MASLD patients"

    # Intervention
    if "semaglutide" in text:
        intervention = "semaglutide"

    # Comparator
    if "standard care" in text:
        comparator = "standard care"
    if "placebo" in text:
        comparator = "placebo"

    # Endpoint
    if "fibrosis improvement" in text:
        primary_endpoint = "fibrosis improvement at week 48"
        endpoint_type = "binary"
        analysis_method = "logistic regression"
        sample_size_method = "two-proportion superiority"
        recommended_sample_size_api = "/sample-size/proportion"
        recommended_protocol_api = "/protocol/endpoints"
        recommended_sap_api = "/sap/statistical-analysis-plan"
        recommended_estimand_api = "/protocol/estimand"
        similar_trials = ["FINITE", "Nuc-STOP", "HBV-STOP"]
        endpoint_strategy_summary = (
            "Binary endpoint strategy commonly used "
            "for functional cure studies."
        )
        recommended_endpoint_type = "binary"
        required_sample_size_inputs = ["p1", "p2", "alpha", "power"]

    elif "hba1c" in text:
        primary_endpoint = "change in HbA1c"
        endpoint_type = "continuous"
        analysis_method = "ANCOVA"
        sample_size_method = "two-sample t-test"
        recommended_sample_size_api = "/sample-size/ttest"
        recommended_protocol_api = "/protocol/endpoints"
        recommended_sap_api = "/sap/statistical-analysis-plan"
        recommended_estimand_api = "/protocol/estimand"
        endpoint_strategy_summary = (
            "Continuous endpoint strategy commonly "
            "used for metabolic outcome studies."
        )
        recommended_endpoint_type = "continuous"
        required_sample_size_inputs = ["effect_size", "alpha", "power"]

    elif (
        "overall survival" in text
        or "progression-free survival" in text
    ):
        primary_endpoint = "time-to-event endpoint"
        endpoint_type = "survival"
        analysis_method = "cox proportional hazards"
        sample_size_method = "log-rank test"
        recommended_sample_size_api = "/sample-size/survival"
        recommended_protocol_api = "/protocol/endpoints"
        recommended_sap_api = "/sap/statistical-analysis-plan"
        recommended_estimand_api = "/protocol/estimand"
        endpoint_strategy_summary = (
            "Time-to-event endpoint strategy "
            "recommended when timing is clinically important."
        )
        recommended_endpoint_type = "survival"
        required_sample_size_inputs = ["hazard_ratio", "alpha", "power"]

    print(
        "DEBUG:",
        disease,
        population,
        intervention,
        comparator,
        primary_endpoint,
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
        required_sample_size_inputs=required_sample_size_inputs,
    )


# =========================
# Disease Knowledge Engine
# =========================

@router.post(
    "/orchestrator/disease-knowledge",
    response_model=DiseaseKnowledgeResponse,
    tags=["Disease Intelligence"],
)
def disease_knowledge(req: DiseaseKnowledgeRequest):

    disease = req.disease.lower()

    if disease == "hbv":
        return DiseaseKnowledgeResponse(
            disease=req.disease,
            common_endpoints=[
                "HBsAg Loss",
                "Functional Cure",
                "Clinical Relapse",
                "Virological Relapse",
            ],
            common_designs=[
                "Single Arm",
                "RCT",
                "Target Trial Emulation",
            ],
            common_analysis_methods=[
                "Logistic Regression",
                "Cox Regression",
                "Competing Risk",
            ],
            common_biases=[
                "Restart-treatment Bias",
                "Informative Censoring",
            ],
            key_trials=["FINITE", "HBV-STOP", "Nuc-STOP"],
            publication_considerations=[
                "Functional cure remains a high-impact endpoint.",
                "Time-to-HBsAg loss may improve publication value.",
            ],
        )

    return DiseaseKnowledgeResponse(
        disease=req.disease,
        common_endpoints=[],
        common_designs=[],
        common_analysis_methods=[],
        common_biases=[],
        key_trials=[],
        publication_considerations=[],
    )


# =========================
# Hepatology Trial Intelligence
# =========================

@router.post(
    "/orchestrator/hepatology-intelligence",
    response_model=HepatologyIntelligenceResponse,
    tags=["Hepatology Research OS"],
)
def hepatology_intelligence(req: HepatologyIntelligenceRequest):

    disease = req.disease.lower()

    if disease == "hbv":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "Functional Cure",
                "Finite Therapy",
                "Relapse Prediction",
                "Biomarker-guided Stopping",
            ],
            preferred_endpoints=[
                "HBsAg Loss",
                "Functional Cure",
                "Time-to-HBsAg Loss",
            ],
            preferred_architectures=[
                "Adaptive Trial",
                "Biomarker-guided Trial",
                "Target Trial Emulation",
            ],
            preferred_statistics=[
                "Competing Risk",
                "Joint Models",
                "Dynamic Treatment Regimes",
            ],
            sample_size_considerations=[
                "Functional cure rate",
                "Relapse rate",
                "Dropout rate",
            ],
            interim_analysis_considerations=[
                "DSMB",
                "Event-driven monitoring",
            ],
            tte_considerations=["IPTW", "MSM", "CCW"],
            emerging_biomarkers=["HBcrAg", "HBV RNA", "qHBsAg"],
            emerging_therapeutics=[
                "siRNA",
                "ASO",
                "CAM",
                "Therapeutic Vaccine",
            ],
            precision_hepatology=[
                "Biomarker-guided stopping",
                "Relapse prediction",
            ],
            reviewer_attack_points=[
                "Restart-treatment bias",
                "Informative censoring",
                "Immortal time bias",
            ],
            publication_opportunities=[
                "Functional cure",
                "Biomarker-guided withdrawal",
            ],
        )

    # MASLD / MASH
    elif disease in ["masld", "mash"]:
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "Fibrosis Improvement",
                "MASH Resolution",
                "Histology-free Endpoints",
            ],
            preferred_endpoints=[
                "Fibrosis Improvement",
                "MASH Resolution",
                "MRI-PDFF",
                "ELF Score",
            ],
            preferred_architectures=[
                "Adaptive Trial",
                "Adaptive Enrichment",
                "Master Protocol",
            ],
            preferred_statistics=[
                "Bayesian Adaptive Design",
                "Joint Models",
                "Adaptive Re-estimation",
            ],
            sample_size_considerations=[
                "Fibrosis response rate",
                "Biopsy attrition rate",
            ],
            interim_analysis_considerations=["DSMB", "Futility Assessment"],
            tte_considerations=["IPTW", "MSM"],
            emerging_biomarkers=["ELF", "PRO-C3", "AI Pathology"],
            emerging_therapeutics=[
                "THR-beta Agonists",
                "GLP-1",
                "Combination Therapy",
            ],
            precision_hepatology=[
                "Risk Enrichment",
                "Fibrosis Stratification",
            ],
            reviewer_attack_points=["Missing Histology", "Biopsy Attrition"],
            publication_opportunities=[
                "Histology-free Endpoints",
                "Combination Therapy",
            ],
        )

    # HCC
    elif disease == "hcc":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "Recurrence Prevention",
                "Advanced HCC",
                "Immunotherapy Sequencing",
            ],
            preferred_endpoints=[
                "Overall Survival",
                "Progression-Free Survival",
                "Recurrence-Free Survival",
            ],
            preferred_architectures=[
                "Platform Trial",
                "Adaptive Trial",
                "Master Protocol",
            ],
            preferred_statistics=[
                "Competing Risk",
                "Multi-state Models",
                "Joint Frailty Models",
            ],
            sample_size_considerations=["Event Rate", "Overall Survival"],
            interim_analysis_considerations=[
                "Event-driven Monitoring",
                "DSMB",
            ],
            tte_considerations=["IPTW", "CCW"],
            emerging_biomarkers=["ctDNA", "MRD"],
            emerging_therapeutics=["IO+IO", "IO+TKI"],
            precision_hepatology=["ctDNA-guided Therapy"],
            reviewer_attack_points=[
                "Post-progression Therapy",
                "Competing Risk",
            ],
            publication_opportunities=[
                "ctDNA-guided Strategies",
                "Platform Trials",
            ],
        )

    # CIRRHOSIS
    elif disease == "cirrhosis":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "Decompensation Prevention",
                "ACLF Prevention",
            ],
            preferred_endpoints=[
                "Decompensation",
                "Transplant-free Survival",
                "Overall Survival",
            ],
            preferred_architectures=["Event-driven RCT"],
            preferred_statistics=["Competing Risk", "Multi-state Models"],
            sample_size_considerations=["Decompensation Rate"],
            interim_analysis_considerations=["Event-driven DSMB"],
            tte_considerations=["IPTW"],
            emerging_biomarkers=["Frailty Metrics"],
            emerging_therapeutics=["Disease-modifying Strategies"],
            precision_hepatology=["Risk Stratification"],
            reviewer_attack_points=[
                "Competing Risk",
                "Informative Censoring",
            ],
            publication_opportunities=["Decompensation Prevention"],
        )

    # PORTAL HYPERTENSION
    elif disease == "portal hypertension":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "HVPG Reduction",
                "Variceal Bleeding Prevention",
            ],
            preferred_endpoints=[
                "HVPG",
                "Variceal Bleeding",
                "Decompensation",
            ],
            preferred_architectures=["RCT"],
            preferred_statistics=["Competing Risk"],
            sample_size_considerations=["Bleeding Event Rate"],
            interim_analysis_considerations=["Safety Monitoring"],
            tte_considerations=["IPTW"],
            emerging_biomarkers=["Non-invasive Portal Pressure Markers"],
            emerging_therapeutics=["Portal Pressure Modulators"],
            precision_hepatology=["HVPG-guided Therapy"],
            reviewer_attack_points=[
                "Death as Competing Risk",
                "Transplant as Competing Risk",
            ],
            publication_opportunities=["HVPG-guided Strategies"],
        )

    # PBC
    elif disease == "pbc":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "Biochemical Response",
                "Long-term Outcomes",
            ],
            preferred_endpoints=["ALP", "Bilirubin"],
            preferred_architectures=["Parallel-group RCT"],
            preferred_statistics=["ANCOVA"],
            sample_size_considerations=["ALP Response Rate"],
            interim_analysis_considerations=["DSMB"],
            tte_considerations=[],
            emerging_biomarkers=["ELF"],
            emerging_therapeutics=["FXR Agonists", "PPAR Agonists"],
            precision_hepatology=[],
            reviewer_attack_points=["Surrogate Endpoint Validity"],
            publication_opportunities=["Long-term Outcome Studies"],
        )

    # AIH
    elif disease == "aih":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=["Remission", "Relapse Prevention"],
            preferred_endpoints=[
                "Biochemical Remission",
                "Histologic Remission",
            ],
            preferred_architectures=["Registry", "Pragmatic Trial"],
            preferred_statistics=["Bayesian Design"],
            sample_size_considerations=["Rare Disease Recruitment"],
            interim_analysis_considerations=[],
            tte_considerations=[],
            emerging_biomarkers=["Immune Signatures"],
            emerging_therapeutics=["Steroid-sparing Strategies"],
            precision_hepatology=[],
            reviewer_attack_points=["Small Sample Size"],
            publication_opportunities=["Rare Disease Methodology"],
        )

    # ALD
    elif disease == "ald":
        return HepatologyIntelligenceResponse(
            disease=req.disease,
            clinical_questions=[
                "Alcoholic Hepatitis",
                "Abstinence Intervention",
            ],
            preferred_endpoints=[
                "Overall Survival",
                "Liver-related Outcomes",
            ],
            preferred_architectures=["Pragmatic Trial"],
            preferred_statistics=["Competing Risk"],
            sample_size_considerations=["Survival Event Rate"],
            interim_analysis_considerations=["Safety Monitoring"],
            tte_considerations=["IPTW"],
            emerging_biomarkers=["Alcohol Use Biomarkers"],
            emerging_therapeutics=["Anti-inflammatory Strategies"],
            precision_hepatology=[],
            reviewer_attack_points=["Adherence Bias", "Survivor Bias"],
            publication_opportunities=["Alcohol Abstinence Strategies"],
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
        publication_opportunities=[],
    )
