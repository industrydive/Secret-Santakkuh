import sys
import sqlite3
import settings


def _save_assignments(connection, year, assignments):
    print "saving assignments"
    connection.cursor().execute('delete from assignments where year = %d' % year)
    for giver, reciever in assignments.iteritems():
        sql = "INSERT INTO assignments (year, giver_id, recipient_id) VALUES (%d, %d, %d)"
        connection.cursor().execute(sql % (year, giver, reciever))
    connection.commit()


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


def _make_assignments(connection, year, verbose):
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
            if verbose:
                print "%s has %s" % (giver_name, recipient_name)
            everyone_is_assigned = True
        else:
            if verbose:
                print "%s has no one" % (giver_name)
            everyone_is_assigned = False
    return everyone_is_assigned, assignments


def _check_is_closed_loop(assignments):
    edges = []
    checking_now = assignments.keys()[0]
    checking_next = assignments[checking_now]
    while checking_now:
        edges.append((checking_now, checking_next))
        checking_now = checking_next
        checking_next = assignments.get(checking_next)
        if checking_next == assignments.keys()[0]:
            edges.append((checking_now, checking_next))
            # loop has closed, stop creating edges and end while loop
            checking_now = False

    # if we made the same amount of edges as we have assignments, then
    # the while loop got all the way through the assignments and we have
    # a full loop
    return len(edges) == len(assignments)


def _start_fresh(connection, year, verbose):
    everyone_is_assigned = False
    assignments = {}
    _try = 1
    while not everyone_is_assigned:
        print "try %d" % _try
        everyone_is_assigned, assignments = _make_assignments(connection, year, verbose)
        _try += 1
    return assignments


def assign_participants(connection, year, verbose=False):
    verify_sql = "select count(*) from participants where year = %d" % year
    for row in connection.cursor().execute(verify_sql):
        if row[0] < 4:
            exit("you need at least 3 people to participate")

    is_closed_loop = False
    while not is_closed_loop:
        assignments = _start_fresh(connection, year, verbose)
        is_closed_loop = _check_is_closed_loop(assignments)
        if is_closed_loop:
            print "is closed loop"
        else:
            print "is not closed loop, trying again"

    _save_assignments(connection, year, assignments)


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    assign_participants(connection, settings.YEAR, verbose='--verbose' in sys.argv)
