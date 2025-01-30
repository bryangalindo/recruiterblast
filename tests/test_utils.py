from unittest import TestCase, mock

from parameterized import parameterized

from recruiterblast.models import Employee
from recruiterblast.utils import (
    generate_formatted_employee_email,
    generate_rocketreach_formatted_username,
)


class UtilsTest(TestCase):
    def setUp(self):
        self.employee = Employee(first_name="foo", last_name="bar")

    @parameterized.expand(
        [
            ("first_last", "FirstLast@gitlab.com", "foobar@gitlab.com"),
            ("f_last", "FLast@gitlab.com", "fbar@gitlab.com"),
            ("first_l", "FirstL@gitlab.com", "foob@gitlab.com"),
            ("f_l", "FL@gitlab.com", "fb@gitlab.com"),
            ("first_dot_l", "First.L@gitlab.com", "foo.b@gitlab.com"),
            ("first_dot_last", "First.Last@gitlab.com", "foo.bar@gitlab.com"),
            ("case_insensitivity", "fLaSt@GitLab.COM", "fbar@gitlab.com"),
        ]
    )
    def test_generate_employee_email(self, name, input_format, expected_output):
        print(name)
        self.assertEqual(
            expected_output,
            generate_formatted_employee_email(self.employee, input_format),
        )

    @parameterized.expand(
        [
            ("full_format", "[first].[last]", "foo.bar"),
            ("initial_format", "[first_initial][last_initial]", "fb"),
            ("underscore_format", "[first]_[last_initial]", "foo_b"),
        ]
    )
    def test_generate_rocketreach_formatted_username(self, name, format, expected):
        actual = generate_rocketreach_formatted_username(self.employee, format)
        self.assertEqual(expected, actual)
