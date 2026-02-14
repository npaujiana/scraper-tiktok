"""
PostgreSQL table definitions for the Data Bank.

Schema derived from RecordManager field definitions in src/storage/manager.py.
Each table mirrors the existing data schemas with additional metadata columns.
"""

__all__ = ["CREATE_TABLES_SQL", "TABLE_CONFIGS"]

# ============================================================================
# CREATE TABLE SQL statements
# ============================================================================

CREATE_CONTENTS_TABLE = """
CREATE TABLE IF NOT EXISTS contents (
    pk_id           SERIAL PRIMARY KEY,
    source_type     VARCHAR(50) NOT NULL DEFAULT 'detail',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Content fields (from RecordManager.detail)
    type            TEXT,
    collection_time TEXT,
    uid             TEXT,
    sec_uid         TEXT,
    unique_id       TEXT,
    id              TEXT,
    "desc"          TEXT,
    text_extra      TEXT,
    duration        TEXT,
    height          INTEGER,
    width           INTEGER,
    share_url       TEXT,
    create_time     TEXT,
    uri             TEXT,
    nickname        TEXT,
    user_age        INTEGER,
    signature       TEXT,
    downloads       TEXT,
    music_author    TEXT,
    music_title     TEXT,
    music_url       TEXT,
    static_cover    TEXT,
    dynamic_cover   TEXT,
    tag             TEXT,
    digg_count      INTEGER DEFAULT 0,
    comment_count   INTEGER DEFAULT 0,
    collect_count   INTEGER DEFAULT 0,
    share_count     INTEGER DEFAULT 0,
    play_count      INTEGER DEFAULT 0,
    extra           TEXT,

    -- Extra metadata
    extra_data      JSONB,

    CONSTRAINT uq_contents_id UNIQUE (id, source_type)
);
"""

CREATE_COMMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS comments (
    pk_id               SERIAL PRIMARY KEY,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'comment',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Comment fields (from RecordManager.comment)
    collection_time     TEXT,
    cid                 TEXT,
    create_time         TEXT,
    uid                 TEXT,
    sec_uid             TEXT,
    nickname            TEXT,
    signature           TEXT,
    user_age            INTEGER,
    ip_label            TEXT,
    text                TEXT,
    sticker             TEXT,
    image               TEXT,
    digg_count          INTEGER DEFAULT 0,
    reply_comment_total INTEGER DEFAULT 0,
    reply_id            TEXT,
    reply_to_reply_id   TEXT,

    extra_data          JSONB,

    CONSTRAINT uq_comments_cid UNIQUE (cid)
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    pk_id               SERIAL PRIMARY KEY,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- User fields (from RecordManager.user)
    collection_time     TEXT,
    nickname            TEXT,
    url                 TEXT,
    signature           TEXT,
    unique_id           TEXT,
    user_age            INTEGER,
    gender              TEXT,
    country             TEXT,
    province            TEXT,
    city                TEXT,
    district            TEXT,
    ip_location         TEXT,
    verify              TEXT,
    enterprise          TEXT,
    sec_uid             TEXT,
    uid                 TEXT,
    short_id            TEXT,
    avatar              TEXT,
    cover               TEXT,
    aweme_count         INTEGER DEFAULT 0,
    total_favorited     INTEGER DEFAULT 0,
    favoriting_count    INTEGER DEFAULT 0,
    follower_count      INTEGER DEFAULT 0,
    following_count     INTEGER DEFAULT 0,
    max_follower_count  INTEGER DEFAULT 0,

    extra_data          JSONB,

    CONSTRAINT uq_users_uid UNIQUE (uid)
);
"""

CREATE_SEARCH_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS search_users (
    pk_id               SERIAL PRIMARY KEY,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'search_user',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Search user fields (from RecordManager.search_user)
    collection_time     TEXT,
    uid                 TEXT,
    sec_uid             TEXT,
    nickname            TEXT,
    unique_id           TEXT,
    short_id            TEXT,
    avatar              TEXT,
    signature           TEXT,
    verify              TEXT,
    enterprise          TEXT,
    follower_count      INTEGER DEFAULT 0,
    total_favorited     INTEGER DEFAULT 0,

    extra_data          JSONB,

    CONSTRAINT uq_search_users_uid UNIQUE (uid)
);
"""

CREATE_SEARCH_LIVES_TABLE = """
CREATE TABLE IF NOT EXISTS search_lives (
    pk_id               SERIAL PRIMARY KEY,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'search_live',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Search live fields (from RecordManager.search_live)
    collection_time     TEXT,
    room_id             TEXT,
    uid                 TEXT,
    sec_uid             TEXT,
    nickname            TEXT,
    short_id            TEXT,
    avatar              TEXT,
    signature           TEXT,
    verify              TEXT,
    enterprise          TEXT,

    extra_data          JSONB,

    CONSTRAINT uq_search_lives_room_id UNIQUE (room_id)
);
"""

