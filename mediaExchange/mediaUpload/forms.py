from django import forms

from mediaExchange.items.models import Audio, ItemInstance, Movie, Season

class UploadForm(forms.Form):
    name = forms.CharField(label='Title', max_length=256)
    file = forms.FileField(label='File', required=False)
    tar = forms.BooleanField(label='Tarfile', required=False)
    dlLinks = forms.CharField(label='Download Links (comma separeted list)', required=False)
    dlLinksFile = forms.FileField(label='Download Links File (seperated by line breaks)', required=False)
    keyfile = forms.FileField(label='Key File', required=False)
    size = forms.IntegerField(label='Size (in bytes)', required=False)

#class MovieUploadForm(UploadForm):
#    subname = forms.CharField(label='Subtitle', max_length=256, required=False)
#    language = forms.CharField(label='Language', max_length=256, required=False)
#    year = forms.CharField(label='Year', max_length=4, required=False)
#    genre = forms.CharField(label='Genre', max_length=256, required=False)
#    source = forms.CharField(label='Source', max_length=256, required=False)
#
#class SeriesUploadForm(UploadForm):
#    subname = forms.CharField(label='Subtitle', max_length=256, required=False)
#    number = forms.IntegerField(label='Season Number', required=True)
#    language = forms.CharField(label='Language', max_length=256, required=False)
#    year = forms.CharField(label='Year', max_length=4, required=False)
#    genre = forms.CharField(label='Genre', max_length=256, required=False)
#    source = forms.CharField(label='Source', max_length=256, required=False)
#
#class AudioUploadForm(UploadForm):
#    artist = forms.CharField(label='Artist', max_length=256)
#    year = forms.CharField(label='Year', max_length=4, required=False)
#    genre = forms.CharField(label='Genre', max_length=256, required=False)
#    language = forms.CharField(label='Language', max_length=256, required=False)
#    source = forms.CharField(label='Source', max_length=256, required=False)

class FileUploadForm(forms.Form):
    file = forms.FileField(label='File')
    tar = forms.BooleanField(label='Tarfile', required=False)
    keyfile = forms.FileField(label='Key File')

class LinkUploadForm(forms.Form):
#    dlLinks = forms.CharField(label='Download Links (comma separeted list)', required=False)
    dlLinksFile = forms.FileField(label='Download Links File (seperated by line breaks)')
    keyfile = forms.FileField(label='Key File')
    size = forms.IntegerField(label='Size (in bytes)', required=False)

class MovieUploadForm(forms.ModelForm):

    class Meta:
        model = Movie
        fields = ('name', 'subname', 'year', 'genres')

class SeriesUploadForm(forms.ModelForm):

    class Meta:
        model = Season
        fields = ('name', 'subname', 'number', 'year', 'genres')

class AudioUploadForm(forms.ModelForm):

    class Meta:
        model = Audio
        fields = ('name', 'artist', 'year', 'genres')

class ItemInstanceForm(forms.ModelForm):

    class Meta:
        model = ItemInstance
        fields = ('source', 'language', 'size')
