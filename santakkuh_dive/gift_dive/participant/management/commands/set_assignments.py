from django.core.management.base import BaseCommand
from django.db.models import Q
# from django.utils.crypto import get_random_string

from participant.models import Participant, Assignment

# todo: make this more smarter
PARTICIPATION_YEAR = 2017


class Command(BaseCommand):

    help = 'Sets secret giver assignments for the latest participation year'

    def _check_is_closed_loop(self, assignments):
        edges = []
        assignments_as_simple_dict = {giver.id: recipient.id for giver, recipient in assignments.items()}
        checking_now = list(assignments_as_simple_dict.keys())[0]
        checking_next = assignments_as_simple_dict[checking_now]
        while checking_now:
            edges.append((checking_now, checking_next))
            checking_now = checking_next
            checking_next = assignments_as_simple_dict.get(checking_next)
            if checking_next == list(assignments_as_simple_dict.keys())[0]:  # the next person to check is the first person
                edges.append((checking_now, checking_next))
                # loop has closed, stop creating edges and end while loop
                checking_now = False

        # if we made the same amount of edges as we have assignments, then
        # the while loop got all the way through the assignments and we have
        # a full loop
        return len(edges) == len(assignments)

    def _get_random_assignee_for_giver(self, year, giver, assignments):
        already_assigned = [recipient.user for g, recipient in assignments.items()]
        recipient = Participant.objects.filter(
            participation_year=year
        ).filter(
            ~Q(user_id=giver.id)
        ).filter(
            ~Q(user_id__in=already_assigned)
        ).order_by('?').first()

        # print recipient_sql

        return recipient

    def _make_assignments(self, year):

        participants = Participant.objects.filter(
            participation_year=PARTICIPATION_YEAR).order_by('?').all()

        assignments = {}

        for giver in participants:

            recipient = self._get_random_assignee_for_giver(year, giver, assignments)
            if recipient:
                assignments[giver] = recipient
            # print ("%s has %s" % (giver.display_name, recipient.display_name))

        return len(assignments) == len(participants), assignments

    def _start_fresh(self, year):
        everyone_is_assigned = False
        assignments = {}
        _try = 1
        while not everyone_is_assigned:
            everyone_is_assigned, assignments = self._make_assignments(year)
            _try += 1
        return assignments

    def handle(self, *args, **options):

        is_closed_loop = False
        _try = 1
        while not is_closed_loop:
            assignments = self._start_fresh(PARTICIPATION_YEAR)
            is_closed_loop = self._check_is_closed_loop(assignments)
            if is_closed_loop:
                print ("try %d is closed loop" % _try)
            else:
                print ("try %d is not closed loop, trying again" % _try)
            _try += 1
        for giver, recipient in assignments.items():
            assignment = Assignment.objects.filter(
                participation_year=PARTICIPATION_YEAR,
                giver=giver,
                # recipient=recipient
            ).first()
            if assignment:
                assignment.recipient = recipient
            else:
                assignment = Assignment(
                    participation_year=PARTICIPATION_YEAR,
                    giver=giver,
                    recipient=recipient
                )
            assignment.save()
