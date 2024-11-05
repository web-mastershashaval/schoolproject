from django.shortcuts import redirect
from django.contrib import messages
def lawyer_selected_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'selected_lawyer' not in request.session:
            messages.warning(request, 'You must select a lawyer before accessing this page.')
            return redirect('users:dashboard')  # Redirect to the user's dashboard or any other page
        return view_func(request, *args, **kwargs)
    return _wrapped_view