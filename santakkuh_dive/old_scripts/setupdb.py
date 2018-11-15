import sys
import sqlite3
import settings


def destroy_db(connection):
    print "dropping tables"
    for drop_statement in [
        'DROP VIEW IF EXISTS v_assignments',
        'DROP VIEW IF EXISTS v_participants',
        'DROP TABLE IF EXISTS participants',
        'DROP TABLE IF EXISTS assignments'
    ]:
        cursor = connection.cursor()
        cursor.execute(drop_statement)


def create_db(connection):
    print "creating tables"
    participants_table_def = """
        CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR
    )
    """

    cursor = connection.cursor()
    cursor.execute(participants_table_def)

    preferences_table_def = """
        CREATE TABLE IF NOT EXISTS preferences (
        participant_id INTEGER,
        year INTEGER,
        in_office VARCHAR,
        dislikes VARCHAR,
        likes VARCHAR,
        PRIMARY KEY (year, participant_id),
        FOREIGN KEY(participant_id) REFERENCES participants(id)
    )
    """

    cursor = connection.cursor()
    cursor.execute(preferences_table_def)

    assignments_table_def = """
        CREATE TABLE IF NOT EXISTS assignments (
        year INTEGER,
        giver_id INTEGER,
        recipient_id INTEGER,
        email_sent VARCHAR,
        PRIMARY KEY (year, giver_id),
        FOREIGN KEY(giver_id) REFERENCES participants(id),
        FOREIGN KEY(recipient_id) REFERENCES participants(id)
        )
    """
    cursor = connection.cursor()
    cursor.execute(assignments_table_def)

    participants_view_def = """
        CREATE VIEW IF NOT EXISTS v_participants AS
        SELECT
            p.id as participant_id,
            p.email,
            p.name,
            pr.year,
            pr.likes,
            pr.dislikes,
            pr.in_office
        FROM participants p, preferences pr where pr.participant_id = p.id;
    """

    cursor = connection.cursor()
    cursor.execute(participants_view_def)

    assignments_view = """
    CREATE VIEW IF NOT EXISTS v_assignments AS
    select
        a.giver_id,
        a.recipient_id,
        p.year,
        p.name,
        p.email,
        p.likes,
        p.dislikes,
        p.in_office
    from
    assignments a, v_participants p
    where
    p.participant_id = a.recipient_id
    and a.year = p.year
    """
    cursor = connection.cursor()
    cursor.execute(assignments_view)


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    if '--clean' in sys.argv:
        destroy_db(connection)
    create_db(connection)
