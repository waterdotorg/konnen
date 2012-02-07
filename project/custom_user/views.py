from django.shortcuts import render_to_response, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from custom_user.forms import SettingsAccountForm

@login_required()
def settings_account(request):
    profile = request.user.get_profile()

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        settings_account_form = SettingsAccountForm(data, files, user=request.user)
    else:
        initial = {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'mobile': profile.mobile,
            'content': profile.content,
        }
        settings_account_form = SettingsAccountForm(user=request.user, initial=initial)

    if request.method == 'POST' and settings_account_form.is_valid():
        settings_account_form.apply_to_user(files)
        messages.add_message(request, messages.SUCCESS, 'Account settings have been updated.')
        return redirect('settings_account')
    return render_to_response('settings/account.html',
        {
            'form': settings_account_form,
            'profile': profile,
        },
        context_instance=RequestContext(request)
    )

@login_required()
def settings_remove_profile_image(request):
    profile = request.user.get_profile()
    profile.remove_profile_images()
    return redirect('settings_account')