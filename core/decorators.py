from django.shortcuts import redirect

def user_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('/admin-panel/')
        return view_func(request, *args, **kwargs)
    return wrapper