from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def lawyer_required(function):
    @user_passes_test(lambda u: u.groups.filter(name='Lawyers').exists(), login_url='users:home')
    def wrap(request, *args, **kwargs):
        # Check if the user is in the Lawyers group
        if not request.user.groups.filter(name='Lawyers').exists():
            raise PermissionDenied
        return function(request, *args, **kwargs)
    
    wrap.__name__ = function.__name__
    return wrap
