import pyarrow as pa

changeset_schema = pa.schema([
    pa.field("id", pa.int64(), False),
    pa.field("created_at", pa.timestamp(unit="s", tz="+00:00"), False),
    pa.field("closed_at", pa.timestamp(unit="s", tz="+00:00"), True),
    pa.field("open", pa.bool_(), False),
    pa.field("num_changes", pa.int32(), True),
    pa.field("user", pa.string(), True),
    pa.field("uid", pa.int32(), True),
    pa.field("min_lat", pa.float64(), True),
    pa.field("max_lat", pa.float64(), True),
    pa.field("min_lon", pa.float64(), True),
    pa.field("max_lon", pa.float64(), True),
    pa.field("comments_count", pa.int16(), False),
    pa.field("created_by", pa.string(), True),
    pa.field("source", pa.string(), True),
    pa.field("locale", pa.string(), True),
    pa.field("bot", pa.string(), True),
    pa.field("review_requested", pa.string(), True),
    pa.field("hashtags", pa.string(), True),
    pa.field("tags", pa.string(), False),
])
