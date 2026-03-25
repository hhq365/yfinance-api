def safe_get(d, key, default=None):
    try:
        return d.get(key, default)
    except Exception:
        return default
