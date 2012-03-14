from decimal import Decimal

def locations_set_chlorine_status(locations):
    locations_processed = []
    for location in locations:
        location.chlorine_level_status = location.get_chlorine_level_status(location.chlorine_level)
        locations_processed.append(location)
    return locations_processed

def locations_chlorine_level_filter(locations, request):
    if (
            not 'chlorine_level_zero' in request.GET and
            not 'chlorine_level_low' in request.GET and
            not 'chlorine_level_pass' in request.GET and
            not 'chlorine_level_high' in request.GET
        ):
        return locations

    zero_locations = []
    if 'chlorine_level_zero' in request.GET:
        zero_locations = filter(lambda location: location.chlorine_level == Decimal('0.00'), locations)

    low_locations = []
    if 'chlorine_level_low' in request.GET:
        low_locations = filter(lambda location: (location.chlorine_level > Decimal('0.00') and location.chlorine_level < Decimal('0.50')), locations)

    pass_locations = []
    if 'chlorine_level_pass' in request.GET:
        pass_locations = filter(lambda location: (location.chlorine_level >= Decimal('0.50') and location.chlorine_level < Decimal('2.00')), locations)

    high_locations = []
    if 'chlorine_level_high' in request.GET:
        high_locations = filter(lambda location: location.chlorine_level >= Decimal('2.00'), locations)

    return zero_locations + low_locations + pass_locations + high_locations

def locations_water_source_type_filter(locations, request):
    request_get_keys = request.GET.keys()
    water_source_type_ids = []

    if not 'water_source_type_' in (',').join(request_get_keys):
        return locations

    for key in request_get_keys:
        if not 'water_source_type_' in key:
            continue
        try:
            water_source_type_ids.append(int(key.strip('water_source_type_')))
        except:
            continue

    filtered_locations = filter(lambda location : location.water_source_type_id in water_source_type_ids, locations)

    return filtered_locations

def locations_provider_filter(locations, request):
    request_get_keys = request.GET.keys()
    provider_ids = []

    if not 'provider_' in (',').join(request_get_keys):
        return locations

    for key in request_get_keys:
        if not 'provider_' in key:
            continue
        try:
            provider_ids.append(int(key.strip('provider_')))
        except:
            continue

    filtered_locations = filter(lambda location : location.provider_id in provider_ids, locations)

    return filtered_locations