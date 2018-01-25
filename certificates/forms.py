"""
Forms related to Certificates models
"""
from django import forms

from util.validators import AlphanumericWithAccentedChars

from .models import CertificateTemplateAsset, CertificateTemplate
from .controller import get_courses_choice_list


class CertificateTemplateAssetForm(forms.ModelForm):
    """
    Form for certificate template assets
    """
    def __init__(self, *args, **kwargs):
        """
        Initializer for certificate template asset form
        adding validator for description field
        """
        super(CertificateTemplateAssetForm, self).__init__(*args, **kwargs)
        self.fields['description'].validators.append(
            AlphanumericWithAccentedChars()
        )

    class Meta(object):
        """
        Form meta class to set model meta options
        """
        model = CertificateTemplateAsset
        fields = ('description', 'asset', )


class CertificateTemplateForm(forms.ModelForm):
    """
    Form for certificate template
    """
    def __init__(self, *args, **kwargs):
        """
        Initializer for certificate template form, adding course ids choice list
        """
        request = kwargs.pop('request', None)
        course_choices = get_courses_choice_list(request)

        super(CertificateTemplateForm, self).__init__(*args, **kwargs)
        self.fields['course_id'] = forms.ChoiceField(
            choices=course_choices
        )
        self.fields['name'].validators.append(AlphanumericWithAccentedChars())
        self.fields['description'].validators.append(
            AlphanumericWithAccentedChars()
        )

    class Meta(object):
        """
        Form meta class to set model meta options
        """
        model = CertificateTemplate
        fields = ('name', 'description', 'template', 'course_id')
