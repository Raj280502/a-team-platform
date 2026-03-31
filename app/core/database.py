"""
database.py
-----------
SQLite database for project persistence.
Stores projects, chat messages, and generated files.
"""

import sqlite3
import uuid
import json
import os
from datetime import datetime
from pathlib import Path

# DB file lives alongside generated projects
_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')
DB_PATH = os.path.join(_DB_DIR, 'projects.db')


def _get_conn() -> sqlite3.Connection:
    """Get a connection with row_factory for dict-like access."""
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist. Call once on app startup."""
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                prompt      TEXT NOT NULL DEFAULT '',
                tech_stack  TEXT NOT NULL DEFAULT 'react-flask',
                status      TEXT NOT NULL DEFAULT 'generating',
                file_count  INTEGER NOT NULL DEFAULT 0,
                project_dir TEXT DEFAULT '',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  TEXT NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                msg_type    TEXT NOT NULL DEFAULT 'message',
                created_at  TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS generated_files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  TEXT NOT NULL,
                file_path   TEXT NOT NULL,
                content     TEXT NOT NULL DEFAULT '',
                size        INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sdlc_stages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  TEXT NOT NULL,
                stage_name  TEXT NOT NULL,
                stage_data  TEXT NOT NULL DEFAULT '{}',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, stage_name)
            );

            CREATE TABLE IF NOT EXISTS project_versions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  TEXT NOT NULL,
                version_num INTEGER NOT NULL DEFAULT 1,
                label       TEXT DEFAULT '',
                files_json  TEXT NOT NULL DEFAULT '{}',
                file_count  INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_project
                ON chat_messages(project_id);
            CREATE INDEX IF NOT EXISTS idx_files_project
                ON generated_files(project_id);
            CREATE INDEX IF NOT EXISTS idx_sdlc_project
                ON sdlc_stages(project_id);
            CREATE INDEX IF NOT EXISTS idx_versions_project
                ON project_versions(project_id);
        """)
        conn.commit()
        print("✅ Database initialized:", DB_PATH)
    finally:
        conn.close()


# ============================================
# PROJECT CRUD
# ============================================

