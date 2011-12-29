from django import forms


class UploadForm(forms.Form):
    name = forms.CharField(label='Title', max_length=256)
    file = forms.FileField(label='File')
    tar = forms.BooleanField(label='Tarfile', required=False)

class MovieUploadForm(UploadForm):
    subname = forms.CharField(label='Subtitle', max_length=256, required=False)
    language = forms.CharField(label='Language', max_length=256, required=False)
    year = forms.CharField(label='Year', max_length=4, required=False)
    genre = forms.CharField(label='Genre', max_length=256, required=False)
    source = forms.CharField(label='Source', max_length=256, required=False)

class SeriesUploadForm(UploadForm):
    subname = forms.CharField(label='Subtitle', max_length=256, required=False)
    number = forms.IntegerField(label='Season Number', required=True)
    language = forms.CharField(label='Language', max_length=256, required=False)
    year = forms.CharField(label='Year', max_length=4, required=False)
    genre = forms.CharField(label='Genre', max_length=256, required=False)
    source = forms.CharField(label='Source', max_length=256, required=False)

