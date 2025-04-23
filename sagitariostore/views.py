from django.shortcuts import render

def terms_view(request):
    """Vista para mostrar los términos y condiciones."""
    return render(request, 'terms.html')

def privacy_policy_view(request):
    """Vista para mostrar la política de privacidad."""
    return render(request, 'privacy.html')