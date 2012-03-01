import re
import simplejson

from decimal import Decimal
from operator import attrgetter

from django.db.models import Avg
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.cache import cache
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext

from custom.forms import LocationSubscriptionForm
from custom.models import Location, LocationSubscription, LocationPost, WaterSourceType, \
    Community, Provider
from custom.utils import locations_chlorine_level_filter, locations_water_source_type_filter, \
    locations_provider_filter


def homepage(request):
    locations = Location.active_objects.filter(latitude__isnull=False, longitude__isnull=False)
    water_source_types = WaterSourceType.objects.all().order_by('title')
    communities = Community.objects.all().order_by('title')
    providers = Provider.objects.all().order_by('title')
    current_site = get_current_site(request)

    return render_to_response('homepage.html',
        {
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'locations': locations,
            'water_source_types': water_source_types,
            'communities': communities,
            'current_site': current_site,
            'providers': providers,
        },
        context_instance=RequestContext(request)
    )

def homepage_kml(request):
    user_is_authenticated = False
    if request.GET.get('auth', False) and request.GET.get('auth') == 'True':
        user_is_authenticated = True

    filter_kwargs = {}
    request_get_keys = request.GET.keys()

    location_ids=[]
    if request.GET.has_key('my_subscribed_locations') and user_is_authenticated and request.GET.get('ruid'):
        location_subscriptions = LocationSubscription.objects.filter(user=request.GET.get('ruid'))
        for ls in location_subscriptions:
            try:
                location_ids.append(ls.location_id)
            except:
                pass
        filter_kwargs['id__in'] = location_ids

    community_ids = []
    if 'community_' in (',').join(request_get_keys):
        for key in request_get_keys:
            if 'community_' in key:
                try:
                    community_ids.append(int(key.strip('community_')))
                except:
                    pass
        filter_kwargs['community__in'] = community_ids

    locations = Location.active_objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        **filter_kwargs
    ).extra(
        select={
            'chlorine_level': """SELECT custom_locationpost.chlorine_level
                              FROM custom_locationpost
                              WHERE custom_location.id = custom_locationpost.location_id
                              AND custom_locationpost.chlorine_level IS NOT NULL
                              ORDER BY published_date DESC LIMIT 1""",
            'water_source_type_id': """SELECT custom_locationpost.water_source_type_id
                              FROM custom_locationpost
                              WHERE custom_location.id = custom_locationpost.location_id
                              AND custom_locationpost.chlorine_level IS NOT NULL
                              ORDER BY published_date DESC LIMIT 1""",
            'provider_id': """SELECT custom_locationpost.provider_id
                              FROM custom_locationpost
                              WHERE custom_location.id = custom_locationpost.location_id
                              AND custom_locationpost.chlorine_level IS NOT NULL
                              ORDER BY published_date DESC LIMIT 1""",
        },
    )

    # TODO : can we do filters in sql instead of python's filter()
    locations_processed = locations_chlorine_level_filter(locations, request)
    locations_processed = locations_water_source_type_filter(locations_processed, request)
    locations_processed = locations_provider_filter(locations_processed, request)

    current_site = get_current_site(request)

    return render_to_response('homepage_kml.kml',
        {
            'locations': locations_processed,
            'current_site': current_site,
            'user_is_authenticated': user_is_authenticated,
        },
        context_instance=RequestContext(request),
        mimetype='application/vnd.google-earth.kml+xml',
    )

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
    location_posts = LocationPost.active_objects.filter(location=location).order_by('-published_date')

    water_quality_location_posts = location_posts.filter(
        type=LocationPost.WATER_QUALITY_TYPE,
        chlorine_level__isnull=False).order_by('-published_date')[:12]
    try:
        latest_water_quality_location_post = water_quality_location_posts[0]
    except:
        latest_water_quality_location_post = None
    water_quality_location_posts = water_quality_location_posts.reverse()

    xaxis_categories = []
    site_wide_chlorine_averages = []
    for water_quality_location_post in water_quality_location_posts:
        xaxis_categories.append(water_quality_location_post.published_date)
        site_avg = LocationPost.active_objects.filter(
            type=LocationPost.WATER_QUALITY_TYPE,
            chlorine_level__isnull=False,
            published_date__year=water_quality_location_post.published_date.year,
            published_date__month=water_quality_location_post.published_date.month,
            published_date__day=water_quality_location_post.published_date.day
        ).aggregate(Avg('chlorine_level'))
        site_wide_chlorine_averages.append(site_avg['chlorine_level__avg'])


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
            'water_quality_location_posts': water_quality_location_posts,
            'xaxis_categories': xaxis_categories,
            'site_wide_chlorine_averages': site_wide_chlorine_averages,
            'latest_water_quality_location_post': latest_water_quality_location_post,
        },
        context_instance=RequestContext(request)
    )