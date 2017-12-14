import csv
from django.core.management.base import BaseCommand

from participant.models import Participant, Assignment


class Command(BaseCommand):

    help = 'Ingests participants from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str)

    def handle(self, *args, **options):

        with open(options['file'], mode='r') as infile:
            reader = csv.DictReader(infile)
            # header: giver,recipient,recipient dislikes,recipient likes
            for row in reader:
                try:
                    giver = Participant.objects.get(display_name=row['giver'])
                    recipient = Participant.objects.get(display_name=row['recipient'])
                    assg = Assignment(
                        participation_year=2017,
                        giver=giver,
                        recipient=recipient
                    )
                    assg.save()
                except Exception:
                    import pdb
                    pdb.set_trace()
