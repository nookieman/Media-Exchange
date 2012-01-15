from django import forms

class AddItemUploadForm(forms.Form):
    dlLinks = forms.CharField(label='Download Links (comma separeted list)', required=False)
    dlLinksFile = forms.FileField(label='Download Links File (seperated by line breaks)', required=False)
    keyfile = forms.FileField(label='Key File', required=True)
