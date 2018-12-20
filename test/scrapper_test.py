import json
import unittest
from subprocess import Popen, PIPE


class ScrapperTest(unittest.TestCase):
    def setUp(self):
        self.x12_url = 'http://www.x12.org/codes/claim-adjustment-reason-codes/'
        self.rarc_url = 'http://www.wpc-edi.com/reference/codelists/healthcare/remittance-advice-remark-codes/'
        self.script_path = '../app/x12_codes_scrapper.py'

    def test_x12_codes(self):
        output, err = Popen(['python', self.script_path, self.x12_url], stdout=PIPE).communicate()

        self.validate_json_output(err, output)

    def test_x12_started_eq(self):
        output, err = Popen(['python', self.script_path, self.x12_url, '-started', '11/01/2017'], stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertEqual(len(output_json), 20)

    def test_x12_started_eq_greater(self):
        output, err = Popen(['python', self.script_path, self.x12_url, '-started', '10/01/2017'], stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertEqual(len(output_json), 20)

    def test_x12_started_no_data(self):
        output, err = Popen(['python', self.script_path, self.x12_url, '-started', '10/01/2022'], stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertEqual(len(output_json), 0)

    def test_rarc_started_eq(self):
        output, err = Popen(['python', self.script_path, self.rarc_url, '-started', '07/01/2018'],
                            stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertEqual(len(output_json), 5)

    def test_rarc_started_eq_greater(self):
        output, err = Popen(['python', self.script_path, self.rarc_url, '-started', '06/01/2018'],
                            stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertEqual(len(output_json), 5)

    def test_rarc_started_no_data(self):
        output, err = Popen(['python', self.script_path, self.rarc_url, '-started', '10/01/2022'],
                            stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertEqual(len(output_json), 0)

    def test_rarc_codes(self):
        output, err = Popen(['python', self.script_path, self.rarc_url], stdout=PIPE).communicate()

        self.validate_json_output(err, output)

    def validate_json_output(self, err, output):
        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        output_json = json.loads(output)
        self.assertIsNotNone(output_json)
        self.assertGreater(len(output_json), 0)
        self.assertTrue(all(item.get('code') and item.get('description') for item in output_json),
                        "JSON in a wrong format")
        self.assertTrue(all('Alerts' not in item.get('description') for item in output_json),
                        "Description should not contain \'Alert\'")
        self.assertTrue(all('Notes: (Modified' not in item.get('description') for item in output_json),
                        "Description should not contain \'Notes: (Modified ...\'")
        self.assertTrue(all('Start' not in item.get('description') for item in output_json),
                        "Description should not contain \'Start\'")
        self.assertTrue(all('Last Modified' not in item.get('description') for item in output_json),
                        "Description should not contain \'Last Modified\'")

    def test_x12_started_modified(self):
        start_only_output, err_start = Popen(['python', self.script_path, self.rarc_url, '-started', '11/01/2013'], stdout=PIPE).communicate()
        modify_only_output, err_modify = Popen(['python', self.script_path, self.rarc_url, '-modified', '03/14/2014'], stdout=PIPE).communicate()
        output, err = Popen(['python', self.script_path, self.rarc_url, '-started', '11/01/2013', '-modified', '03/14/2014'], stdout=PIPE).communicate()

        self.assertIsNone(err, "Error occurred. {err}".format(err=err))
        self.assertIsNone(err_start, "Error occurred. {err}".format(err=err_start))
        self.assertIsNone(err_modify, "Error occurred. {err}".format(err=err_modify))

        start_only_json = json.loads(start_only_output)
        modify_only_json = json.loads(modify_only_output)

        start_only_codes = set(map(lambda item: item.get('code'), start_only_json))
        modify_only_codes = set(map(lambda item: item.get('code'), modify_only_json))

        expected_codes = start_only_codes.intersection(modify_only_codes)

        output_json = json.loads(output)
        self.assertIsNotNone(output_json)

        actual_codes = set(map(lambda item: item.get('code'), output_json))

        self.assertEqual(expected_codes, actual_codes)



