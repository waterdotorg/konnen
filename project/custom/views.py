import datetime
import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404

from custom.forms import LocationSubscriptionForm
from custom.models import Location, LocationSubscription
from django.template.context import RequestContext

def homepage(request):
    #TODO: build homepage
    return

@login_required
def location_browse(request):
    locations = Location.active_objects.all()
    location_subscriptions = LocationSubscription.objects.select_related().filter(user=request.user)

    processed_locations = []
    for location in locations:
        location.is_subscribed = False
        for location_subscription in location_subscriptions:
            if location.id == location_subscription.location.id:
                location.is_subscribed = True
                location.email_subscription = location_subscription.email_subscription
                location.phone_subscription = location_subscription.phone_subscription
        processed_locations.append(location)


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
    location = get_object_or_404(Location, slug=slug, status=Location.ACTIVE_STATUS, published_date__lte=datetime.datetime.now())

    return render_to_response('location/location.html',
        {
            'location': location,
        },
        context_instance=RequestContext(request)
    )