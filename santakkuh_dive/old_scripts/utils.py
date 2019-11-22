class Participant():
    def __init__(self, connection, id, year):
        select_sql = """
            SELECT name, email, likes, dislikes, in_office, participant_id
            FROM v_participants WHERE participant_id = %d AND year = %d
        """ % (id, year)

        for data_row in connection.cursor().execute(select_sql):
            self.name = data_row[0]
            self.email = data_row[1]
            self.likes = data_row[2] if data_row[2].strip() != '' else None
            self.dislikes = data_row[3] if data_row[3].strip() != '' else None
            self.in_office = data_row[4] == 'Yes'
            self.id = data_row[5]


def get_all_participants(connection, year, exclude_email_sent=True):
    if exclude_email_sent:
        sql = """
            SELECT giver_id FROM v_assignments
            WHERE year = %d and (email_sent != 'Y' or email_sent is null)
        """ % year
    else:
        sql = """
            SELECT giver_id FROM v_assignments
            WHERE year = %d
        """ % year
    participants = []
    for row in connection.cursor().execute(sql):
        participants.append(row[0])
    return participants


def get_targetted_participants(connection, year, emails):
    sql = """
        SELECT giver_id FROM v_assignments WHERE year = %d
        AND giver_email in (%s)
    """ % (year, ",".join(["'%s'" % email for email in emails]))

    participants = []
    for row in connection.cursor().execute(sql):
        participants.append(row[0])
    return participants


def get_assignment(connection, participant_id, year):
    assignment_result = connection.cursor().execute(
        "SELECT giver_id, recipient_id FROM v_assignments WHERE year = %d and giver_id=%d" % (
            year, participant_id
        )
    )
    for row in assignment_result:
        return row
