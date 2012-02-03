import datetime

from django.shortcuts import render_to_response, redirect, get_object_or_404

from custom.models import Location
from django.template.context import RequestContext

def location(request, slug=None):
    location = get_object_or_404(Location, slug=slug, status=Location.ACTIVE_STATUS, published_date__lte=datetime.datetime.now())

    return render_to_response('location/location.html',
        {
            'location': location,
        },
        context_instance=RequestContext(request)
    )