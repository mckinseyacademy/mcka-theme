from django.test import TestCase
from license import controller


# Create your tests here.
class TestLicenses(TestCase):
    def test_license_creation(self):
        # grant 1 license to course 1 on behalf of organisation 11
        controller.create_licenses(1, 11, 1)

        allocated, assigned = controller.licenses_report(1, 11)
        self.assertEqual(allocated, 1)
        self.assertEqual(assigned, 0)

        assigned_licenses = controller.assigned_licenses(1, 11)
        self.assertEqual(len(assigned_licenses), 0)

        # assign the license to user 101
        license = controller.assign_license(1, 11, 101)
        self.assertEqual(license.granted_id, 1)
        self.assertEqual(license.grantor_id, 11)
        self.assertEqual(license.grantee_id, 101)

        assigned_licenses = controller.assigned_licenses(1, 11)
        self.assertEqual(len(assigned_licenses), 1)

        allocated, assigned = controller.licenses_report(1, 11)
        self.assertEqual(allocated, 1)
        self.assertEqual(assigned, 1)

        # now try to assign another, should fail
        with self.assertRaises(controller.NoAvailableLicensesError):
            license2 = controller.assign_license(1, 11, 102)

        allocated, assigned = controller.licenses_report(1, 11)
        self.assertEqual(allocated, 1)
        self.assertEqual(assigned, 1)

        # now revoke license for user 101
        controller.revoke_license(1, 11, 101)
        allocated, assigned = controller.licenses_report(1, 11)
        self.assertEqual(allocated, 1)
        self.assertEqual(assigned, 0)

        # and now we should be able to assign to other user
        license2 = controller.assign_license(1, 11, 102)
        self.assertEqual(license2.granted_id, 1)
        self.assertEqual(license2.grantor_id, 11)
        self.assertEqual(license2.grantee_id, 102)

        allocated, assigned = controller.licenses_report(1, 11)
        self.assertEqual(allocated, 1)
        self.assertEqual(assigned, 1)

    def test_many_licenses(self):
        controller.create_licenses(2, 12, 100)

        allocated, assigned = controller.licenses_report(2, 12)
        self.assertEqual(allocated, 100)
        self.assertEqual(assigned, 0)

        assigned_licenses = controller.assigned_licenses(2, 12)
        self.assertEqual(len(assigned_licenses), 0)

        for x in range(1, 101):
            controller.assign_license(2, 12, x + 100)
            allocated, assigned = controller.licenses_report(2, 12)
            self.assertEqual(allocated, 100)
            self.assertEqual(assigned, x)

        assigned_licenses = controller.assigned_licenses(2, 12)
        self.assertEqual(len(assigned_licenses), 100)

        with self.assertRaises(controller.NoAvailableLicensesError):
            controller.assign_license(2, 12, 201)

        allocated, assigned = controller.licenses_report(2, 12)
        self.assertEqual(allocated, 100)
        self.assertEqual(assigned, 100)

        # revoke form somewhere in the middle of the pack
        controller.revoke_license(2, 12, 155)

        allocated, assigned = controller.licenses_report(2, 12)
        self.assertEqual(allocated, 100)
        self.assertEqual(assigned, 99)

        # should be able to grab that extra one now
        license = controller.assign_license(2, 12, 201)
        self.assertEqual(license.granted_id, 2)
        self.assertEqual(license.grantor_id, 12)
        self.assertEqual(license.grantee_id, 201)

        allocated, assigned = controller.licenses_report(2, 12)
        self.assertEqual(allocated, 100)
        self.assertEqual(assigned, 100)

    def test_already_licensed(self):
        licensor = controller.LicenseBroker(3, 13)
        licensor.create(1)

        # assign to a user
        licensor.assign(101)

        with self.assertRaises(controller.NoAvailableLicensesError):
            licensor.assign(102)

        # try to assign when already assigned, should be okay
        licensor.assign(101)
