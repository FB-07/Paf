from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or (hasattr(request.user, "usersprofile") and request.user.usersprofile.tipo_utilizador == "admin"):
                return view_func(request, *args, **kwargs)
        return redirect("mainpage")
    return _wrapped_view