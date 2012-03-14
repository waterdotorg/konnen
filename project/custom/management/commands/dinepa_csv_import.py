import csv
import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from custom.models import Community, Location, WaterSourceType, Provider, LocationPost

class Command(BaseCommand):
    help = 'Import Dinepa CSV data'
    args = '< /path/filname.csv user_id >'

    def handle(self, *args, **options):
        try:
            file_path = args[0]
            user = User.objects.get(id=args[1])
        except:
            raise CommandError("Need file path and user id arguments.")

        try:
            r = csv.reader(open(file_path, 'rb'), delimiter=',', quotechar='"')
            r.next()
        except:
            raise CommandError("Unable to parse CSV file")

        try:
            for row in r:
                try:
                    community = Community.objects.get(title__iexact=row[1])
                except Community.DoesNotExist:
                    community = Community(title=row[1])
                    community.save()
                try:
                    location = Location.objects.get(uid=row[6])
                except Location.DoesNotExist:
                    location = Location(
                        title=row[2],
                        latitude=row[3],
                        longitude=row[4],
                        uid=row[6],
                        community=community,
                    )
                    location.save()
                try:
                    water_source_type = WaterSourceType.objects.get(title__iexact=row[5])
                except WaterSourceType.DoesNotExist:
                    water_source_type = WaterSourceType(title=row[5])
                    water_source_type.save()
                try:
                    provider = Provider.objects.get(title__iexact=row[8])
                except Provider.DoesNotExist:
                    provider = Provider(title=row[8])
                    provider.save()
                try:
                    location_post = LocationPost.objects.get(
                        user=user,
                        published_date=datetime.datetime.strptime(row[0], '%m/%d/%Y %H:%M'),
                        location=location,
                        water_source_type=water_source_type,
                        provider=provider,
                        chlorine_level=row[7],
                        content=row[9],
                    )
                except LocationPost.DoesNotExist:
                    location_post = LocationPost(
                        user=user,
                        published_date=datetime.datetime.strptime(row[0], '%m/%d/%Y %H:%M'),
                        location=location,
                        water_source_type=water_source_type,
                        provider=provider,
                        chlorine_level=row[7],
                        content=row[9],
                    )
                    location_post.save()
        except:
            raise
            #raise CommandError("Error during csv import")