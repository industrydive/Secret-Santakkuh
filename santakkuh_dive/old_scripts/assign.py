import random
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


def _get_previous_assignee_for_giver(connection, year, giver_id):
    last_year = year - 1
    previous_recipient_sql = """
        SELECT recipient_id
        FROM assignments WHERE
        year = %d
        AND giver_id = %d;
    """
    previous_recipient_id = None
    for recipient_id in connection.cursor().execute(
        previous_recipient_sql % (last_year, giver_id)
    ):
        previous_recipient_id = recipient_id[0]
    return previous_recipient_id


def _available_recipients(connection, exclude_ids, year):
    available_recipients = []
    sql = """
        SELECT participant_id, name FROM v_participants WHERE year = %d and participant_id NOT IN (%s)
    """ % (year, ','.join([str(xid) for xid in exclude_ids]))
    for recipient in connection.cursor().execute(sql):
        available_recipients.append(recipient)
    return available_recipients


def _get_random_assignee_for_giver(connection, year, giver_id, assignments):
    recipient_giver_list = {assigned_recipients: assigned_giver for assigned_giver, assigned_recipients in assignments.iteritems()}
    already_assigned = recipient_giver_list.get(giver_id)

    previous_recipient_id = _get_previous_assignee_for_giver(connection, year, giver_id)

    # people who have already been assigned to a giver
    assigned_recipient_ids = [assigned_recipient for assigned_giver, assigned_recipient in assignments.iteritems()]

    # if this giver gave a gift last year, exclude that person from their pool this year
    if previous_recipient_id:
        exclude_ids = list(set(assigned_recipient_ids + [previous_recipient_id, giver_id]))
    else:
        exclude_ids = list(set(assigned_recipient_ids + [giver_id, ]))

    # make sure this person doesn't get assigned the person who has them if applicable
    if already_assigned:
        exclude_ids = list(set(exclude_ids + [already_assigned, ]))

    available_recipients = _available_recipients(connection, exclude_ids, year)
    return random.choice(available_recipients)


def _make_assignments(connection, year, verbose):
    sql = """
        SELECT participant_id, name FROM v_participants WHERE year = %d ORDER BY RANDOM()
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
    # edges = []
    checking_now = assignments.keys()[0]
    checking_next = assignments[checking_now]
    checked = []
    while checking_now:
        checked.append(checking_now)
        checking_now = checking_next
        checking_next = assignments.get(checking_next)
        if checking_next in checked:
            checked.append(checking_next)
            # loop has closed, stop creating edges and end while loop
            checking_now = False

    # if we made the same amount of edges as we have assignments, then
    # the while loop got all the way through the assignments and we have
    # a full loop
    return len(checked) == len(assignments)


def _start_fresh(connection, year, verbose, _try):
    everyone_is_assigned = False
    assignments = {}
    while not everyone_is_assigned:
        print "try %d" % _try
        everyone_is_assigned, assignments = _make_assignments(connection, year, verbose)
        _try += 1
    return _try, assignments


def _final_checks(connection, year):
    ''' Sanity checks against assignee data
    '''
    total_particpant_q = connection.cursor().execute("select count(*) from v_participants where year = %d" % year)
    for row in total_particpant_q:
        total_particpant_count = int(row[0])

    total_giver_q = connection.cursor().execute("select count(distinct giver_id) from assignments where year = %d" % year)
    for row in total_giver_q:
        total_giver_count = int(row[0])

    total_recipient_q = connection.cursor().execute("select count(distinct recipient_id) from assignments where year = %d" % year)
    for row in total_recipient_q:
        total_recipient_count = int(row[0])

    dupe_count_qs = connection.cursor().execute("select count(*) from assignments where giver_id = recipient_id and year = %d" % year)
    for row in dupe_count_qs:
        dupe_count_count = int(row[0])

    print "total participants: %d" % total_particpant_count
    print "total assigned givers: %d" % total_giver_count
    print "total assigned recipients: %d" % total_recipient_count
    print "anyone assigned to themselves: %d" % dupe_count_count


def assign_participants(connection, year, verbose=False):
    verify_sql = "select count(*) from v_participants where year = %d" % year
    for row in connection.cursor().execute(verify_sql):
        if row[0] < 4:
            exit("you need at least 3 people to participate")
    max_tries = 10
    is_closed_loop = False
    _try = 1
    print "try %d" % _try
    while not is_closed_loop and _try <= max_tries:
        _try, assignments = _start_fresh(connection, year, verbose, _try)
        if verbose:
            print "checking is closed loop..."
        is_closed_loop = _check_is_closed_loop(assignments)
        if is_closed_loop:
            print "is closed loop on try %d" % _try
        else:
            print "is not closed loop, trying again"
    if is_closed_loop:
        _save_assignments(connection, year, assignments)
        _final_checks(connection, year)
    else:
        print "failed to generate closed loop in under %d tries" % max_tries


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    assign_participants(connection, settings.YEAR, verbose='--verbose' in sys.argv)
