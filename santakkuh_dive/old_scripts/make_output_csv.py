import sqlite3
import settings
import csv


def make_output_csv(connection):
    assignments_sql = """
        select
        giver.name,
        recipient.name,
        recipient.likes,
        recipient.dislikes,
        recipient.in_office
        from v_assignments recipient, participants giver
        where
        giver.id = recipient.giver_id
        and year = %d
    """

    with open(settings.OUT_FILE, 'w+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['giver', 'recipient', 'recipient likes', 'recipient dislikes', 'recipient in office'])
        for assignment in connection.cursor().execute(assignments_sql % settings.YEAR):
            writer.writerow(assignment)


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    make_output_csv(connection)
