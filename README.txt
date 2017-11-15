Secret Santakkuh Dive
+========================+
 	Getting Started
+========================+

1) Create and activate a python virtual environment
2) pip install the requirements
3) Copy settings_sample.py to settings.py and adjust the values as needed
4) Run the modules as detailed below

+========================+
 	Modules
+========================+

setupdb
------------------

This module sets up a sqlite database in the current directory
The file will be named whatever is in your settings.py under
SQLITE_FILENAME

if you run it with a --clean flag, it will first drop the tables
in the database if they exist and then build the tables. Otherwise
it will just execute "create if not exists" statements to build 
tables.

usage:

$ python setuodb.py
or
$ python setupdb.py --clean


ingest
------------------

This module ingests data from a CSV file into the sqlite database.
The file must have the headers:
name, email, allergies/dislikes, likes, in_office

For each email and given year (in settings.py), the script will perform
an upsert on the data in the database - so you can run this against the
same set of participants as many times as you need to update their
data. 

usage:

$ python ingest.py


assign
------------------

This module sets up assignments for the secret santakkuh exchange.
It will run the assignment algorithm as many times as needed to create a
closed loop where every participant gets an assigned to be some one's
secret santakkuh and every participant is assigned a secret santakkuh. 

You can debug using the --verbose flag (WARNING: This will print out who has
been assigned to who as it goes, so be careful if you don't want spoilers)

usage:

$ python assign.py
or
$ python assign.py --verbose


send_emails
------------------

Once participants have been given assignments, use this module to send
emails detailing who they have been assigned to as secret santakkuh and
their person's likes/dislikes/allergies, etc.

You can di this in bulk by passing in no arguments, or to a single
person by passing in their email address.

When sent in bulk, emails will only be sent if that participants "email_sent" 
flag has not been set to 'Y' (meaning their email was already sent)

If specifying a single email address, the email will be sent regardless of
this flag

usage:
$ python send_emails.py
or
$ python send_emails.py bmorin@industrydive.com

+================+
 	Testing
+================+

Run tests with nose:

$ nosetests