CREATE_HOT_TRENDS_TABLE = """
CREATE TABLE IF NOT EXISTS hot_trends (
    pk_id               SERIAL PRIMARY KEY,
    source_type         VARCHAR(50) NOT NULL DEFAULT 'hot',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Hot trend fields (from RecordManager.hot)
    position            INTEGER,
    word                TEXT,
    hot_value           INTEGER DEFAULT 0,
    cover               TEXT,
    event_time          TEXT,
    view_count          INTEGER DEFAULT 0,
    video_count         INTEGER DEFAULT 0,
    sentence_id         TEXT,

    extra_data          JSONB,

    CONSTRAINT uq_hot_trends_sentence UNIQUE (sentence_id, event_time)
);
"""

# Create indexes for common query patterns
CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_contents_uid ON contents (uid);
CREATE INDEX IF NOT EXISTS idx_contents_nickname ON contents (nickname);
CREATE INDEX IF NOT EXISTS idx_contents_create_time ON contents (create_time);
CREATE INDEX IF NOT EXISTS idx_contents_source_type ON contents (source_type);
CREATE INDEX IF NOT EXISTS idx_contents_created_at ON contents (created_at);
CREATE INDEX IF NOT EXISTS idx_comments_uid ON comments (uid);
CREATE INDEX IF NOT EXISTS idx_comments_create_time ON comments (create_time);
CREATE INDEX IF NOT EXISTS idx_users_nickname ON users (nickname);
CREATE INDEX IF NOT EXISTS idx_users_uid ON users (uid);
CREATE INDEX IF NOT EXISTS idx_hot_trends_event_time ON hot_trends (event_time);
"""

# Combined SQL for initialization
CREATE_TABLES_SQL = "\n".join([
    CREATE_CONTENTS_TABLE,
    CREATE_COMMENTS_TABLE,
    CREATE_USERS_TABLE,
    CREATE_SEARCH_USERS_TABLE,
    CREATE_SEARCH_LIVES_TABLE,
    CREATE_HOT_TRENDS_TABLE,
    CREATE_INDEXES,
])

# ============================================================================
# Table configuration mapping
# Maps data type -> (table_name, field_keys, unique_field)
# field_keys order must match RecordManager field order
# ============================================================================

TABLE_CONFIGS = {
    "detail": {
        "table": "contents",
        "fields": [
            "type", "collection_time", "uid", "sec_uid", "unique_id", "id",
            "desc", "text_extra", "duration", "height", "width", "share_url",
            "create_time", "uri", "nickname", "user_age", "signature",
            "downloads", "music_author", "music_title", "music_url",
            "static_cover", "dynamic_cover", "tag", "digg_count",
            "comment_count", "collect_count", "share_count", "play_count",
            "extra",
        ],
        "source_type": "detail",
    },
    "mix": {
        "table": "contents",
        "fields": [
            "type", "collection_time", "uid", "sec_uid", "unique_id", "id",
            "desc", "text_extra", "duration", "height", "width", "share_url",
            "create_time", "uri", "nickname", "user_age", "signature",
            "downloads", "music_author", "music_title", "music_url",
            "static_cover", "dynamic_cover", "tag", "digg_count",
            "comment_count", "collect_count", "share_count", "play_count",
            "extra",
        ],
        "source_type": "mix",
    },
    "search_general": {
        "table": "contents",
        "fields": [
            "type", "collection_time", "uid", "sec_uid", "unique_id", "id",
            "desc", "text_extra", "duration", "height", "width", "share_url",
            "create_time", "uri", "nickname", "user_age", "signature",
            "downloads", "music_author", "music_title", "music_url",
            "static_cover", "dynamic_cover", "tag", "digg_count",
            "comment_count", "collect_count", "share_count", "play_count",
            "extra",
        ],
        "source_type": "search_general",
    },
    "comment": {
        "table": "comments",
        "fields": [
            "collection_time", "cid", "create_time", "uid", "sec_uid",
            "nickname", "signature", "user_age", "ip_label", "text",
            "sticker", "image", "digg_count", "reply_comment_total",
            "reply_id", "reply_to_reply_id",
        ],
        "source_type": "comment",
    },
    "user": {
        "table": "users",
        "fields": [
            "collection_time", "nickname", "url", "signature", "unique_id",
            "user_age", "gender", "country", "province", "city", "district",
            "ip_location", "verify", "enterprise", "sec_uid", "uid",
            "short_id", "avatar", "cover", "aweme_count", "total_favorited",
            "favoriting_count", "follower_count", "following_count",
            "max_follower_count",
        ],
        "source_type": "user",
    },
    "search_user": {
        "table": "search_users",
        "fields": [
            "collection_time", "uid", "sec_uid", "nickname", "unique_id",
            "short_id", "avatar", "signature", "verify", "enterprise",
            "follower_count", "total_favorited",
        ],
        "source_type": "search_user",
    },
    "search_live": {
        "table": "search_lives",
        "fields": [
            "collection_time", "room_id", "uid", "sec_uid", "nickname",
            "short_id", "avatar", "signature", "verify", "enterprise",
        ],
        "source_type": "search_live",
    },
    "hot": {
        "table": "hot_trends",
        "fields": [
            "position", "word", "hot_value", "cover", "event_time",
            "view_count", "video_count", "sentence_id",
        ],
        "source_type": "hot",
    },
}

# Human-readable column names for Excel export headers
COLUMN_LABELS = {
    "contents": {
        "pk_id": "ID",
        "source_type": "Source Type",
        "created_at": "Saved At",
        "type": "Content Type",
        "collection_time": "Collection Time",
        "uid": "UID",
        "sec_uid": "SEC_UID",
        "unique_id": "Account ID",
        "id": "Content ID",
        "desc": "Description",
        "text_extra": "Topics/Tags",
        "duration": "Duration",
        "height": "Height",
        "width": "Width",
        "share_url": "Share URL",
        "create_time": "Publish Time",
        "uri": "Video URI",
        "nickname": "Nickname",
        "user_age": "Age",
        "signature": "Bio",
        "downloads": "Download URL",
        "music_author": "Music Author",
        "music_title": "Music Title",
        "music_url": "Music URL",
        "static_cover": "Static Cover",
        "dynamic_cover": "Dynamic Cover",
        "tag": "Hidden Tags",
        "digg_count": "Likes",
        "comment_count": "Comments",
        "collect_count": "Favorites",
        "share_count": "Shares",
        "play_count": "Plays",
        "extra": "Extra Info",
    },
    "comments": {
        "pk_id": "ID",
        "source_type": "Source Type",
        "created_at": "Saved At",
        "collection_time": "Collection Time",
        "cid": "Comment ID",
        "create_time": "Comment Time",
        "uid": "UID",
        "sec_uid": "SEC_UID",
        "nickname": "Nickname",
        "signature": "Bio",
        "user_age": "Age",
        "ip_label": "IP Location",
        "text": "Comment Text",
        "sticker": "Sticker",
        "image": "Image",
        "digg_count": "Likes",
        "reply_comment_total": "Replies",
        "reply_id": "Reply ID",
        "reply_to_reply_id": "Reply To",
    },
    "users": {
        "pk_id": "ID",
        "source_type": "Source Type",
        "created_at": "Saved At",
        "collection_time": "Collection Time",
        "nickname": "Nickname",
        "url": "Profile URL",
        "signature": "Bio",
        "unique_id": "Account ID",
        "user_age": "Age",
        "gender": "Gender",
        "country": "Country",
        "province": "Province",
        "city": "City",
        "district": "District",
        "ip_location": "IP Location",
        "verify": "Verification",
        "enterprise": "Enterprise",
        "sec_uid": "SEC_UID",
        "uid": "UID",
        "short_id": "SHORT_ID",
        "avatar": "Avatar URL",
        "cover": "Cover URL",
        "aweme_count": "Posts",
        "total_favorited": "Total Likes",
        "favoriting_count": "Favorites Given",
        "follower_count": "Followers",
        "following_count": "Following",
        "max_follower_count": "Max Followers",
    },
    "search_users": {
        "pk_id": "ID",
        "source_type": "Source Type",
        "created_at": "Saved At",
        "collection_time": "Collection Time",
        "uid": "UID",
        "sec_uid": "SEC_UID",
        "nickname": "Nickname",
        "unique_id": "Account ID",
        "short_id": "SHORT_ID",
        "avatar": "Avatar URL",
        "signature": "Bio",
        "verify": "Verification",
        "enterprise": "Enterprise",
        "follower_count": "Followers",
        "total_favorited": "Total Likes",
    },
    "search_lives": {
        "pk_id": "ID",
        "source_type": "Source Type",
        "created_at": "Saved At",
        "collection_time": "Collection Time",
        "room_id": "Room ID",
        "uid": "UID",
        "sec_uid": "SEC_UID",
        "nickname": "Nickname",
        "short_id": "SHORT_ID",
        "avatar": "Avatar URL",
        "signature": "Bio",
        "verify": "Verification",
        "enterprise": "Enterprise",
    },
    "hot_trends": {
        "pk_id": "ID",
        "source_type": "Source Type",
        "created_at": "Saved At",
        "position": "Rank",
        "word": "Content",
        "hot_value": "Hot Value",
        "cover": "Cover",
        "event_time": "Event Time",
        "view_count": "Views",
        "video_count": "Videos",
        "sentence_id": "Sentence ID",
    },
}
