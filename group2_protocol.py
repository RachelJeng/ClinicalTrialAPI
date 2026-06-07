"""
group2_protocol.py
==================
Layer 2 — Protocol Development

Endpoints that generate protocol text, estimands, SAPs, ClinicalTrials.gov
packages, CRF / REDCap builders, brochures, and target-trial-emulation
(TTE) designs.
"""

from fastapi import APIRouter

from shared_models import (
    ProtocolSampleSizeRequest,
    ProtocolEndpointsRequest,
    ProtocolEstimandRequest,
    SAPRequest,
    AdvancedSAPRequest,
    AdvancedSAPResponse,
    ClinicalTrialsGovRequest,
    ClinicalTrialsGovResponse,
    ClinicalTrialsGovV2Request,
    ClinicalTrialsGovV2Response,
    CRFBuilderRequest,
    CRFBuilderResponse,
    REDCapBuilderRequest,
    REDCapBuilderResponse,
    REDCapBuilderV3Request,
    REDCapBuilderV3Response,
    BrochureRequest,
    BrochureResponse,
    TTERequest,
    TTEResponse,
    TTEV2Request,
    TTEV2Response,
    TTEV3Request,
    TTEV3Response,
)

router = APIRouter()


# =========================
# Protocol Sample Size
# =========================

@router.post("/protocol/sample-size", tags=["Protocol Development"])
def generate_sample_size_protocol(req: ProtocolSampleSizeRequest):

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

    return {"protocol_text": protocol_text}


# =========================
# Protocol Endpoints
# =========================

@router.post("/protocol/endpoints", tags=["Protocol Development"])
def generate_protocol_endpoints(req: ProtocolEndpointsRequest):

    primary_endpoint = (
        f"Assessment of {req.primary_objective} "
        f"in participants with {req.disease} "
        f"receiving {req.intervention}."
    )

    secondary_endpoints = [
        "Change in disease-related biomarkers.",
        "Change in laboratory parameters.",
        "Safety and tolerability outcomes.",
    ]

    exploratory_endpoints = [
        "Patient-reported outcomes.",
        "Health-related quality of life.",
        "Exploratory biomarker analyses.",
    ]

    return {
        "primary_endpoint": primary_endpoint,
        "secondary_endpoints": secondary_endpoints,
        "exploratory_endpoints": exploratory_endpoints,
    }


# =========================
# Protocol Estimand
# =========================

@router.post("/protocol/estimand", tags=["Protocol Development"])
def generate_estimand(req: ProtocolEstimandRequest):

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
        "estimand_text": estimand_text,
    }


# =========================
# Statistical Analysis Plan
# =========================

@router.post(
    "/sap/statistical-analysis-plan",
    tags=["Statistical Analysis Plan"],
)
def generate_sap(req: SAPRequest):

    endpoint_type = req.endpoint_type.lower()

    if endpoint_type == "binary":
        return {
            "analysis_population": "Intention-to-treat",
            "primary_analysis": "Logistic regression",
            "missing_data": "Multiple imputation",
            "sensitivity_analysis": "Per-protocol analysis",
        }

    if endpoint_type == "continuous":
        return {
            "analysis_population": "Intention-to-treat",
            "primary_analysis": "ANCOVA",
            "missing_data": "Multiple imputation",
            "sensitivity_analysis": "Mixed model repeated measures",
        }

    if endpoint_type == "survival":
        return {
            "analysis_population": "Intention-to-treat",
            "primary_analysis": "Log-rank test and Cox model",
            "missing_data": "Censoring rules predefined",
            "sensitivity_analysis": "Per-protocol analysis",
        }

    return {"message": "Endpoint type not supported"}


# =========================
# Advanced SAP
# =========================

