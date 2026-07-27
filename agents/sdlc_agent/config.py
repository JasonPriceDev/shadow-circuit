"""Labels, milestones, and repo metadata for the SDLC harness agent."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RepoConfig:
    """Canonical metadata about this repository."""

    owner: str = "JasonPriceDev"
    repo: str = "shadow-circuit"
    default_branch: str = "main"

    milestones: list[str] = field(default_factory=lambda: [
        "v0.1 Vertical Slice",
        "v0.2 Content Pipeline",
        "v0.3 Districts 2-4",
        "v0.4 Districts 5-7",
        "v1.0 Shadow Citadel & Release",
    ])

    type_labels: list[str] = field(default_factory=lambda: [
        "type:spec",
        "type:epic",
        "type:feature",
        "type:task",
        "type:bug",
        "type:chore",
        "type:research",
    ])

    area_labels: list[str] = field(default_factory=lambda: [
        "area:player",
        "area:enemy",
        "area:boss",
        "area:stage",
        "area:systems",
        "area:ui",
        "area:build",
        "area:ci",
    ])

    discipline_labels: list[str] = field(default_factory=lambda: [
        "discipline:code",
        "discipline:art",
        "discipline:audio",
        "discipline:design",
        "discipline:qa",
    ])

    severity_labels: list[str] = field(default_factory=lambda: [
        "severity:critical",
        "severity:major",
        "severity:minor",
    ])

    status_labels: list[str] = field(default_factory=lambda: [
        "status:needs-triage",
        "status:ready",
        "status:blocked",
        "status:playtest",
    ])

    agent_label: str = "agent:generated"

    def all_labels(self) -> list[str]:
        return [
            *self.type_labels,
            *self.area_labels,
            *self.discipline_labels,
            *self.severity_labels,
            *self.status_labels,
            self.agent_label,
        ]


# Singleton for import convenience.
config = RepoConfig()
