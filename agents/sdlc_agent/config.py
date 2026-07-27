"""Repository metadata and SDLC taxonomy."""

from dataclasses import dataclass, field
import os


@dataclass(frozen=True)
class RepoConfig:
    owner: str = "JasonPriceDev"
    repo: str = "shadow-circuit"
    default_branch: str = "main"
    agent_label: str = "agent:generated"
    branch_prefix: str = "agent/task-"

    milestones: tuple[str, ...] = (
        "v0.1 Vertical Slice",
        "v0.2 Content Pipeline",
        "v0.3 Districts 2-4",
        "v0.4 Districts 5-7",
        "v1.0 Shadow Citadel & Release",
    )
    type_labels: tuple[str, ...] = (
        "type:spec",
        "type:epic",
        "type:feature",
        "type:task",
        "type:bug",
        "type:chore",
        "type:research",
    )
    area_labels: tuple[str, ...] = (
        "area:player",
        "area:enemy",
        "area:boss",
        "area:stage",
        "area:systems",
        "area:ui",
        "area:build",
        "area:ci",
        "area:agent",
    )
    discipline_labels: tuple[str, ...] = (
        "discipline:code",
        "discipline:art",
        "discipline:audio",
        "discipline:design",
        "discipline:qa",
    )
    severity_labels: tuple[str, ...] = (
        "severity:critical",
        "severity:major",
        "severity:minor",
    )
    status_labels: tuple[str, ...] = (
        "status:proposed",
        "status:triaged",
        "status:ready",
        "status:in-progress",
        "status:in-review",
        "status:playtest",
        "status:done",
        "status:blocked",
    )
    approval_labels: tuple[str, ...] = (
        "approve:plan",
        "approve:create-issues",
        "approve:implement",
        "approve:revise",
        "approve:close",
    )
    approvers: tuple[str, ...] = field(
        default_factory=lambda: ("JasonPriceDev",),
    )
    restricted_paths: tuple[str, ...] = (
        ".github/workflows/",
        ".github/CODEOWNERS",
        ".github/copilot-instructions.md",
        ".github/instructions/",
        "AGENTS.md",
        "agents/sdlc_agent/instructions.py",
        "agents/requirements.txt",
        "package.json",
        "package-lock.json",
    )

    @property
    def full_name(self) -> str:
        return os.environ.get("GITHUB_REPOSITORY", f"{self.owner}/{self.repo}")

    @property
    def taxonomy_labels(self) -> tuple[str, ...]:
        return (
            *self.type_labels,
            *self.area_labels,
            *self.discipline_labels,
            *self.severity_labels,
        )

    @property
    def all_labels(self) -> tuple[str, ...]:
        return (
            *self.taxonomy_labels,
            *self.status_labels,
            *self.approval_labels,
            self.agent_label,
        )


config = RepoConfig()