@router.post(
    "/orchestrator/advanced-sap",
    response_model=AdvancedSAPResponse,
    tags=["Statistics"],
)
def advanced_sap(req: AdvancedSAPRequest):

    endpoint_type = req.endpoint_type.lower()

    analysis_population = "Intention-to-Treat"
    multiplicity_strategy = "Hierarchical Testing"
    covariate_adjustment = ["Age", "Sex", "Baseline Disease Severity"]
    subgroup_analysis = ["Age Group", "Sex", "Disease Severity"]
    missing_data_strategy = "Multiple Imputation"
    sensitivity_analysis = ["Per Protocol Analysis", "Worst Case Analysis"]

    if endpoint_type == "binary":
        primary_analysis = "Logistic Regression"
    elif endpoint_type == "continuous":
        primary_analysis = "ANCOVA"
    elif endpoint_type == "survival":
        primary_analysis = "Cox Proportional Hazards Model"
    else:
        primary_analysis = "Manual Review"

    return AdvancedSAPResponse(
        analysis_population=analysis_population,
        primary_analysis=primary_analysis,
        multiplicity_strategy=multiplicity_strategy,
        covariate_adjustment=covariate_adjustment,
        subgroup_analysis=subgroup_analysis,
        missing_data_strategy=missing_data_strategy,
        sensitivity_analysis=sensitivity_analysis,
    )


# =========================
# ClinicalTrials.gov Package
# =========================

@router.post(
    "/orchestrator/clinicaltrialsgov-package",
    response_model=ClinicalTrialsGovResponse,
    tags=["Trial Operations"],
)
def clinicaltrialsgov_package(req: ClinicalTrialsGovRequest):

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

    primary_outcome_measure = req.primary_endpoint

    eligibility_criteria = (
        f"Adults with "
        f"{req.disease} "
        f"meeting study eligibility criteria."
    )

    return ClinicalTrialsGovResponse(
        brief_title=brief_title,
        official_title=official_title,
        brief_summary=brief_summary,
        detailed_description=detailed_description,
        primary_outcome_measure=primary_outcome_measure,
        eligibility_criteria=eligibility_criteria,
    )


# =========================
# ClinicalTrials.gov Package V2
# =========================

@router.post(
    "/orchestrator/clinicaltrialsgov-package-v2",
    response_model=ClinicalTrialsGovV2Response,
    tags=["Trial Operations"],
)
def clinicaltrialsgov_package_v2(req: ClinicalTrialsGovV2Request):

    spec = req.trial_specification

    disease = spec.disease if spec.disease else "Target Disease"
    intervention = (
        spec.intervention if spec.intervention else "Study Intervention"
    )
    endpoint = spec.primary_endpoint if spec.primary_endpoint else "Primary Endpoint"
    design = spec.study_design if spec.study_design else "Clinical Trial"

    brief_title = f"{intervention} in {disease}"

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
        brief_title=brief_title,
        official_title=official_title,
        brief_summary=brief_summary,
        detailed_description=detailed_description,
        primary_outcome_measure=endpoint,
        eligibility_criteria=eligibility_criteria,
    )


# =========================
# CRF Builder
# =========================

@router.post(
    "/orchestrator/crf-builder",
    response_model=CRFBuilderResponse,
    tags=["Trial Operations"],
)
def crf_builder(req: CRFBuilderRequest):

    screening_fields = [
        "Informed Consent",
        "Eligibility Assessment",
        "Medical History",
    ]

    baseline_fields = [
        "Age",
        "Sex",
        "Disease Duration",
        "Baseline Laboratory Values",
    ]

    followup_fields = [
        "Visit Date",
        "Medication Adherence",
        "Laboratory Assessments",
    ]

    safety_fields = [
        "Adverse Events",
        "Serious Adverse Events",
        "Treatment Discontinuation",
    ]

    endpoint_fields = [req.primary_endpoint]

    return CRFBuilderResponse(
        screening_fields=screening_fields,
        baseline_fields=baseline_fields,
        followup_fields=followup_fields,
        safety_fields=safety_fields,
        endpoint_fields=endpoint_fields,
    )


# =========================
# REDCap Builder V2
# =========================

@router.post(
    "/orchestrator/redcap-builder-v2",
    response_model=REDCapBuilderResponse,
    tags=["Trial Operations"],
)
def redcap_builder_v2(req: REDCapBuilderRequest):

    variables = [
        {"field_name": "subject_id", "field_type": "text"},
        {"field_name": "visit_date", "field_type": "date"},
        {"field_name": "adverse_event", "field_type": "yesno"},
        {"field_name": "primary_endpoint", "field_type": "text"},
    ]

    return REDCapBuilderResponse(
        form_name=f"{req.disease} Study CRF",
        variable_definitions=variables,
    )


# =========================
# REDCap Builder V3
# =========================

