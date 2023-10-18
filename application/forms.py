from django import forms

class UploadPDFForm(forms.Form):
    birth_certificate_pdf = forms.FileField()