import sys
import sqlite3
import settings


def destroy_db(connection):
    print "dropping tables"
    for table in ['participants', 'assignments']:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS %s" % table)


def create_db(connection):
    print "creating tables"
    participants_table_def = """
        CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY,
        year INTEGER,
        name VARCHAR,
        email VARCHAR,
        in_office VARCHAR,
        dislikes VARCHAR,
        likes VARCHAR
    )
    """

    cursor = connection.cursor()
    cursor.execute(participants_table_def)

    assignments_table_def = """
        CREATE TABLE IF NOT EXISTS assignments (
        year INTEGER,
        giver_id INTEGER,
        recipient_id INTEGER,
        PRIMARY KEY (year, giver_id),
        FOREIGN KEY(giver_id) REFERENCES participants(id),
        FOREIGN KEY(recipient_id) REFERENCES participants(id)
        )
    """
    cursor = connection.cursor()
    cursor.execute(assignments_table_def)


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    if '--clean' in sys.argv:
        destroy_db(connection)
    create_db(connection)
