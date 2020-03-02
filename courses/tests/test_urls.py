from django.test import TestCase
from django.urls import resolve


class UrlsTest(TestCase):
    def test_infer_course_navigation_url(self):
        resolver = resolve('/courses/c152/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')

        resolver = resolve('/courses/ABC/123/456/789/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

    def test_infer_chapter_navigation_url(self):
        resolver = resolve('/courses/c152/lessons/ch153')
        self.assertEqual(resolver.view_name, 'infer_chapter_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['chapter_id'], 'ch153')

        resolver = resolve('/courses/ABC/123/456/789/lessons/XYZ/987/654/321')
        self.assertEqual(resolver.view_name, 'infer_chapter_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['chapter_id'], 'XYZ/987/654/321')

        resolver = resolve(
            '/courses/edX/Open_DemoX/edx_demo_course/lessons/i4x://edX/Open_DemoX/chapter/interactive_demonstrations')
        self.assertEqual(resolver.view_name, 'infer_chapter_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['chapter_id'], 'i4x://edX/Open_DemoX/chapter/interactive_demonstrations')

    def test_infer_page_navigation_url(self):
        resolver = resolve('/courses/c152/lessons/jump_to_page/ch153')
        self.assertEqual(resolver.view_name, 'infer_page_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['page_id'], 'ch153')

        resolver = resolve('/courses/ABC/123/456/789/lessons/jump_to_page/XYZ/987/654/321')
        self.assertEqual(resolver.view_name, 'infer_page_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['page_id'], 'XYZ/987/654/321')

        resolver = resolve(
            '/courses/edX/Open_DemoX/edx_demo_course/lessons/jump_to_page/i4x://edX/Open_DemoX/page/'
            'interactive_demonstrations'
        )
        self.assertEqual(resolver.view_name, 'infer_page_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['page_id'], 'i4x://edX/Open_DemoX/page/interactive_demonstrations')

    def test_navigate_to_lesson_module_url(self):
        resolver = resolve('/courses/c152/lessons/ch153/module/p154')
        self.assertEqual(resolver.view_name, 'navigate_to_lesson_module')
        self.assertEqual(resolver.kwargs['course_id'], 'c152')
        self.assertEqual(resolver.kwargs['chapter_id'], 'ch153')
        self.assertEqual(resolver.kwargs['page_id'], 'p154')

        resolver = resolve('/courses/ABC/123/456/789/lessons/XYZ/987/654/321/module/LMN/ZXC/LAKSJDFLASKJFLWE/444')
        self.assertEqual(resolver.view_name, 'navigate_to_lesson_module')
        self.assertEqual(resolver.kwargs['course_id'], 'ABC/123/456/789')
        self.assertEqual(resolver.kwargs['chapter_id'], 'XYZ/987/654/321')
        self.assertEqual(resolver.kwargs['page_id'], 'LMN/ZXC/LAKSJDFLASKJFLWE/444')

        resolver = resolve(
            '/courses/edX/Open_DemoX/edx_demo_course/lessons/i4x://edX/Open_DemoX/chapter/'
            'd8a6192ade314473a78242dfeedfbf5b/module/i4x://edX/Open_DemoX/sequential/edx_introduction'
        )
        self.assertEqual(resolver.view_name, 'navigate_to_lesson_module')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
        self.assertEqual(resolver.kwargs['chapter_id'], 'i4x://edX/Open_DemoX/chapter/d8a6192ade314473a78242dfeedfbf5b')
        self.assertEqual(resolver.kwargs['page_id'], 'i4x://edX/Open_DemoX/sequential/edx_introduction')

    def test_navigate_to_page_url(self):
        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/lessons')
        self.assertEqual(resolver.view_name, 'infer_course_navigation')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/overview')
        self.assertEqual(resolver.view_name, 'course_overview')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/announcements')
        self.assertEqual(resolver.view_name, 'course_news')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')

        resolver = resolve('/courses/edX/Open_DemoX/edx_demo_course/resources')
        self.assertEqual(resolver.view_name, 'course_resources')
        self.assertEqual(resolver.kwargs['course_id'], 'edX/Open_DemoX/edx_demo_course')
