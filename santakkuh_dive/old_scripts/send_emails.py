import sys
import sqlite3
import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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


def send_email(connection, giver, recipient):
    send_now = True
    HMTL = """
        <html>
        <head></head>
        <body>
        <p>
        Good news, %s! Your Secret Holiday Recipient this year is: <b>%s</b>! <br><br>

        %s %s be in the office for the gift exchange and likes:<br>
        %s
        <br><br>
        Is %s allergic to or strongly opposed to anything?<br>
        %s
        <br><br>
        Remember to keep your spending around $25 and NO GIFT CARDS or you'll ruin the holidays.

        Thanks!
        </p>
        </body>
        </html>
        """ % (
        giver.name,
        recipient.name,
        recipient.name,
        "will" if recipient.in_office else "<b>WILL NOT</b>",
        recipient.likes or "nothing, apparently. Good luck!",
        recipient.name,
        recipient.dislikes or "nothing, apparently. Good luck!",
    )

    TEXT = """
        Good news, %s! Your Secret Holiday Recipient this year is: %s!

        %s %s be in the office for the gift exchange and likes:
        %s

        Is %s allergic to or strongly opposed to anything?
        %s

        Remember to keep your spending around $25 and NO GIFT CARDS or you'll ruin the holidays.

        Thanks!
        """ % (
        giver.name,
        recipient.name,
        recipient.name,
        "will" if recipient.in_office else "WILL NOT",
        recipient.likes or "nothing, apparently. Good luck!",
        recipient.name,
        recipient.dislikes or "nothing, apparently. Good luck!",
    )

    FROM = 'Secret Gift Exchange <%s>' % settings.FROM_EMAIL
    TO = giver.email
    SUBJECT = 'Secret Holiday Gift Exchange %d!!!' % settings.YEAR

    if send_now:
        print("sending email to %s (%s)" % (giver.name, giver.email))
        msg = MIMEMultipart('alternative')
        part1 = MIMEText(TEXT, 'plain')
        part2 = MIMEText(HMTL, 'html')
        msg.attach(part1)
        msg.attach(part2)
        msg['Subject'] = SUBJECT
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # port 465 or 587
        server.ehlo()
        # server.starttls()
        # server.ehlo()
        server.login(settings.FROM_EMAIL, settings.EMAIL_PW)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
        connection.cursor().execute("UPDATE assignments SET email_sent = 'Y' where giver_id = %d" % giver.id)
        connection.commit()
    else:
        print("[TEST] sending email to %s (%s)" % (giver.name, giver.email))


def get_assignment(connection, participant_id, year):
    assignment_result = connection.cursor().execute(
        "SELECT giver_id, recipient_id FROM v_assignments WHERE year = %d and giver_id=%d" % (
            year, participant_id
        )
    )
    for row in assignment_result:
        return row


def send_emails(connection, year, participants):
    for participant_id in participants:
        assignment = get_assignment(connection, participant_id, year)
        giver_id = assignment[0]
        recipient_id = assignment[1]

        giver = Participant(connection, giver_id, year)
        recipient = Participant(connection, recipient_id, year)
        send_email(connection, giver, recipient)


def get_all_participants(connection, year):
    sql = """
        SELECT giver_id FROM v_assignments
        WHERE year = %d and (email_sent != 'Y' or email_sent is null)
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


if __name__ == '__main__':
    testing = '--testing' in sys.argv
    connection = sqlite3.connect(settings.SQLITE_FILENAME)

    if testing:
        print("just testing, folks")
        participants = get_targetted_participants(connection, settings.YEAR, settings.TEST_EMAILS)
        send_emails(connection, settings.YEAR, participants)
    else:
        print("ITS THE REAL THING")
        participants = get_all_participants(connection, settings.YEAR)
        send_emails(connection, settings.YEAR, participants)
