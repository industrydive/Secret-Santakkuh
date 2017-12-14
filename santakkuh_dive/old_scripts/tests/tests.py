import sqlite3
from unittest import TestCase
from santakkuh_dive import test_settings as settings
from santakkuh_dive.setupdb import destroy_db, create_db
from santakkuh_dive.ingest import parse_csv_into_sqlite
from santakkuh_dive.assign import _check_is_closed_loop, assign_participants


class DBTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.connection = sqlite3.connect(settings.SQLITE_FILENAME)
        create_db(cls.connection)
        parse_csv_into_sqlite(cls.connection, settings.SOURCE_FILE, settings.YEAR)
        cls.known_test_participants = {
            'Thor': ['thor@avengers.com', "trickery", '"hammers, storms"'],
            'Captain America': ['cap@avengers.com', '', '"motorcycles, olden timey music"'],
            'Black Widow': ['natr@averngers.com', '', '"spandex, gadgets"'],
            'Hulk': ['aliureghlig@avengers.com', 'puny banner', 'smash'],
            'Black Panther': ['kingofwakanda@wakanda.gov', 'dogs', '"cats, spandex, gadgets"'],
            'Vision': ['vis@avengers.com', 'privacy', 'cook books'],
        }  # i just know this

    @classmethod
    def tearDownClass(cls):
        destroy_db(cls.connection)

    def test_ingestion(self):

        test_sql = "SELECT name, email, dislikes, likes FROM participants WHERE year = %d" % settings.YEAR
        db_rows = {}
        for row in self.connection.cursor().execute(test_sql):
            db_rows[row[0]] = [row[1], row[2], row[3]]
        for known_participant in self.known_test_participants:
            self.assertTrue(known_participant in db_rows)

    def end_to_end_test(self):
        assign_participants(self.connection, settings.YEAR)
        test_select_sql = """
            select pg.name, pr.name as giver
            from assignments a
            join participants pg on a.giver_id = pg.id
            join participants pr on a.recipient_id = pr.id
        """

        assignments = {}
        for row in self.connection.cursor().execute(test_select_sql):
            assignments[row[0]] = row[1]
        self.assertEqual(len(assignments), len(self.known_test_participants))
        for participant in self.known_test_participants:
            self.assertTrue(participant in assignments.keys())
            self.assertTrue(participant in [recipient for k, recipient in assignments.iteritems()])


class AssignmentUtilsTestCase(TestCase):
    def test_check_is_closed_loop(self):

        # edges: 1->6->5->->2->3->4->1
        known_closed_loop = {
            1: 6,
            2: 3,
            3: 4,
            4: 1,
            5: 2,
            6: 5,
        }
        self.assertTrue(_check_is_closed_loop(known_closed_loop))

        # edges: 1->6->5->1 2->3->4->2->3
        known_closed_loop = {
            1: 6,
            2: 3,
            3: 4,
            4: 2,
            5: 1,
            6: 5,
        }
        self.assertFalse(_check_is_closed_loop(known_closed_loop))
