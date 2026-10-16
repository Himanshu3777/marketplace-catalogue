"""Context processor: inject business stats into Django admin pages."""


def admin_dashboard(request):
    if not request.path.startswith("/admin/"):
        return {}
    if not getattr(request.user, "is_authenticated", False):
        return {}
    if not getattr(request.user, "is_staff", False):
        return {}
    try:
        from .admin_stats import dashboard_stats
        return {"dashboard": dashboard_stats()}
    except Exception:
        return {"dashboard": None}
