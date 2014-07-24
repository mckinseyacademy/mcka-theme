from django.test import TestCase

from .util import LegacyIdConvert

class LegacyIdsTest(TestCase):

    def test_legacy_from_new_course(self):
        new_format = "slashes:Me+MY101+2014_1"
        old_format = "Me/MY101/2014_1"

        self.assertEqual(old_format, LegacyIdConvert.legacy_from_new(new_format))

    def test_legacy_from_new_chapter(self):
        new_format = "location:Me+MY101+2014_1+chapter+01d1c90e6588470b821142474f504c58"
        old_format = "i4x://Me/MY101/chapter/01d1c90e6588470b821142474f504c58"

        self.assertEqual(old_format, LegacyIdConvert.legacy_from_new(new_format))

    def test_legacy_from_new_page(self):
        new_format = "location:Me+MY101+2014_1+vertical+345ebe791ee4494f963420cac9c6d7a6"
        old_format = "i4x://Me/MY101/vertical/345ebe791ee4494f963420cac9c6d7a6"

        self.assertEqual(old_format, LegacyIdConvert.legacy_from_new(new_format))

    def test_new_from_legacy_course(self):
        new_format = "slashes:Me+MY101+2014_1"
        old_format = "Me/MY101/2014_1"
        old_course = "Me/MY101/2014_1"

        self.assertEqual(new_format, LegacyIdConvert.new_from_legacy(old_format, old_course))

    def test_new_from_legacy_chapter(self):
        new_format = "location:Me+MY101+2014_1+chapter+01d1c90e6588470b821142474f504c58"
        old_format = "i4x://Me/MY101/chapter/01d1c90e6588470b821142474f504c58"
        old_course = "Me/MY101/2014_1"

        self.assertEqual(new_format, LegacyIdConvert.new_from_legacy(old_format, old_course))

    def test_new_from_legacy_page(self):
        new_format = "location:Me+MY101+2014_1+vertical+345ebe791ee4494f963420cac9c6d7a6"
        old_format = "i4x://Me/MY101/vertical/345ebe791ee4494f963420cac9c6d7a6"
        old_course = "Me/MY101/2014_1"

        self.assertEqual(new_format, LegacyIdConvert.new_from_legacy(old_format, old_course))

    def test_legacy_from_new_course_already(self):
        new_format = "Me/MY101/2014_1"
        old_format = "Me/MY101/2014_1"

        self.assertEqual(old_format, LegacyIdConvert.legacy_from_new(new_format))

    def test_legacy_from_new_chapter_already(self):
        new_format = "i4x://Me/MY101/chapter/01d1c90e6588470b821142474f504c58"
        old_format = "i4x://Me/MY101/chapter/01d1c90e6588470b821142474f504c58"

        self.assertEqual(old_format, LegacyIdConvert.legacy_from_new(new_format))

    def test_new_from_legacy_course_already(self):
        new_format = "slashes:Me+MY101+2014_1"
        old_format = "slashes:Me+MY101+2014_1"
        old_course = "slashes:Me+MY101+2014_1"

        self.assertEqual(new_format, LegacyIdConvert.new_from_legacy(old_format, old_course))

    def test_new_from_legacy_chapter_already(self):
        new_format = "location:Me+MY101+2014_1+chapter+01d1c90e6588470b821142474f504c58"
        old_format = "location:Me+MY101+2014_1+chapter+01d1c90e6588470b821142474f504c58"
        old_course = "slashes:Me+MY101+2014_1"

        self.assertEqual(new_format, LegacyIdConvert.new_from_legacy(old_format, old_course))
