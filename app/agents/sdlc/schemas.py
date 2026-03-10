"""
schemas.py - Pydantic schemas for all 5 SDLC planning stages.
Each schema defines the structured AI output for its stage.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================
# STAGE 1: PROJECT OVERVIEW
# ============================================

class ProjectOverviewOutput(BaseModel):
    """AI-generated project overview — high-level vision and scope."""

    title: str = Field(..., description="Project title")
    description: str = Field(..., description="2-3 sentence project description")
    goals: List[str] = Field(..., description="3-5 specific project goals")
    target_audience: str = Field(..., description="Who this project is for")
    key_metrics: List[str] = Field(default_factory=list, description="Success metrics / KPIs")
    tech_recommendations: str = Field(default="", description="Recommended tech stack and why")
    timeline_estimate: str = Field(default="", description="Rough timeline estimate")
    domain: str = Field(default="", description="Project domain (e.g., E-commerce, Healthcare)")


# ============================================
# STAGE 2: REQUIREMENTS
# ============================================

class Requirement(BaseModel):
    """A single functional or non-functional requirement."""
    id: str = Field(..., description="Unique ID like FR-001")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(default="medium", description="high / medium / low")
    category: str = Field(default="", description="Category grouping")


class RequirementsOutput(BaseModel):
    """AI-generated project requirements."""

    functional_requirements: List[Requirement] = Field(
        ..., description="Functional requirements (what the system must do)"
    )
    non_functional_requirements: List[Requirement] = Field(
        default_factory=list, description="Non-functional requirements (performance, security, etc.)"
    )
    constraints: List[str] = Field(default_factory=list, description="Technical or business constraints")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")


# ============================================
# STAGE 3: USER RESEARCH
# ============================================

class UserRole(BaseModel):
    """A user role that interacts with the system."""
    name: str = Field(..., description="Role name (e.g., 'Admin', 'Customer')")
    description: str = Field(..., description="How this role interacts with the system")


class EmpathyMap(BaseModel):
    """What the persona thinks, feels, says, and does."""
    thinks: List[str] = Field(default_factory=list, description="What they think")
    feels: List[str] = Field(default_factory=list, description="What they feel")
    says: List[str] = Field(default_factory=list, description="What they say")
    does: List[str] = Field(default_factory=list, description="What they do")


class UserPersona(BaseModel):
    """AI-generated user persona with demographics and psychology."""
    name: str = Field(..., description="Persona full name")
    age: int = Field(..., description="Age")
    occupation: str = Field(..., description="Job/occupation")
    location: str = Field(..., description="Geographic location")
    role: str = Field(..., description="Which UserRole this persona represents")
    goals: List[str] = Field(..., description="3-5 user goals")
    key_characteristics: List[str] = Field(..., description="3-5 characteristics")
    pain_points: List[str] = Field(..., description="3-5 frustrations")
    empathy_map: EmpathyMap = Field(default_factory=EmpathyMap, description="Empathy map")


class UserResearchOutput(BaseModel):
    """AI-generated user research — roles and personas."""

    roles: List[UserRole] = Field(..., description="All user roles in the system")
    personas: List[UserPersona] = Field(..., description="Detailed personas for key roles")


# ============================================
# STAGE 4: TASK FLOWS
# ============================================

class FlowConnection(BaseModel):
    """A connection between two nodes in a task flow."""
    target_id: str = Field(..., description="ID of the target node")
    label: str = Field(default="", description="Edge label (e.g., 'Yes', 'No')")


class FlowStep(BaseModel):
    """A single step/node in a task flow diagram."""
    id: str = Field(..., description="Unique node ID")
    label: str = Field(..., description="Display label for this step")
    type: str = Field(
        ..., description="Node type: 'start', 'action', 'decision', 'end', 'system'"
    )
    next_steps: List[FlowConnection] = Field(
        default_factory=list, description="Connections to next nodes"
    )


class TaskFlow(BaseModel):
    """A complete task flow / user journey."""
    name: str = Field(..., description="Flow name (e.g., 'User Onboarding')")
    description: str = Field(..., description="What this flow covers")
    primary_roles: List[str] = Field(..., description="Primary user roles involved")
    secondary_roles: List[str] = Field(default_factory=list, description="Secondary roles")
    steps: List[FlowStep] = Field(..., description="Ordered list of flow steps/nodes")


class TaskFlowsOutput(BaseModel):
    """AI-generated task flows for the project."""

    flows: List[TaskFlow] = Field(..., description="All user task flows")


# ============================================
# STAGE 5: USER STORIES
# ============================================

class UserStory(BaseModel):
    """A user story in Agile format."""
    id: str = Field(..., description="Story ID like US-001")
    title: str = Field(..., description="Short title")
    as_a: str = Field(..., description="User role (As a...)")
    i_want: str = Field(..., description="Desired action (I want...)")
    so_that: str = Field(..., description="Benefit (So that...)")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    priority: str = Field(default="should", description="must / should / could / wont")
    story_points: int = Field(default=3, description="Estimated story points (1-13)")


class Sprint(BaseModel):
    """A sprint containing user stories."""
    name: str = Field(..., description="Sprint name (e.g., 'Sprint 1')")
    goal: str = Field(..., description="Sprint goal")
    stories: List[UserStory] = Field(..., description="Stories in this sprint")


class Epic(BaseModel):
    """An epic grouping multiple sprints."""
    name: str = Field(..., description="Epic name")
    description: str = Field(..., description="Epic description")
    sprints: List[Sprint] = Field(..., description="Sprints within this epic")


class UserStoriesOutput(BaseModel):
    """AI-generated user stories organized by epics and sprints."""

    epics: List[Epic] = Field(..., description="All epics with sprints and stories")
