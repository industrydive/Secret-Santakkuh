import sqlite3
import settings
import csv
import sys

from utils import Participant, get_all_participants, get_targetted_participants, get_assignment


def make_output_csv(connection, participants):
    with open(settings.OUT_FILE, 'w+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['giver', 'recipient', 'recipient likes', 'recipient dislikes/allergies', 'giver in office', 'recipient in office'])

        for participant_id in participants:
            assignment = get_assignment(connection, participant_id, settings.YEAR)
            giver_id = assignment[0]
            recipient_id = assignment[1]

            giver = Participant(connection, giver_id, settings.YEAR)
            recipient = Participant(connection, recipient_id, settings.YEAR)
            row_data = [
                giver.name,
                recipient.name,
                recipient.likes,
                recipient.dislikes,
                giver.in_office,
                recipient.in_office
            ]

            writer.writerow(row_data)


if __name__ == '__main__':
    testing = '--testing' in sys.argv
    connection = sqlite3.connect(settings.SQLITE_FILENAME)

    if testing:
        print("just testing, folks")
        participants = get_targetted_participants(connection, settings.YEAR, settings.TEST_EMAILS)
    else:
        print("ITS THE REAL THING")
        participants = get_all_participants(connection, settings.YEAR, exclude_email_sent=False)

    make_output_csv(connection, participants)
