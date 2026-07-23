from dataclasses import dataclass, field
from enum import Enum


class ProductType(str, Enum):
    PHYSICAL = "physical"
    SERVICE = "service"
    MIXED = "mixed"


class RevisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REVISION_NEEDED = "REVISION_NEEDED"
    REJECTED = "REJECTED"


@dataclass
class FounderProfile:
    name: str
    skills: list[str]
    availability: str


@dataclass
class BusinessIdeaProfile:
    project_name: str
    idea_description: str
    need_addressed: str
    product_type: ProductType
    sector_hint: str
    target_region: str
    founders: list[FounderProfile]
    available_capital_eur: float
    desired_timeline_months: int
    notes: str = ""
    raw_intake_notes: dict[str, str] = field(default_factory=dict)


@dataclass
class IntakeReport:
    profile: BusinessIdeaProfile
    needs_clarification: list[str]
    summary_markdown: str
    confidence: float


@dataclass
class ChartSpec:
    chart_type: str
    title: str
    labels: list[str]
    series: dict[str, list[float]]
    filename: str


@dataclass
class AgentOutput:
    agent_name: str
    status: str
    data: dict
    confidence: float
    reasoning: str
    revision_count: int = 0


@dataclass
class OrchestratorResult:
    plan_id: str
    profile: BusinessIdeaProfile
    agent_outputs: dict[str, AgentOutput]
    revision_log: list[dict]
    charts_generated: list[str]
    business_plan_markdown: str
    business_plan_docx_path: str
    business_plan_md_path: str
    total_iterations: int
    status: RevisionStatus