def save_project(name: str, prompt: str, tech_stack: str,
                 files: dict, messages: list,
                 project_dir: str = '', status: str = 'complete') -> str:
    """
    Save a new project with its files and chat messages.
    Returns the project_id (UUID).
    """
    project_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO projects (id, name, prompt, tech_stack, status,
               file_count, project_dir, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, name, prompt, tech_stack, status,
             len(files), project_dir, now, now)
        )

        # Save files
        for file_path, content in files.items():
            content_str = content if isinstance(content, str) else str(content)
            conn.execute(
                """INSERT INTO generated_files
                   (project_id, file_path, content, size, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (project_id, file_path, content_str, len(content_str), now)
            )

        # Save messages
        for msg in messages:
            conn.execute(
                """INSERT INTO chat_messages
                   (project_id, role, content, msg_type, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (project_id,
                 msg.get('role', 'system'),
                 msg.get('text', msg.get('content', '')),
                 msg.get('type', msg.get('msg_type', 'message')),
                 msg.get('ts', now) if isinstance(msg.get('ts'), str) else now)
            )

        conn.commit()
        return project_id
    finally:
        conn.close()


def update_project(project_id: str, files: dict = None,
                   status: str = None, name: str = None):
    """Update an existing project's fields and/or files."""
    now = datetime.utcnow().isoformat()
    conn = _get_conn()
    try:
        # Update metadata
        updates = ["updated_at = ?"]
        params = [now]

        if status:
            updates.append("status = ?")
            params.append(status)
        if name:
            updates.append("name = ?")
            params.append(name)
        if files is not None:
            updates.append("file_count = ?")
            params.append(len(files))

        params.append(project_id)
        conn.execute(
            f"UPDATE projects SET {', '.join(updates)} WHERE id = ?",
            params
        )

        # Replace files if provided
        if files is not None:
            conn.execute(
                "DELETE FROM generated_files WHERE project_id = ?",
                (project_id,)
            )
            for file_path, content in files.items():
                content_str = content if isinstance(content, str) else str(content)
                conn.execute(
                    """INSERT INTO generated_files
                       (project_id, file_path, content, size, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (project_id, file_path, content_str, len(content_str), now)
                )

        conn.commit()
    finally:
        conn.close()


def load_project(project_id: str) -> dict | None:
    """
    Load a project with all its files, messages, and SDLC stages.
    Returns: { project: {...}, files: {path: content}, messages: [...], sdlc_stages: {...} }
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()

        if not row:
            return None

        project = dict(row)

        # Load files
        file_rows = conn.execute(
            "SELECT file_path, content FROM generated_files WHERE project_id = ? ORDER BY file_path",
            (project_id,)
        ).fetchall()
        files = {r['file_path']: r['content'] for r in file_rows}

        # Load messages
        msg_rows = conn.execute(
            "SELECT role, content, msg_type, created_at FROM chat_messages WHERE project_id = ? ORDER BY id",
            (project_id,)
        ).fetchall()
        messages = [
            {
                'role': r['role'],
                'text': r['content'],
                'type': r['msg_type'],
                'ts': r['created_at'],
            }
            for r in msg_rows
        ]

        # Load SDLC stages
        sdlc_rows = conn.execute(
            "SELECT stage_name, stage_data FROM sdlc_stages WHERE project_id = ?",
            (project_id,)
        ).fetchall()
        sdlc_stages = {}
        for r in sdlc_rows:
            try:
                sdlc_stages[r['stage_name']] = json.loads(r['stage_data'])
            except json.JSONDecodeError:
                sdlc_stages[r['stage_name']] = {}

        return {
            'project': project,
            'files': files,
            'messages': messages,
            'sdlc_stages': sdlc_stages,
        }
    finally:
        conn.close()


def list_projects() -> list:
    """List all projects (metadata only, no file contents)."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """SELECT id, name, prompt, tech_stack, status,
                      file_count, created_at, updated_at
               FROM projects ORDER BY created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_project(project_id: str) -> bool:
    """Delete a project and all its files/messages (CASCADE)."""
    conn = _get_conn()
    try:
        cursor = conn.execute(
            "DELETE FROM projects WHERE id = ?", (project_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def save_message(project_id: str, role: str, content: str,
                 msg_type: str = 'message'):
    """Save a single chat message for a project."""
    now = datetime.utcnow().isoformat()
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO chat_messages
               (project_id, role, content, msg_type, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, role, content, msg_type, now)
        )
        conn.commit()
    finally:
        conn.close()


def get_messages(project_id: str) -> list:
    """Get all chat messages for a project."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """SELECT role, content, msg_type, created_at
               FROM chat_messages WHERE project_id = ? ORDER BY id""",
            (project_id,)
        ).fetchall()
        return [
            {
                'role': r['role'],
                'text': r['content'],
                'type': r['msg_type'],
                'ts': r['created_at'],
            }
            for r in rows
        ]
    finally:
        conn.close()


# ============================================
# SDLC STAGE PERSISTENCE
# ============================================

def save_sdlc_stage(project_id: str, stage_name: str, stage_data: dict):
    """Save or update SDLC stage data for a project."""
    now = datetime.utcnow().isoformat()
    data_json = json.dumps(stage_data, default=str)
    conn = _get_conn()
    try:
        conn.execute(
            """INSERT INTO sdlc_stages (project_id, stage_name, stage_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(project_id, stage_name)
               DO UPDATE SET stage_data = ?, updated_at = ?""",
            (project_id, stage_name, data_json, now, now, data_json, now)
        )
        conn.commit()
    finally:
        conn.close()


def load_sdlc_stages(project_id: str) -> dict:
    """Load all SDLC stages for a project. Returns { stage_name: data_dict }."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT stage_name, stage_data FROM sdlc_stages WHERE project_id = ?",
            (project_id,)
        ).fetchall()
        stages = {}
        for r in rows:
            try:
                stages[r['stage_name']] = json.loads(r['stage_data'])
            except json.JSONDecodeError:
                stages[r['stage_name']] = {}
        return stages
    finally:
        conn.close()


# ============================================
# PROJECT VERSION HISTORY
# ============================================

def save_version(project_id: str, files: dict, label: str = '') -> int:
    """
    Save a snapshot of the current files as a version.
    Returns the version number.
    """
    now = datetime.utcnow().isoformat()
    conn = _get_conn()
    try:
        # Get next version number
        row = conn.execute(
            "SELECT COALESCE(MAX(version_num), 0) + 1 AS next_ver FROM project_versions WHERE project_id = ?",
            (project_id,)
        ).fetchone()
        ver = row['next_ver']

        files_json = json.dumps(files, default=str)
        conn.execute(
            """INSERT INTO project_versions
               (project_id, version_num, label, files_json, file_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (project_id, ver, label or f"Version {ver}", files_json, len(files), now)
        )
        conn.commit()
        return ver
    finally:
        conn.close()


def list_versions(project_id: str) -> list:
    """List all versions for a project (metadata, no file contents)."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """SELECT id, version_num, label, file_count, created_at
               FROM project_versions WHERE project_id = ?
               ORDER BY version_num DESC""",
            (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def restore_version(project_id: str, version_num: int) -> dict | None:
    """
    Restore files from a specific version.
    Also saves current files as a new version before restoring.
    Returns the restored files dict or None if not found.
    """
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT files_json FROM project_versions WHERE project_id = ? AND version_num = ?",
            (project_id, version_num)
        ).fetchone()

        if not row:
            return None

        restored_files = json.loads(row['files_json'])

        # Update the project's current files
        update_project(project_id, files=restored_files)

        return restored_files
    finally:
        conn.close()


def load_sdlc_stages(project_id: str) -> dict:
    """
    Load all SDLC stage records for a project.
    Returns a dict like {'overview': {...}, 'requirements': {...}, ...}
    or an empty dict if no stages are saved yet.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT stage_name, stage_data FROM sdlc_stages WHERE project_id = ?",
            (project_id,)
        ).fetchall()
        result = {}
        for row in rows:
            try:
                result[row['stage_name']] = json.loads(row['stage_data'])
            except (json.JSONDecodeError, TypeError):
                result[row['stage_name']] = None
        return result
    finally:
        conn.close()


def save_sdlc_stage(project_id: str, stage_name: str, stage_data: dict) -> None:
    """
    Save (or update) a single SDLC stage record for a project.
    Uses UPSERT so calling it multiple times is safe.
    """
    conn = _get_conn()
    now = datetime.utcnow().isoformat()
    try:
        conn.execute(
            """INSERT INTO sdlc_stages (project_id, stage_name, stage_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(project_id, stage_name) DO UPDATE SET
                 stage_data = excluded.stage_data,
                 updated_at = excluded.updated_at""",
            (project_id, stage_name, json.dumps(stage_data, default=str), now, now)
        )
        conn.commit()
    finally:
        conn.close()



