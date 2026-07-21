from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WorkbenchPanelState(BaseModel):
    type: str
    visible: bool


class ToolCatalogEntry(BaseModel):
    key: str
    available: bool


class PinnedTool(BaseModel):
    key: str
    available: bool


class WorkbenchLayoutOut(BaseModel):
    panels: list[WorkbenchPanelState]
    pinned_tools: list[PinnedTool]
    tool_catalog: list[ToolCatalogEntry]


class WorkbenchLayoutUpdate(BaseModel):
    panels: list[WorkbenchPanelState]
    pinned_tools: list[str]


class StorageStats(BaseModel):
    database_bytes: int
    disk_total_bytes: int
    disk_used_bytes: int
    disk_free_bytes: int


class ActivityEntry(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: str
    summary: str
    created_at: datetime


class DashboardNote(BaseModel):
    id: str
    title: str
    color: str
    updated_at: datetime


class WorkbenchData(BaseModel):
    version: str
    storage: StorageStats
    recent_activity: list[ActivityEntry]
    recent_notes: list[DashboardNote]


class WorkbenchOut(BaseModel):
    layout: WorkbenchLayoutOut
    data: WorkbenchData
