from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


# ── Pagination ─────────────────────────────────────────────


class PaginatedResult(TypedDict):
    items: List[Any]
    cursor: Optional[str]
    has_more: bool
    total: Optional[int]


class PaginationParams(TypedDict, total=False):
    cursor: str
    limit: int


# ── API Response Envelope ──────────────────────────────────


class ApiError(TypedDict, total=False):
    code: str
    message: str
    details: List[Any]


class PaginationMeta(TypedDict, total=False):
    cursor: Optional[str]
    has_more: bool
    total: int


class ApiMeta(TypedDict, total=False):
    request_id: str
    pagination: PaginationMeta


class ApiResponse(TypedDict, total=False):
    data: Any
    error: ApiError
    meta: ApiMeta


# ── Memory ─────────────────────────────────────────────────


MemoryType = Literal[
    "fact",
    "preference",
    "decision",
    "goal",
    "experience",
    "skill",
]

MemoryStatus = Literal[
    "active",
    "candidate",
    "archived",
    "conflicted",
]

SourceType = Literal[
    "user_input",
    "system_inference",
    "ai_extraction",
    "user_confirmed",
]


class MemoryItem(TypedDict):
    id: str
    user_id: str
    type: MemoryType
    title: str
    body: str
    source_type: SourceType
    confidence: float
    status: MemoryStatus
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class CreateMemoryInput(TypedDict, total=False):
    type: MemoryType  # required
    title: str  # required
    body: str  # required
    source_type: SourceType
    confidence: float
    metadata: Optional[Dict[str, Any]]


class UpdateMemoryInput(TypedDict, total=False):
    title: str
    body: str
    confidence: float
    status: Literal["active", "candidate", "archived"]
    metadata: Optional[Dict[str, Any]]


class MemoryListParams(TypedDict, total=False):
    cursor: str
    limit: int
    type: MemoryType
    status: MemoryStatus
    search: str


class MemorySearchInput(TypedDict, total=False):
    query: str  # required
    top_k: int


class MemorySearchResult(TypedDict):
    id: str
    title: str
    body: str
    type: MemoryType
    confidence: float
    score: float


class MemorySearchResponse(TypedDict):
    results: List[MemorySearchResult]
    mode: Literal["hybrid", "text"]


class ConsolidateInput(TypedDict, total=False):
    type: str
    threshold: float
    dry_run: bool


class ExpireInput(TypedDict, total=False):
    ttl_days: int


class ImportItem(TypedDict, total=False):
    type: MemoryType  # required
    title: str  # required
    body: str  # required
    source_type: SourceType
    confidence: float


class AiExtractInput(TypedDict, total=False):
    text: str  # required
    ai_provider: str


class IngestUrlInput(TypedDict):
    url: str


class ParseChatInput(TypedDict, total=False):
    transcript: str  # required
    format: str


class DuplicateEntry(TypedDict):
    id: str
    title: str
    similarity: float


class DuplicateGroup(TypedDict):
    id: str
    title: str
    duplicates: List[DuplicateEntry]


# ── Entity ─────────────────────────────────────────────────


class Entity(TypedDict):
    id: str
    user_id: str
    name: str
    type: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class EntityLink(TypedDict):
    id: str
    entity_id: str
    memory_item_id: str
    link_type: str
    created_at: str


class CreateEntityInput(TypedDict, total=False):
    name: str  # required
    type: str  # required
    description: str
    metadata: Optional[Dict[str, Any]]


class UpdateEntityInput(TypedDict, total=False):
    name: str
    type: str
    description: str
    metadata: Optional[Dict[str, Any]]


class CreateEntityLinkInput(TypedDict):
    memory_item_id: str
    link_type: str


class EntityListParams(TypedDict, total=False):
    cursor: str
    limit: int
    type: str


class EntityMergeInput(TypedDict):
    keep_id: str
    remove_id: str


class AutoExtractInput(TypedDict):
    memory_id: str


# ── Project ────────────────────────────────────────────────


ProjectStatus = Literal["active", "archived", "completed"]


class Project(TypedDict):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    status: ProjectStatus
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class ProjectMemoryLink(TypedDict):
    id: str
    project_id: str
    memory_item_id: str
    link_type: str
    created_at: str


class CreateProjectInput(TypedDict, total=False):
    name: str  # required
    status: ProjectStatus
    description: str
    metadata: Optional[Dict[str, Any]]


class UpdateProjectInput(TypedDict, total=False):
    name: str
    status: ProjectStatus
    description: str
    metadata: Optional[Dict[str, Any]]


class CreateProjectMemoryLinkInput(TypedDict):
    memory_item_id: str
    link_type: str


class ProjectListParams(TypedDict, total=False):
    cursor: str
    limit: int
    status: ProjectStatus


# ── Brain ──────────────────────────────────────────────────


class BrainProfile(TypedDict):
    summary: Optional[str]
    traits: Dict[str, Any]
    preferences: Dict[str, Any]


