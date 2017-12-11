import sqlite3
import settings
import csv


def make_output_csv(connection):
    assignments_sql = """
        select
        giv.name as giver,
        rec.name as recipient,
        rec.dislikes as dislikes,
        rec.likes as likes
        from participants giv, participants rec, assignments asm
        where
        giv.id = asm.giver_id
        and rec.id = asm.recipient_id
    """

    with open(settings.OUT_FILE, 'w+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['giver', 'recipient', 'recipient dislikes', 'recipient likes'])
        for assignment in connection.cursor().execute(assignments_sql):
            writer.writerow(assignment)


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    make_output_csv(connection)
