import sqlite3
import settings
import csv


def parse_csv_into_sqlite(connection, source_file, year):
    with open(source_file, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            existing_participant_sql = """
                SELECT * FROM participants WHERE year = %d AND email = '%s';
            """

            cursor = connection.cursor()
            existing_participant = cursor.execute(
                existing_participant_sql % (year, row['email'])
            ).fetchone()
            if existing_participant:
                sql_template = """
                    UPDATE participants SET
                    name = '%s',
                    likes = '%s',
                    dislikes = '%s'
                    WHERE email = '%s' and year = %d
                """
                sql = sql_template % (
                    row['name'].strip(),
                    row['likes'].strip(),
                    row['allergies/dislikes'].strip(),
                    row['email'].strip(),
                    year
                )

            else:
                sql_template = """
                    INSERT INTO PARTICIPANTS (year, name, email, likes, dislikes)
                    VALUES (%d, '%s', '%s', '%s', '%s');
                """
                sql = sql_template % (
                    year,
                    row['name'].strip(),
                    row['email'].strip(),
                    row['likes'].strip(),
                    row['allergies/dislikes'].strip()
                )
            print sql
            connection.cursor().execute(sql)
            connection.commit()


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    parse_csv_into_sqlite(connection, settings.SOURCE_FILE, settings.YEAR)
