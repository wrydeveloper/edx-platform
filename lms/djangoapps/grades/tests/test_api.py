""" Tests calling the grades api directly """

from __future__ import absolute_import

import ddt
from mock import patch

from lms.djangoapps.grades import api
from lms.djangoapps.grades.models import (
    PersistentSubsectionGrade,
    PersistentSubsectionGradeOverride,
)
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


@ddt.ddt
class GradesServiceTests(ModuleStoreTestCase):
    """
    Tests for the Grades service
    """

    def setUp(self):
        super(GradesServiceTests, self).setUp()
        self.course = CourseFactory.create(org='edX', number='DemoX', display_name='Demo_Course', run='Spring2019')
        self.subsection = ItemFactory.create(parent=self.course, category="subsection", display_name="Subsection")
        self.user = UserFactory()
        self.overriding_user = UserFactory()
        self.grade = PersistentSubsectionGrade.update_or_create_grade(
            user_id=self.user.id,
            course_id=self.course.id,
            usage_key=self.subsection.location,
            first_attempted=None,
            visible_blocks=[],
            earned_all=6.0,
            possible_all=6.0,
            earned_graded=5.0,
            possible_graded=5.0
        )
        self.signal_patcher = patch('lms.djangoapps.grades.signals.signals.SUBSECTION_OVERRIDE_CHANGED.send')
        self.mock_signal = self.signal_patcher.start()
        self.id_patcher = patch('lms.djangoapps.grades.api.create_new_event_transaction_id')
        self.mock_create_id = self.id_patcher.start()
        self.mock_create_id.return_value = 1
        self.type_patcher = patch('lms.djangoapps.grades.api.set_event_transaction_type')
        self.mock_set_type = self.type_patcher.start()

    def tearDown(self):
        super(GradesServiceTests, self).tearDown()
        PersistentSubsectionGradeOverride.objects.all().delete()  # clear out all previous overrides
        self.signal_patcher.stop()
        self.id_patcher.stop()
        self.type_patcher.stop()

    @ddt.data(0.0, None, 3.0)
    def test_override_subsection_grade(self, earned_graded):
        api.override_subsection_grade(
            self.user.id,
            self.course.id,
            self.subsection.location,
            overrider=self.overriding_user,
            earned_graded=earned_graded,
            comment='Test Override Comment',
        )
        override_obj = api.get_subsection_grade_override(
            self.user.id,
            self.course.id,
            self.subsection.location
        )
        self.assertIsNotNone(override_obj)
        self.assertEqual(override_obj.earned_graded_override, earned_graded)
        self.assertEqual(override_obj.override_reason, 'Test Override Comment')

        for i in range(3):
            override_obj.override_reason = 'this field purposefully left blank'
            override_obj.earned_graded_override = i
            override_obj.save()

        api.override_subsection_grade(
            self.user.id,
            self.course.id,
            self.subsection.location,
            overrider=self.overriding_user,
            earned_graded=earned_graded,
            comment='Test Override Comment 2',
        )
        override_obj = api.get_subsection_grade_override(
            self.user.id,
            self.course.id,
            self.subsection.location
        )

        self.assertIsNotNone(override_obj)
        self.assertEqual(override_obj.earned_graded_override, earned_graded)
        self.assertEqual(override_obj.override_reason, 'Test Override Comment 2')

        self.assertEqual(5, len(override_obj.history.all()))
        for history_entry in override_obj.history.all():
            if history_entry.override_reason.startswith('Test Override Comment'):
                self.assertEquals(self.overriding_user, history_entry.history_user)
                self.assertEquals(self.overriding_user.id, history_entry.history_user_id)
            else:
                self.assertIsNone(history_entry.history_user)
                self.assertIsNone(history_entry.history_user_id)
