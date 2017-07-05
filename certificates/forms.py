"""
Forms related to Certificates models
"""
from django import forms

from api_client import course_api

from .models import CertificateTemplateAsset, CertificateTemplate
from .controller import get_courses_choice_list
from util.validators import AlphanumericWithAccentedChars


class CertificateTemplateAssetForm(forms.ModelForm):
    """
    Form for certificate template assets
    """
    def __init__(self, *args, **kwargs):
        """
        Initializer for certificate template asset form, adding description validator
        """
        super(CertificateTemplateAssetForm, self).__init__(*args, **kwargs)
        self.fields['description'].validators.append(AlphanumericWithAccentedChars())


    class Meta:
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
        super(CertificateTemplateForm, self).__init__(*args, **kwargs)
        self.fields['course_id'] = forms.ChoiceField(
            choices=get_courses_choice_list()
        )
        self.fields['name'].validators.append(AlphanumericWithAccentedChars())
        self.fields['description'].validators.append(AlphanumericWithAccentedChars())

    class Meta:
        """
        Form meta class to set model meta options
        """
        model = CertificateTemplate
        fields = ('name', 'description', 'template', 'course_id')
