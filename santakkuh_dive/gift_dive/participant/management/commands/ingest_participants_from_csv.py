import csv

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
# from django.utils.crypto import get_random_string

from participant.models import Participant


class Command(BaseCommand):

    help = 'Ingests participants from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str)
        parser.add_argument('--year', type=int)

    def handle(self, *args, **options):

        with open(options['file'], mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                existing_user = User.objects.filter(email=row['email']).exists()
                if not existing_user:
                    user = User(
                        email=row['email'],
                        username=row['email'].split('@')[0],
                    )

                    user.set_password('ChangeMeNow')
                    user.save()
                    print("adding new user %s" % user.username)
                else:
                    user = User.objects.get(email=row['email'])
                    print("updating user %s" % user.username)

                existing_profile = Participant.objects.filter(user=user, participation_year=options['year']).exists()

                if not existing_profile:
                        profile = Participant(
                            participation_year=options['year'],
                            likes=row['likes'].strip(),
                            dislikes=row['allergies/dislikes'].strip(),
                            user=user,
                            display_name=row['name'].strip()
                        )
                else:
                    profile = Participant.objects.get(user=user, participation_year=options['year'])
                    profile.likes = row['likes'].strip()
                    profile.dislikes = row['allergies/dislikes'].strip()
                    profile.display_name = row['name'].strip()

                profile.save()
