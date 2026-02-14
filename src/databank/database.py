"""
DataBank — Centralized PostgreSQL database for all extracted TikTok data.

Uses asyncpg for high-performance async PostgreSQL access with connection pooling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich import print
from rich.text import Text

from .models import CREATE_TABLES_SQL
from .models import TABLE_CONFIGS

if TYPE_CHECKING:
    from typing import Any

__all__ = ["DataBank"]

DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5444/tiktok_databank"


class DataBank:
    """Centralized PostgreSQL database for all extracted data."""

    def __init__(self, dsn: str = DEFAULT_DSN):
        self.dsn = dsn
        self.pool = None
        self._enabled = True

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self) -> bool:
        """Create connection pool and initialize all tables.

        Returns True if successful, False otherwise.
        """
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=10,
            )
            async with self.pool.acquire() as conn:
                await conn.execute(CREATE_TABLES_SQL)
            print(
                Text("Data Bank initialized successfully", style="bold green")
            )
            return True
        except Exception as e:
            print(
                Text(
                    f"Data Bank initialization failed: {e}",
                    style="bold red",
                )
            )
            self._enabled = False
            return False

    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None

    @property
    def is_available(self) -> bool:
        """Check if the data bank is ready to use."""
        return self._enabled and self.pool is not None

    # ========================================================================
    # Generic save methods
    # ========================================================================

    async def save(
        self,
        data: list | tuple,
        type_: str = "detail",
    ) -> bool:
        """Save extracted data to the data bank.

        Args:
            data: List/tuple of values in the same order as RecordManager fields.
            type_: Data type key (detail, comment, user, mix, search_general,
                   search_user, search_live, hot).

        Returns:
            True if saved successfully, False otherwise.
        """
        if not self.is_available:
            return False

        config = TABLE_CONFIGS.get(type_)
        if not config:
            return False

        try:
            table = config["table"]
            fields = config["fields"]
            source_type = config["source_type"]

            # Build field -> value mapping from positional data
            values = {}
            for i, field in enumerate(fields):
                if i < len(data):
                    values[field] = data[i]

            # Add source_type
            values["source_type"] = source_type

            # Coerce types for PostgreSQL INTEGER columns
            self._coerce_types(table, values)

            await self._upsert(table, values, type_)
            return True
        except Exception as e:
            print(
                Text(
                    f"Data Bank save error ({type_}): {e}",
                    style="bold red",
                )
            )
            return False

    # Known INTEGER columns per table
    _INTEGER_COLUMNS = {
        "contents": {
            "height", "width", "digg_count", "comment_count",
            "collect_count", "share_count", "play_count", "user_age",
        },
        "comments": {
            "digg_count", "reply_comment_total", "user_age",
        },
        "users": {
            "user_age", "aweme_count", "total_favorited",
            "favoriting_count", "follower_count", "following_count",
            "max_follower_count",
        },
        "search_users": {
            "follower_count", "total_favorited",
        },
        "hot_trends": {
            "position", "hot_value", "view_count", "video_count",
        },
    }

    def _coerce_types(self, table: str, values: dict) -> None:
        """Convert string values to int for known INTEGER columns."""
        int_cols = self._INTEGER_COLUMNS.get(table, set())
        for col in int_cols:
            if col in values and values[col] is not None:
                try:
                    values[col] = int(values[col])
                except (ValueError, TypeError):
                    values[col] = 0

    async def save_batch(
        self,
        items: list[list | tuple],
        type_: str = "detail",
    ) -> int:
        """Save multiple records in batch.

        Returns the number of successfully saved records.
        """
        if not self.is_available:
            return 0

        saved = 0
        for data in items:
            if await self.save(data, type_):
                saved += 1
        return saved

    # ========================================================================
    # Upsert logic
    # ========================================================================

    async def _upsert(
        self,
        table: str,
        values: dict[str, Any],
        type_: str,
    ):
        """Insert or update a record using ON CONFLICT."""
        # Remove None keys
        clean_values = {
            k: v for k, v in values.items() if v is not None
        }

        columns = list(clean_values.keys())
        placeholders = [f"${i + 1}" for i in range(len(columns))]
        params = list(clean_values.values())

        # Quote reserved words
        quoted_columns = [
            f'"{c}"' if c in ("desc", "text", "type", "user") else c
            for c in columns
        ]

        # Get the unique constraint column(s) for ON CONFLICT
        conflict_target = self._get_conflict_target(table)

        if conflict_target:
            # Build SET clause for update (exclude unique key columns)
            conflict_cols = conflict_target.split(", ")
            update_cols = [
                c for c, qc in zip(columns, quoted_columns)
                if c not in conflict_cols
            ]
            update_quoted = [
                f'"{c}"' if c in ("desc", "text", "type", "user") else c
                for c in update_cols
            ]
            set_clause = ", ".join(
                f"{qc} = EXCLUDED.{qc}"
                for qc in update_quoted
            )

            sql = (
                f"INSERT INTO {table} ({', '.join(quoted_columns)}) "
                f"VALUES ({', '.join(placeholders)}) "
                f"ON CONFLICT ({conflict_target}) "
                f"DO UPDATE SET {set_clause}"
            )
        else:
            sql = (
                f"INSERT INTO {table} ({', '.join(quoted_columns)}) "
                f"VALUES ({', '.join(placeholders)})"
            )

        async with self.pool.acquire() as conn:
            await conn.execute(sql, *params)

    @staticmethod
    def _get_conflict_target(table: str) -> str | None:
        """Return the unique constraint columns for a table."""
        targets = {
            "contents": "id, source_type",
            "comments": "cid",
            "users": "uid",
            "search_users": "uid",
            "search_lives": "room_id",
            "hot_trends": "sentence_id, event_time",
        }
        return targets.get(table)

    # ========================================================================
    # Query methods
    # ========================================================================

    async def query(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at DESC",
    ) -> list[dict]:
        """Query data from a table with optional filters.

        Args:
            table: Table name (contents, comments, users, etc.)
            filters: Dict of column -> value for WHERE conditions.
            limit: Max number of rows.
            offset: Offset for pagination.
            order_by: ORDER BY clause.

        Returns:
            List of dicts, one per row.
        """
        if not self.is_available:
            return []

        where_parts = []
        params = []
        idx = 1

        if filters:
            for col, val in filters.items():
                quoted_col = (
                    f'"{col}"'
                    if col in ("desc", "text", "type", "user")
                    else col
                )
                where_parts.append(f"{quoted_col} = ${idx}")
                params.append(val)
                idx += 1

        where_clause = (
            "WHERE " + " AND ".join(where_parts) if where_parts else ""
        )

        sql = (
            f"SELECT * FROM {table} {where_clause} "
            f"ORDER BY {order_by} "
            f"LIMIT ${idx} OFFSET ${idx + 1}"
        )
        params.extend([limit, offset])

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [dict(row) for row in rows]

    async def count(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """Count rows in a table with optional filters."""
        if not self.is_available:
            return 0

        where_parts = []
        params = []
        idx = 1

        if filters:
            for col, val in filters.items():
                quoted_col = (
                    f'"{col}"'
                    if col in ("desc", "text", "type", "user")
                    else col
                )
                where_parts.append(f"{quoted_col} = ${idx}")
                params.append(val)
                idx += 1

        where_clause = (
            "WHERE " + " AND ".join(where_parts) if where_parts else ""
        )

        sql = f"SELECT COUNT(*) FROM {table} {where_clause}"

        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql, *params)

    async def get_statistics(self) -> dict[str, int]:
        """Get row counts for all tables.

        Returns:
            Dict of table_name -> count.
        """
        if not self.is_available:
            return {}

        tables = [
            "contents", "comments", "users",
            "search_users", "search_lives", "hot_trends",
        ]
        stats = {}
        async with self.pool.acquire() as conn:
            for table in tables:
                count = await conn.fetchval(
                    f"SELECT COUNT(*) FROM {table}"
                )
                stats[table] = count
        return stats

    async def get_all_data(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        order_by: str = "created_at DESC",
    ) -> list[dict]:
        """Get all data from a table (no limit). Use with caution."""
        if not self.is_available:
            return []

        where_parts = []
        params = []
        idx = 1

        if filters:
            for col, val in filters.items():
                quoted_col = (
                    f'"{col}"'
                    if col in ("desc", "text", "type", "user")
                    else col
                )
                where_parts.append(f"{quoted_col} = ${idx}")
                params.append(val)
                idx += 1

        where_clause = (
            "WHERE " + " AND ".join(where_parts) if where_parts else ""
        )

        sql = f"SELECT * FROM {table} {where_clause} ORDER BY {order_by}"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [dict(row) for row in rows]
