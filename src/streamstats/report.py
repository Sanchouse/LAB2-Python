from .analysis import Stats


def build_report(stats: Stats, skips: bool) -> dict:
    """Return a data for reports."""
    if skips:
        return {
        "total_events": stats.total_events,
        "levels": dict(stats.levels),
        "sources": dict(stats.sources),
        "top_error_sources": stats.top_error_sources(),
        "first_timestamp": stats.first_timestamp.isoformat(),
        "last_timestamp": stats.last_timestamp.isoformat(),
        "skipped_invalid": stats.skipped
        }
    else:
        return {
        "total_events": stats.total_events,
        "levels": dict(stats.levels),
        "sources": dict(stats.sources),
        "first_timestamp": stats.first_timestamp.isoformat(),
        "last_timestamp": stats.last_timestamp.isoformat(),
        }