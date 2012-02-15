import datetime
import hashlib
import simplejson

from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404

from custom.forms import LocationSubscriptionForm
from custom.models import Location, LocationSubscription, LocationPost
from django.template.context import RequestContext

def homepage(request):
    #TODO: build homepage
    return

@login_required
def location_browse(request):
    location_subscriptions = LocationSubscription.objects.select_related().filter(user=request.user)

    # Set sorting
    sort='uid'
    db_sort_fields = ['title', 'uid']
    if request.GET.get('sort') and request.GET.get('sort') in db_sort_fields:
        sort = request.GET.get('sort')
        if request.GET.get('dir') == 'desc' or not request.GET.get('dir'):
            sort = '-' + sort

    processed_locations = []
    locations = Location.active_objects.all().order_by(sort)
    for location in locations:
        location.is_subscribed = False
        for location_subscription in location_subscriptions:
            if location.id == location_subscription.location.id:
                location.is_subscribed = True
                location.email_subscription = location_subscription.email_subscription
                location.phone_subscription = location_subscription.phone_subscription
        processed_locations.append(location)

    reverse_sort = False
    if request.GET.get('dir') == 'desc' or not request.GET.get('dir'):
        reverse_sort = True
    processed_locations = sorted(processed_locations, key=attrgetter(sort.strip('-')), reverse=reverse_sort)
    processed_locations = sorted(processed_locations, key=attrgetter('is_subscribed'), reverse=True)

    return render_to_response('location/browse.html',
        {
            'locations': processed_locations,
            'location_subscriptions': location_subscriptions,
        },
        context_instance=RequestContext(request)
    )

@login_required
def location_subscribe(request):
    response_data = {}
    response_data['success'] = False
    response_data['errors'] = ''

    if request.method == 'POST' and request.is_ajax():
        data = request.POST
        files = request.FILES
        form = LocationSubscriptionForm(data, files, user=request.user)
        if form.is_valid():
            location = Location.objects.get(id=form.cleaned_data['location_id'])
            if request.POST.get('subscribe') != 'false':
                try:
                    location_subscription = LocationSubscription.objects.get(location=location, user=request.user)
                    location_subscription.email_subscription = form.cleaned_data['email_subscription']
                    location_subscription.phone_subscription = form.cleaned_data['phone_subscription']
                    location_subscription.save()
                except:
                    location_subscription = LocationSubscription(
                        user = request.user,
                        location = location,
                        email_subscription = form.cleaned_data['email_subscription'],
                        phone_subscription = form.cleaned_data['phone_subscription'],
                    )
                    location_subscription.save()
            else:
                try:
                    location_subscription = LocationSubscription.objects.get(location=location, user=request.user)
                    location_subscription.delete()
                except:
                    pass
            response_data['success'] = True
        else:
            response_data['errors'] = dict((k, map(unicode, v)) for (k,v) in form.errors.iteritems())

    return HttpResponse(simplejson.dumps(response_data), mimetype='application/javascript')

@login_required
def location(request, slug=None):
    try:
        location = Location.active_objects.filter(slug=slug)[0]
    except Location.DoesNotExist:
        raise Http404

    location_subscriptions = LocationSubscription.objects.select_related().filter(location=location)
    location_posts = LocationPost.active_objects.filter(location=location)

    try:
        LocationSubscription.objects.get(user=request.user, location=location)
        user_is_subscribed =  True
    except:
        user_is_subscribed = False

    return render_to_response('location/location.html',
        {
            'location': location,
            'location_subscriptions': location_subscriptions,
            'location_posts': location_posts,
            'user_is_subscribed': user_is_subscribed,
            'location_subscription_email_default_value': LocationSubscription.EMAIL_DAILY_FREQ,
        },
        context_instance=RequestContext(request)
    )