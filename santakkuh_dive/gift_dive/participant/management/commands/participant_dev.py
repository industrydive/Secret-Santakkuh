from django.core.management.base import BaseCommand
from participant.models import Participant


class Command(BaseCommand):
    def handle(self, *args, **options):
        test_id = 76

        person = Participant.objects.get(pk=test_id)
        santa = person.secret_santa()

        print(santa)
