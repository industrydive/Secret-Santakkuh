import sqlite3
import settings


def assign_participants(connection, year):

    def _get_random_assignee_for_giver(connection, year, giver_id, assignments):
        already_assigned = {assigned_recipients: assigned_giver for assigned_giver, assigned_recipients in assignments.iteritems()}
        recipient = None

        recipient_sql_template = """
            SELECT id, name
            FROM participants WHERE
            year = %d
            AND id != %d
            AND id not in (%s)
            %s
            AND id >= (abs(random()) %% (SELECT max(id) FROM participants))
            LIMIT 1
        """

        recipient_sql = recipient_sql_template % (
            year,
            giver_id,
            ','.join(
                [str(assigned_recipients) for assigned_giver, assigned_recipients in assignments.iteritems()]
            ),
            'AND id != %d' % already_assigned.get(giver_id) if already_assigned.get(giver_id) else ''
        )

        # print recipient_sql

        for recipient in connection.cursor().execute(recipient_sql):
            return recipient
        return None

    def _make_assignments(connection, year):
        sql = """
            SELECT id, name FROM participants WHERE year = %d ORDER BY RANDOM()
        """

        assignments = {}
        everyone_is_assigned = False

        for giver in connection.cursor().execute(sql % year):
            giver_id = giver[0]
            giver_name = giver[1]

            recipient = _get_random_assignee_for_giver(connection, year, giver_id, assignments)

            if recipient:
                recipient_name = recipient[1]
                recipient_id = recipient[0]
                assignments[giver_id] = recipient_id
                print "%s has %s" % (giver_name, recipient_name)
                everyone_is_assigned = True
            else:
                print "%s has no one" % (giver_name)
                everyone_is_assigned = False
        return everyone_is_assigned, assignments

    connection.cursor().execute('delete from assignments where year = %d' % year)

    everyone_is_assigned = False
    assignments = {}
    _try = 1
    while not everyone_is_assigned:
        print "try %d" % _try
        everyone_is_assigned, assignments = _make_assignments(connection, year)
        _try += 1


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    assign_participants(connection, settings.YEAR)
