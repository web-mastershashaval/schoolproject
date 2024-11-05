from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
import logging

# Set up logging
logger = logging.getLogger(__name__)

def client_required(function):
    @user_passes_test(lambda u: u.groups.filter(name='Clients').exists(), login_url='users:sign-in')
    def wrap(request, *args, **kwargs):
        # Log the user's groups for debugging
        logger.debug(f"User: {request.user.username}, Groups: {[group.name for group in request.user.groups.all()]}")
        
        # Call the original function if the user is in the "Clients" group
        return function(request, *args, **kwargs)
    
    wrap.__name__ = function.__name__
    return wrap
