from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AuthDep, SessionDep
from app.schemas.knowledge import (
    KnowledgeItemOut,
    KnowledgeItemType,
    KnowledgeLinkCreateIn,
    KnowledgeLinkOtherOut,
    KnowledgeLinkOut,
    KnowledgeListOut,
    KnowledgeTagAssignIn,
    KnowledgeTagOut,
)
from app.schemas.secrets import TagOut
from app.services.knowledge import service

router = APIRouter(prefix="/knowledge", tags=["knowledge"], dependencies=[AuthDep])


@router.get("", response_model=KnowledgeListOut)
async def list_knowledge(
    session: SessionDep,
    q: str = "",
    type: KnowledgeItemType | str = "all",
    tag_id: Annotated[list[str] | None, Query()] = None,
    project_id: str | None = None,
) -> KnowledgeListOut:
    item_type = type.value if isinstance(type, KnowledgeItemType) else type
    items, total, truncated = await service.list_knowledge(
        session, q=q, item_type=item_type, tag_ids=tag_id, project_id=project_id
    )
    return KnowledgeListOut(
        items=[
            KnowledgeItemOut(
                type=item.type,
                id=item.id,
                title=item.title,
                excerpt=item.excerpt,
                tags=[TagOut(id=t.id, name=t.name, color=t.color) for t in item.tags],
                project_id=item.project_id,
                updated_at=item.updated_at,
            )
            for item in items
        ],
        total=total,
        truncated=truncated,
    )


@router.get("/tags", response_model=list[KnowledgeTagOut])
async def list_knowledge_tags(session: SessionDep) -> list[KnowledgeTagOut]:
    pairs = await service.list_knowledge_tags(session)
    return [KnowledgeTagOut(id=tag.id, name=tag.name, color=tag.color, count=count) for tag, count in pairs]


@router.post("/{item_type}/{item_id}/tags", response_model=list[TagOut])
async def add_tag(item_type: KnowledgeItemType, item_id: str, body: KnowledgeTagAssignIn, session: SessionDep) -> list[TagOut]:
    tags = await service.add_tag(
        session, item_type.value, item_id, tag_id=body.tag_id, name=body.name, color=body.color
    )
    return [TagOut(id=t.id, name=t.name, color=t.color) for t in tags]


@router.delete("/{item_type}/{item_id}/tags/{tag_id}", status_code=204)
async def remove_tag(item_type: KnowledgeItemType, item_id: str, tag_id: str, session: SessionDep) -> None:
    await service.remove_tag(session, item_type.value, item_id, tag_id)


@router.get("/{item_type}/{item_id}/links", response_model=list[KnowledgeLinkOut])
async def list_links(item_type: KnowledgeItemType, item_id: str, session: SessionDep) -> list[KnowledgeLinkOut]:
    links = await service.list_links(session, item_type.value, item_id)
    return [
        KnowledgeLinkOut(
            link_id=link.link_id,
            other=KnowledgeLinkOtherOut(type=link.other_type, id=link.other_id, title=link.other_title),
            created_at=link.created_at,
        )
        for link in links
    ]


@router.post("/{item_type}/{item_id}/links", response_model=KnowledgeLinkOut, status_code=201)
async def create_link(item_type: KnowledgeItemType, item_id: str, body: KnowledgeLinkCreateIn, session: SessionDep) -> KnowledgeLinkOut:
    link = await service.create_link(session, item_type.value, item_id, body.target_type.value, body.target_id)
    return KnowledgeLinkOut(
        link_id=link.link_id,
        other=KnowledgeLinkOtherOut(type=link.other_type, id=link.other_id, title=link.other_title),
        created_at=link.created_at,
    )


@router.delete("/links/{link_id}", status_code=204)
async def delete_link(link_id: str, session: SessionDep) -> None:
    await service.delete_link(session, link_id)
