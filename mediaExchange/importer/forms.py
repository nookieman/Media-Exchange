from django import forms

class ImportForm(forms.Form):
    file = forms.FileField(label='Import File')
