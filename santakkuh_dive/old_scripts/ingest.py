import sqlite3
import settings
import csv


def get_create_or_update_participant(connection, email, name):
    existing_participant_sql = """
        SELECT id FROM participants WHERE email = '%s';
    """ % (email)

    cursor = connection.cursor()
    print(existing_participant_sql)
    existing_participant = cursor.execute(
        existing_participant_sql
    ).fetchone()
    if existing_participant:
        sql_template = """
            UPDATE participants SET
            name = '%s'
            WHERE id = %d
        """
        sql = sql_template % (
            name.strip(),
            existing_participant[0]
        )

    else:
        sql_template = """
            INSERT INTO PARTICIPANTS (name, email)
            VALUES ('%s', '%s');
        """
        sql = sql_template % (
            name.strip(),
            email.strip()
        )
    print(sql)
    connection.cursor().execute(sql)
    connection.commit()

    cursor = connection.cursor()
    print(existing_participant_sql)
    existing_participant = cursor.execute(
        existing_participant_sql
    ).fetchone()
    return existing_participant[0]


def create_or_update_preferences(connection, participant_id, year, likes, dislikes, in_office):
    existing_preferences_sql = """
        SELECT participant_id, year, likes, dislikes, in_office
        FROM preferences WHERE year = %d and participant_id = %d
    """
    cursor = connection.cursor()
    existing_preferences = cursor.execute(
        existing_preferences_sql % (year, participant_id)
    ).fetchone()

    if existing_preferences:
        sql_template = """
            UPDATE preferences SET
                likes = ?,
                dislikes = ?,
                in_office = ?
                WHERE year = ? and participant_id = ?;
        """
        cursor = connection.cursor()
        connection.cursor().execute(sql_template, (likes, dislikes, in_office, year, participant_id))
        connection.commit()

    else:
        sql_template = """
            INSERT INTO preferences (participant_id, year, likes, dislikes, in_office)
            VALUES (?, ?, ?, ?, ?);
        """

        cursor = connection.cursor()
        connection.cursor().execute(sql_template, (participant_id, year, likes, dislikes, in_office))
        connection.commit()


def parse_csv_into_sqlite(connection, source_file, year):
    with open(source_file, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            participant_id = get_create_or_update_participant(
                connection,
                row['email'],
                row['name']
            )
            create_or_update_preferences(
                connection,
                participant_id,
                year,
                row['likes'],
                row['allergies/dislikes'],
                row['in_office']
            )


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    parse_csv_into_sqlite(connection, settings.SOURCE_FILE, settings.YEAR)
