"""Build 7 distinct interview questions for custom job roles."""

# Preset banks keyed by substring match (lowercase role name)
ROLE_PRESETS = {
    "devops": [
        {"q": "How do you design a CI/CD pipeline for reliable deployments?", "a": "Automated build, test, staging, and rollback with monitoring."},
        {"q": "Explain your approach to infrastructure as code.", "a": "Version-controlled templates, idempotent provisioning, and peer review."},
        {"q": "How do you handle production incidents and postmortems?", "a": "Triage, communicate, fix, document root cause, and prevent recurrence."},
        {"q": "What is your strategy for container orchestration at scale?", "a": "Kubernetes workloads, resource limits, health checks, and autoscaling."},
        {"q": "How do you manage secrets and configuration across environments?", "a": "Secret managers, least privilege, rotation, and environment separation."},
        {"q": "How do you monitor system health and SLOs?", "a": "Metrics, logs, alerts, error budgets, and on-call runbooks."},
        {"q": "How do you balance speed and stability in releases?", "a": "Feature flags, canary deploys, automated tests, and blast-radius control."},
    ],
    "product manager": [
        {"q": "How do you prioritize features on a crowded roadmap?", "a": "User impact, business value, effort, and data-driven tradeoffs."},
        {"q": "Describe how you gather and validate customer requirements.", "a": "Interviews, analytics, prototypes, and iterative feedback loops."},
        {"q": "How do you define success metrics for a new product?", "a": "Clear KPIs, baselines, experiments, and outcome over output."},
        {"q": "How do you work with engineering when scope slips?", "a": "Re-scope MVP, align on must-haves, and transparent stakeholder updates."},
        {"q": "Explain a go-to-market plan you have driven.", "a": "Positioning, launch phases, channels, and post-launch iteration."},
        {"q": "How do you handle conflicting stakeholder priorities?", "a": "Facilitate alignment, document decisions, and tie back to strategy."},
        {"q": "What frameworks do you use for product discovery?", "a": "Jobs-to-be-done, opportunity solution trees, and rapid experimentation."},
    ],
    "ux": [
        {"q": "Walk through your end-to-end design process.", "a": "Research, personas, wireframes, testing, and handoff with developers."},
        {"q": "How do you validate designs before development?", "a": "Usability tests, prototypes, A/B tests, and heuristic evaluation."},
        {"q": "How do you balance user needs with business goals?", "a": "Evidence from research, prioritization, and measurable UX outcomes."},
        {"q": "Describe how you build and maintain a design system.", "a": "Reusable components, documentation, accessibility, and governance."},
        {"q": "How do you design for accessibility?", "a": "WCAG guidelines, contrast, keyboard flow, and inclusive patterns."},
        {"q": "How do you collaborate with product and engineering?", "a": "Shared specs, critiques, iteration, and clear acceptance criteria."},
        {"q": "Tell us about a redesign that improved key metrics.", "a": "Problem, hypothesis, solution, measurement, and lessons learned."},
    ],
    "cyber": [
        {"q": "How do you perform a risk assessment for a new system?", "a": "Asset inventory, threats, likelihood, impact, and mitigation plan."},
        {"q": "Explain defense in depth in modern architectures.", "a": "Layered controls across network, identity, data, and application."},
        {"q": "How do you respond to a suspected security breach?", "a": "Contain, preserve evidence, eradicate, recover, and report."},
        {"q": "What is your approach to vulnerability management?", "a": "Scanning, prioritization by exploitability, patching, and verification."},
        {"q": "How do you implement least-privilege access?", "a": "Role-based access, MFA, periodic reviews, and just-in-time elevation."},
        {"q": "How do you secure cloud workloads?", "a": "Hardening, encryption, logging, IAM policies, and compliance checks."},
        {"q": "How do you promote security awareness in an organization?", "a": "Training, phishing simulations, policies, and secure SDLC practices."},
    ],
    "marketing": [
        {"q": "How do you build a multi-channel marketing campaign?", "a": "Audience segmentation, messaging, budget, channels, and KPI tracking."},
        {"q": "How do you measure campaign ROI?", "a": "Attribution, conversion funnels, CAC, LTV, and incrementality tests."},
        {"q": "Describe your content strategy for brand growth.", "a": "Audience insights, editorial calendar, SEO, and performance optimization."},
        {"q": "How do you use data to improve acquisition?", "a": "Analytics, cohort analysis, A/B tests, and channel optimization."},
        {"q": "How do you manage brand positioning vs competitors?", "a": "Differentiation, messaging pillars, and consistent voice."},
        {"q": "How do you align marketing with sales goals?", "a": "SLAs, lead scoring, shared dashboards, and feedback loops."},
        {"q": "What trends are shaping digital marketing today?", "a": "Privacy changes, AI tools, short-form video, and first-party data."},
    ],
    "hr": [
        {"q": "How do you design an effective hiring process?", "a": "Structured interviews, scorecards, diversity goals, and candidate experience."},
        {"q": "How do you handle employee performance issues?", "a": "Documented feedback, PIP, support, and fair consistent policy."},
        {"q": "Describe your approach to employee engagement.", "a": "Surveys, listening sessions, recognition, and manager enablement."},
        {"q": "How do you stay compliant with labor regulations?", "a": "Policy updates, training, audits, and legal partnership."},
        {"q": "How do you support learning and development?", "a": "Skills frameworks, budgets, mentorship, and career paths."},
        {"q": "How do you manage conflict between team members?", "a": "Neutral facilitation, clear expectations, and follow-up."},
        {"q": "How do you build an inclusive workplace culture?", "a": "Inclusive policies, ERGs, bias training, and equitable practices."},
    ],
    "sales": [
        {"q": "Walk through your sales methodology from lead to close.", "a": "Qualify, discover needs, demo value, handle objections, and negotiate."},
        {"q": "How do you handle a major deal at risk of slipping?", "a": "Identify blockers, multi-thread stakeholders, and create urgency with value."},
        {"q": "How do you build long-term client relationships?", "a": "Trust, regular check-ins, success metrics, and expansion opportunities."},
        {"q": "How do you forecast pipeline accurately?", "a": "Stage definitions, historical conversion, and disciplined CRM hygiene."},
        {"q": "Describe a time you lost a deal and what you learned.", "a": "Honest post-mortem, process fix, and improved qualification."},
        {"q": "How do you collaborate with marketing on leads?", "a": "ICP alignment, lead scoring, feedback on quality, and SLAs."},
        {"q": "How do you negotiate without damaging the relationship?", "a": "Focus on mutual value, trade concessions, and clear terms."},
    ],
}