@router.post(
    "/orchestrator/redcap-builder-v3",
    response_model=REDCapBuilderV3Response,
    tags=["Trial Operations"],
)
def redcap_builder_v3(req: REDCapBuilderV3Request):

    visit_schedule = [
        "Screening",
        "Baseline",
        "Week 4",
        "Week 12",
        "Week 24",
        "Week 48",
        "Week 96",
    ]

    forms = [
        {"form_name": "Screening"},
        {"form_name": "Baseline"},
        {"form_name": "Follow-up"},
        {"form_name": "Safety"},
        {"form_name": "Endpoint"},
    ]

    variable_metadata = [
        {
            "visit": "Baseline",
            "form_name": "Baseline",
            "field_name": "age",
            "field_label": "Age at Enrollment",
            "field_type": "number",
            "required": True,
            "validation": "integer",
            "choices": "",
        },
        {
            "visit": "Baseline",
            "form_name": "Baseline",
            "field_name": "sex",
            "field_label": "Sex",
            "field_type": "radio",
            "required": True,
            "validation": "",
            "choices": "1,Male | 2,Female",
        },
        {
            "visit": "Week 96",
            "form_name": "Endpoint",
            "field_name": "primary_endpoint",
            "field_label": req.primary_endpoint,
            "field_type": "text",
            "required": True,
            "validation": "",
            "choices": "",
        },
    ]

    return REDCapBuilderV3Response(
        visit_schedule=visit_schedule,
        forms=forms,
        variable_metadata=variable_metadata,
    )


# =========================
# Brochure Generator
# =========================

@router.post(
    "/orchestrator/brochure-generator",
    response_model=BrochureResponse,
    tags=["Trial Operations"],
)
def brochure_generator(req: BrochureRequest):

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
        scientific_rationale=scientific_rationale,
        unmet_need=unmet_need,
        expected_impact=expected_impact,
    )


# =========================
# TTE Design
# =========================

@router.post("/orchestrator/tte-design", response_model=TTEResponse)
def tte_design(req: TTERequest):

    text = req.research_question.lower()

    eligibility_criteria = "Patients meeting study eligibility criteria."
    time_zero = "Date of treatment strategy assignment."
    treatment_strategy = "Treatment versus comparator strategy."
    follow_up = "Follow participants until endpoint occurrence or censoring."
    causal_contrast = "Treatment effect under target trial framework."
    recommended_method = "Inverse Probability of Treatment Weighting (IPTW)"

    if "survival" in text or "time to event" in text:
        recommended_method = "Marginal Structural Model (MSM)"

    return TTEResponse(
        eligibility_criteria=eligibility_criteria,
        time_zero=time_zero,
        treatment_strategy=treatment_strategy,
        follow_up=follow_up,
        causal_contrast=causal_contrast,
        recommended_method=recommended_method,
    )


@router.post("/orchestrator/tte-design-v2", response_model=TTEV2Response)
def tte_design_v2(req: TTEV2Request):

    return TTEV2Response(
        eligibility_criteria=(
            "Patients meeting target trial eligibility criteria."
        ),
        time_zero="Date of treatment strategy assignment.",
        treatment_strategy="Treatment versus comparator.",
        follow_up="Until endpoint occurrence or censoring.",
        causal_contrast="Average treatment effect.",
        recommended_method="IPTW",
        sensitivity_analysis="Marginal Structural Model",
    )


# =========================
# TTE V3
# =========================

@router.post("/orchestrator/tte-design-v3", response_model=TTEV3Response)
def tte_design_v3(req: TTEV3Request):

    bias_report = [
        "Immortal Time Bias Risk: Review time-zero definition.",
        "Residual Confounding Risk: Evaluate measured and unmeasured "
        "confounders.",
        "Selection Bias Risk: Assess inclusion criteria.",
        "Measurement Bias Risk: Verify outcome ascertainment.",
    ]

    return TTEV3Response(
        eligibility_criteria=(
            "Patients meeting target trial eligibility criteria."
        ),
        time_zero="Date of treatment strategy assignment.",
        treatment_strategy="Treatment versus comparator.",
        follow_up="Until endpoint occurrence or censoring.",
        causal_contrast="Average treatment effect.",
        recommended_method="IPTW with Marginal Structural Model",
        cloning_censoring_weighting=True,
        positivity_diagnostics=(
            "Propensity score overlap assessment recommended."
        ),
        weight_diagnostics="Evaluate extreme weights and stabilized weights.",
        sequential_exchangeability=(
            "Assess exchangeability assumptions at each decision point."
        ),
        target_trial_bias_report=bias_report,
    )
