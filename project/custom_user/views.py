from django.shortcuts import render_to_response, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.context import RequestContext

from custom.models import LocationPost
from custom_user.forms import SettingsAccountForm
from custom_user.models import Profile

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

@login_required()
def member_account(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    location_posts = LocationPost.active_objects.select_related().filter(user=user).order_by('-published_date')
    locations_served = []
    for location_post in location_posts:
        if location_post.location not in locations_served:
            locations_served.append(location_post.location)

    return render_to_response('member/profile.html',
        {
            'user': user,
            'profile': profile,
            'location_posts': location_posts,
            'locations_served': locations_served,
        },
        context_instance=RequestContext(request)
    )