# Seven unique generic templates when no preset matches (role name woven in)
GENERIC_TEMPLATES = [
    (
        "What core skills and experience are essential for a {role}?",
        "Relevant domain knowledge, proven tools, and hands-on project experience.",
    ),
    (
        "Describe a difficult challenge you faced as a {role} and how you solved it.",
        "Defined the problem, took structured action, and delivered measurable results.",
    ),
    (
        "Which tools, methods, or frameworks do you rely on most as a {role}?",
        "Industry-standard stack with practical examples and continuous improvement.",
    ),
    (
        "How do you collaborate with teammates and stakeholders in a {role} position?",
        "Clear communication, shared goals, accountability, and constructive feedback.",
    ),
    (
        "How do you prioritize work when facing tight deadlines as a {role}?",
        "Impact and urgency analysis, stakeholder alignment, and focused execution.",
    ),
    (
        "How do you stay current with trends and best practices for a {role}?",
        "Learning plans, communities, certifications, and applying new knowledge on the job.",
    ),
    (
        "Why are you a strong fit for this {role} opportunity?",
        "Relevant achievements, motivation, cultural alignment, and growth potential.",
    ),
]


def _match_preset(role_lower):
    """Return preset questions if role name matches a known category."""
    # Order longer keys first so "product manager" beats "product"
    for key in sorted(ROLE_PRESETS.keys(), key=len, reverse=True):
        if key in role_lower:
            return [dict(item) for item in ROLE_PRESETS[key]]
    if "designer" in role_lower or "ui " in role_lower:
        return [dict(item) for item in ROLE_PRESETS["ux"]]
    if "security" in role_lower or "infosec" in role_lower:
        return [dict(item) for item in ROLE_PRESETS["cyber"]]
    if "sre" in role_lower or "site reliability" in role_lower:
        return [dict(item) for item in ROLE_PRESETS["devops"]]
    if "human resources" in role_lower or role_lower.startswith("hr"):
        return [dict(item) for item in ROLE_PRESETS["hr"]]
    return None


def build_custom_role_questions(role):
    """Return exactly 7 distinct Q&A dicts tailored to the job role."""
    role = (role or "Professional").strip()
    role_lower = role.lower()

    preset = _match_preset(role_lower)
    if preset:
        return preset[:7]

    questions = []
    for q_tpl, a_tpl in GENERIC_TEMPLATES:
        questions.append({
            "q": q_tpl.format(role=role),
            "a": a_tpl,
        })
    return questions[:7]
