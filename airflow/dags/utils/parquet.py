import pyarrow as pa

changeset_schema = pa.schema([
    pa.field("id", pa.int64(), bool_nullable=False),
    pa.field("created_at", pa.int64(), bool_nullable=False),
    pa.field("closed_at", pa.int64(), bool_nullable=True),
    pa.field("open", pa.bool_(), bool_nullable=False),
    pa.field("num_changes", pa.int32(), bool_nullable=True),
    pa.field("user", pa.string(), bool_nullable=True),
    pa.field("uid", pa.int32(), bool_nullable=False),
    pa.field("min_lat", pa.float64(), bool_nullable=True),
    pa.field("max_lat", pa.float64(), bool_nullable=True),
    pa.field("min_lon", pa.float64(), bool_nullable=True),
    pa.field("max_lon", pa.float64(), bool_nullable=True),
    pa.field("comments_count", pa.int16(), bool_nullable=False),
    pa.field("created_by", pa.string(), bool_nullable=True),
    pa.field("source", pa.string(), bool_nullable=True),
    pa.field("locale", pa.string(), bool_nullable=True),
    pa.field("bot", pa.string(), bool_nullable=True),
    pa.field("review_requested", pa.string(), bool_nullable=True),
    pa.field("hashtags", pa.string(), bool_nullable=True),
    pa.field("tags", pa.map_(pa.string(), pa.string(), keys_sorted=False), bool_nullable=True),
])