class UpdateBrainProfileInput(TypedDict, total=False):
    summary: str
    traits: Dict[str, Any]
    preferences: Dict[str, Any]


class BrainContextMemory(TypedDict):
    type: str
    title: str
    body: str
    confidence: float


class BrainContextEntity(TypedDict):
    name: str
    type: str
    description: Optional[str]
    link_count: int


class BrainContextProject(TypedDict):
    name: str
    description: Optional[str]
    status: str


class BrainContextStats(TypedDict, total=False):
    total_memories: int
    total_entities: int
    total_projects: int


class BrainContextStructured(TypedDict, total=False):
    profile: BrainProfile
    memories: List[BrainContextMemory]
    entities: List[BrainContextEntity]
    projects: List[BrainContextProject]
    stats: BrainContextStats


class ContextMeta(TypedDict):
    scope: str
    token_estimate: int
    truncated: bool


class BrainContext(TypedDict):
    formatted: str
    structured: BrainContextStructured
    meta: ContextMeta


# ── Context ────────────────────────────────────────────────


ContextScope = Literal["brief", "assistant", "project", "deep"]


class OptimizedContext(TypedDict):
    formatted: str
    structured: Dict[str, Any]
    meta: ContextMeta


# ── Connect ────────────────────────────────────────────────


class ConnectReadOptions(TypedDict, total=False):
    scope: ContextScope
    format: Literal["text", "json"]


class ConnectWriteResult(TypedDict, total=False):
    status: Literal["created", "duplicate"]
    id: str
    title: str


class ConnectBatchResult(TypedDict):
    results: List[ConnectWriteResult]
    created: int
    duplicates: int


class DeltaSyncChange(TypedDict):
    id: str
    type: str
    action: Literal["created", "updated", "deleted"]
    timestamp: str


class DeltaSyncResult(TypedDict):
    changes: List[DeltaSyncChange]
    count: int


# ── DeepRecall (Enhanced Search) ───────────────────────────


SearchMode = Literal["keyword", "vector", "hybrid"]


class DeepSearchInput(TypedDict, total=False):
    query: str  # required
    mode: SearchMode
    top_k: int
    alpha: float


class DeepSearchResult(TypedDict):
    id: str
    title: str
    body: str
    type: MemoryType
    confidence: float
    score: float
    dice_score: float
    vector_score: float


class DeepSearchResponse(TypedDict, total=False):
    results: List[DeepSearchResult]
    search_mode: str
    downgraded_from: str


class EmbeddingStatus(TypedDict):
    total_memories: int
    embedded: int
    pending: int
    failed: int
    missing: int
    coverage: float


class ReindexInput(TypedDict, total=False):
    status: Literal["failed", "missing"]
    max_items: int


class ReindexResult(TypedDict, total=False):
    total: int
    queued: int
    errors: int
    error: str


# ── SkillForge ─────────────────────────────────────────────


SkillStatus = Literal[
    "candidate",
    "active",
    "archived",
    "dismissed",
]

SkillFeedbackEvent = Literal[
    "applied",
    "referenced",
    "dismissed",
]


class SkillItem(TypedDict):
    id: str
    title: str
    body: str
    status: SkillStatus
    confidence_score: float
    usage_count: int
    trigger_conditions: List[str]


class SkillListParams(TypedDict, total=False):
    cursor: str
    limit: int
    status: SkillStatus
    min_confidence: float
    sort_by: Literal["confidence", "usage", "recency"]


class SkillFeedbackInput(TypedDict, total=False):
    event_type: SkillFeedbackEvent  # required
    context: Dict[str, Any]


# ── BrainPulse ─────────────────────────────────────────────


BriefingType = Literal[
    "morning",
    "midday",
    "evening",
    "event_triggered",
    "weekly_health",
]

BriefingStatus = Literal[
    "pending",
    "generating",
    "ready",
    "delivered",
    "failed",
]


class BriefingConfig(TypedDict):
    id: str
    is_enabled: bool
    timezone: str
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    channels: List[str]


class BriefingItem(TypedDict):
    id: str
    type: BriefingType
    status: BriefingStatus
    title: str
    created_at: str


class BriefingListParams(TypedDict, total=False):
    cursor: str
    limit: int
    type: BriefingType
    status: BriefingStatus


# ── Billing ────────────────────────────────────────────────


class UsageStats(TypedDict):
    period: str
    usage: Dict[str, Any]


class PlanDetails(TypedDict):
    name: str
    limits: Dict[str, Any]


# ── API Keys ──────────────────────────────────────────────


class ApiKey(TypedDict):
    id: str
    name: str
    prefix: str
    scopes: List[str]
    trust_level: Literal["review", "trusted"]
    created_at: str
    last_used_at: Optional[str]


class CreateApiKeyInput(TypedDict, total=False):
    name: str  # required
    scopes: List[str]


class ApiKeyCreated(TypedDict):
    id: str
    name: str
    prefix: str
    scopes: List[str]
    trust_level: Literal["review", "trusted"]
    created_at: str
    last_used_at: Optional[str]
    full_key: str
