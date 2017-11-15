import sqlite3
import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Participant():
    def __init__(self, connection, id, year):
        select_sql = "SELECT name, email, likes, dislikes, in_office FROM participants WHERE id = %d AND year = %d" % (
            id, year
        )
        for data_row in connection.cursor().execute(select_sql):
            self.name = data_row[0]
            self.email = data_row[1]
            self.likes = data_row[2] if data_row[2].strip() != '' else None
            self.dislikes = data_row[3] if data_row[3].strip() != '' else None
            self.in_office = data_row[4] == 'Yes'


def send_email(giver, recipient):
    send_now = True
    HMTL = """
        <html>
        <head></head>
        <body>
        <p>
        Good news, %s! Your Secret Santakkuh recipient this year is: <b>%s</b>! <br><br>

        %s %s be in the office for the gift exchange and likes:<br>
        %s
        <br><br>
        Is %s allergic to or strongly opposed to anything?<br>
        %s
        <br><br>
        Remember to keep your spending around $20 and NO GIFT CARDS or you'll ruin christmas.

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
        Good news, %s! Your Secret Santakkuh recipient this year is: %s!

        %s %s be in the office for the gift exchange and likes:
        %s

        Is %s allergic to or strongly opposed to anything?
        %s

        Remember to keep your spending around $20 and NO GIFT CARDS or you'll ruin christmas.

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

    FROM = settings.FROM_EMAIL
    TO = giver.email
    SUBJECT = 'Secret Santakkuh TEST FOR %s' % giver.name

    if send_now:
        msg = MIMEMultipart('alternative')
        part1 = MIMEText(TEXT, 'plain')
        part2 = MIMEText(HMTL, 'html')
        msg.attach(part1)
        msg.attach(part2)
        msg['Subject'] = SUBJECT
        server = smtplib.SMTP('smtp.gmail.com', 587)  # port 465 or 587
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.FROM_EMAIL, settings.EMAIL_PW)
        server.sendmail(FROM, TO, msg.as_string())
        server.close()
    else:

        print TEXT


def send_emails(connection, year):
    assignments_sql = "SELECT giver_id, recipient_id FROM assignments WHERE year = %d" % year
    for assignment in connection.cursor().execute(assignments_sql):
        giver_id = assignment[0]
        recipient_id = assignment[1]

        giver = Participant(connection, giver_id, year)
        recipient = Participant(connection, recipient_id, year)

        send_email(giver, recipient)


if __name__ == '__main__':
    connection = sqlite3.connect(settings.SQLITE_FILENAME)
    send_emails(connection, settings.YEAR)
