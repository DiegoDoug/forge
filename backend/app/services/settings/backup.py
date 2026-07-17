"""Export/import a full backup of vault + notes data as a single JSON bundle.

Secret values stay encrypted (PyNaCl ciphertext, base64-encoded) end to end —
a backup file is only useful to someone who also has ``FORGE_MASTER_KEY``.
This deliberately avoids swapping the live SQLite file on disk, which would
race with the running engine's open connections; instead it round-trips
through the same ORM writes normal requests use.
"""

from __future__ import annotations

import base64

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from app.models.base import utcnow
from app.models.note import Note
from app.models.vault import Folder, Secret, SecretTagLink, SecretVersion, Tag

BACKUP_VERSION = 1


def _b64(blob: bytes | None) -> str | None:
    return base64.b64encode(blob).decode("ascii") if blob is not None else None


def _unb64(value: str | None) -> bytes | None:
    return base64.b64decode(value) if value is not None else None


async def export_backup(session: AsyncSession) -> dict:
    folders = (await session.execute(select(Folder))).scalars().all()
    tags = (await session.execute(select(Tag))).scalars().all()
    secrets = (await session.execute(select(Secret))).scalars().all()
    versions = (await session.execute(select(SecretVersion))).scalars().all()
    links = (await session.execute(select(SecretTagLink))).scalars().all()
    notes = (await session.execute(select(Note))).scalars().all()

    versions_by_secret: dict[str, list[SecretVersion]] = {}
    for v in versions:
        versions_by_secret.setdefault(v.secret_id, []).append(v)
    tags_by_secret: dict[str, list[str]] = {}
    for link in links:
        tags_by_secret.setdefault(link.secret_id, []).append(link.tag_id)

    return {
        "version": BACKUP_VERSION,
        "exported_at": utcnow().isoformat(),
        "folders": [{"id": f.id, "name": f.name, "parent_id": f.parent_id} for f in folders],
        "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in tags],
        "secrets": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "folder_id": s.folder_id,
                "favorite": s.favorite,
                "encrypted_value": _b64(s.encrypted_value),
                "encrypted_metadata": _b64(s.encrypted_metadata),
                "tag_ids": tags_by_secret.get(s.id, []),
                "versions": [
                    {"id": v.id, "encrypted_value": _b64(v.encrypted_value), "created_at": v.created_at.isoformat()}
                    for v in versions_by_secret.get(s.id, [])
                ],
            }
            for s in secrets
        ],
        "notes": [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "color": n.color,
                "pos_x": n.pos_x,
                "pos_y": n.pos_y,
                "width": n.width,
                "height": n.height,
                "pinned": n.pinned,
                "archived": n.archived,
            }
            for n in notes
        ],
    }


async def import_backup(session: AsyncSession, bundle: dict) -> dict:
    await session.execute(delete(SecretTagLink))
    await session.execute(delete(SecretVersion))
    await session.execute(delete(Secret))
    await session.execute(delete(Tag))
    await session.execute(delete(Folder))
    await session.execute(delete(Note))

    for f in bundle.get("folders", []):
        session.add(Folder(id=f["id"], name=f["name"], parent_id=f.get("parent_id")))
    for t in bundle.get("tags", []):
        session.add(Tag(id=t["id"], name=t["name"], color=t.get("color", "#6366f1")))
    await session.flush()

    for s in bundle.get("secrets", []):
        secret = Secret(
            id=s["id"],
            name=s["name"],
            type=s["type"],
            folder_id=s.get("folder_id"),
            favorite=s.get("favorite", False),
            encrypted_value=_unb64(s["encrypted_value"]),
            encrypted_metadata=_unb64(s.get("encrypted_metadata")),
        )
        session.add(secret)
        for tag_id in s.get("tag_ids", []):
            session.add(SecretTagLink(secret_id=secret.id, tag_id=tag_id))
        for v in s.get("versions", []):
            session.add(SecretVersion(id=v["id"], secret_id=secret.id, encrypted_value=_unb64(v["encrypted_value"])))

    for n in bundle.get("notes", []):
        session.add(
            Note(
                id=n["id"],
                title=n.get("title", ""),
                content=n.get("content", ""),
                color=n.get("color", "#fde68a"),
                pos_x=n.get("pos_x", 0),
                pos_y=n.get("pos_y", 0),
                width=n.get("width", 280),
                height=n.get("height", 220),
                pinned=n.get("pinned", False),
                archived=n.get("archived", False),
            )
        )

    await session.commit()
    return {
        "folders": len(bundle.get("folders", [])),
        "tags": len(bundle.get("tags", [])),
        "secrets": len(bundle.get("secrets", [])),
        "notes": len(bundle.get("notes", [])),
    }
