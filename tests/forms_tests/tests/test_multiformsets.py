import collections
import unittest

from django import forms
from django.forms.utils import ErrorList
from django.forms.widgets import Media
from django.forms.formsets import MultiFormSet


class MultiFormSetTest(unittest.TestCase):
    class TestFormOne(forms.Form):
        char_field = forms.CharField()

    class TestFormTwo(forms.Form):
        int_field = forms.IntegerField()

    class TestFormThree(forms.Form):
        # Is multipart
        file_field = forms.FileField()

    def setUp(self):
        self.forms = (
            MultiFormSetTest.TestFormOne,
            MultiFormSetTest.TestFormTwo
        )

    def test__init__(self):
        form_set = MultiFormSet(
            forms=forms,
        )

        self.assertFalse(form_set.is_bound)
        self.assertEqual(form_set.prefix, 'form')
        self.assertEqual(form_set.auto_id, 'id_%s')
        self.assertEqual(form_set.defaults, {})
        self.assertEqual(form_set.data, {})
        self.assertEqual(form_set.files, {})
        self.assertIsNone(form_set.initial)
        self.assertEqual(form_set.error_class, ErrorList)
        self.assertEqual(form_set._forms, forms)

    def test__init__with_non_defaults(self):
        form_set = MultiFormSet(
            forms=self.forms,
            defaults={"test": True},
            data={"char_field": "Test"},
            files={},
            auto_id="id-%s",
            prefix="multiformset",
            initial=[{"char_field": "Initial"}, ],
        )

        self.assertTrue(form_set.is_bound)
        self.assertEqual(form_set.prefix, 'multiformset')
        self.assertEqual(form_set.auto_id, 'id-%s')
        self.assertEqual(form_set.defaults, {"test": True})
        self.assertEqual(form_set.data, {"char_field": "Test"})
        self.assertEqual(form_set.files, {})
        self.assertEqual(form_set.initial, [{"char_field": "Initial"}])
        self.assertEqual(form_set.error_class, ErrorList)
        self.assertEqual(form_set._forms, self.forms)

    def test__str__(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertEqual(str(form_set), form_set.as_table())

    def test__iter__(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertTrue(isinstance(iter(form_set), collections.Iterable))
        for idx, form in enumerate(form_set):
            self.assertTrue(isinstance(form, self.forms[idx]))

    def test__getitem__(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )
        self.assertTrue(isinstance(form_set.__getitem__(0), self.forms[0]))

    def test__len__(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )
        self.assertEqual(len(form_set), 2)

    def test__bool__(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )
        self.assertTrue(bool(form_set))

    def test__nonzero__(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )
        self.assertTrue(form_set.__nonzero__())

    def test_forms(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )
        for instance, cls in zip(form_set.forms, self.forms):
            self.assertTrue(isinstance(instance, cls))

    def test_cleaned_data__invalid(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )
        with self.assertRaises(AttributeError):
            form_set.cleaned_data

    def test_cleaned_data(self):
        # With prefix
        data = {
            "form-0-char_field": "test",
            "form-1-int_field": 1,
        }
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        self.assertEqual(form_set.cleaned_data, [
            {
                "char_field": "test",
            },
            {
                "int_field": 1,
            }
        ])

    def test_get_default_prefix(self):
        self.assertEqual(MultiFormSet.get_default_prefix(), "form")

    def test_non_form_errors(self):
        # With prefix
        data = {
            "form-0-char_field": "test",
            "form-1-int_field": 1,
        }
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        self.assertEqual(form_set.non_form_errors(), [])
        self.assertTrue(isinstance(form_set.non_form_errors(), ErrorList))

    def test_errors(self):
        data = {}
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        self.assertEqual(form_set.errors, [
            {'char_field': [u'This field is required.']},
            {'int_field': [u'This field is required.']}
        ])

    def test_total_error_count(self):
        data = {}
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        self.assertEqual(form_set.total_error_count(), 2)

    def test_is_valid(self):
        # With prefix
        data = {
            "form-0-char_field": "test",
            "form-1-int_field": 1,
        }
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        self.assertTrue(form_set.is_valid())

    def test_is_valid__unbound(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertFalse(form_set.is_valid())

    def test_is_valid__one_error(self):
        # With prefix
        data = {
            "form-0-char_field": "test",
        }
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        self.assertFalse(form_set.is_valid())

    def test_full_clean(self):
        # With prefix
        data = {
            "form-0-char_field": "test",
            "form-1-int_field": 1,
        }
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        form_set.full_clean()
        # No errors
        self.assertEqual(form_set._errors, [{}, {}])
        self.assertEqual(form_set._non_form_errors, [])

    def test_full_clean__not_bound(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertIsNone(form_set.full_clean())
        self.assertEqual(form_set._errors, [])
        self.assertTrue(isinstance(form_set._non_form_errors, ErrorList))

    def test_full_clean__with_errors(self):
        # With prefix
        data = {}
        form_set = MultiFormSet(
            forms=self.forms,
            data=data,
        )

        form_set.full_clean()
        # No errors
        self.assertEqual(form_set._errors, [
            {'char_field': [u'This field is required.']},
            {'int_field': [u'This field is required.']}
        ])
        self.assertEqual(form_set._non_form_errors, [])

    def test_clean(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertIsNone(form_set.clean())

    def test_has_changed__no_change(self):
        initial = [
            {
                "char_field": "test",
            },
            {
                "int_field": 1,
            }
        ]
        # With prefix
        data = {
            "form-0-char_field": "test",
            "form-1-int_field": 1,
        }

        form_set = MultiFormSet(
            forms=self.forms,
            initial=initial,
            data=data,
        )

        self.assertFalse(form_set.has_changed())

    def test_has_changed__changed(self):
        initial = [
            {
                "char_field": "old",
            },
            {
                "int_field": 0,
            }
        ]
        # With prefix
        data = {
            "form-0-char_field": "test",
            "form-1-int_field": 1,
        }

        form_set = MultiFormSet(
            forms=self.forms,
            initial=initial,
            data=data,
        )

        self.assertTrue(form_set.has_changed())

    def test_add_fields(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertIsNone(form_set.add_fields(self.forms[0], 0))

    def test_add_prefix(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertEqual(form_set.add_prefix(0), "form-0")

    def test_is_multipart__not_multipart(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertFalse(form_set.is_multipart())

    def test_is_multipart(self):
        forms = (
            MultiFormSetTest.TestFormOne,
            MultiFormSetTest.TestFormTwo,
            MultiFormSetTest.TestFormThree,
        )

        form_set = MultiFormSet(
            forms=forms,
        )

        self.assertTrue(form_set.is_multipart())

    def test_media(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertTrue(isinstance(form_set.media, Media))

    def test_as_table(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertEqual(form_set.as_table(), '<tr><th><label for="id_form-0-char_field">Char field:</label></th><td><input id="id_form-0-char_field" name="form-0-char_field" type="text" /></td></tr> <tr><th><label for="id_form-1-int_field">Int field:</label></th><td><input id="id_form-1-int_field" name="form-1-int_field" type="number" /></td></tr>')

    def test_as_p(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertEqual(form_set.as_p(), '<p><label for="id_form-0-char_field">Char field:</label> <input id="id_form-0-char_field" name="form-0-char_field" type="text" /></p> <p><label for="id_form-1-int_field">Int field:</label> <input id="id_form-1-int_field" name="form-1-int_field" type="number" /></p>')

    def test_as_ul(self):
        form_set = MultiFormSet(
            forms=self.forms,
        )

        self.assertEqual(form_set.as_ul(), '<li><label for="id_form-0-char_field">Char field:</label> <input id="id_form-0-char_field" name="form-0-char_field" type="text" /></li> <li><label for="id_form-1-int_field">Int field:</label> <input id="id_form-1-int_field" name="form-1-int_field" type="number" /></li>')
