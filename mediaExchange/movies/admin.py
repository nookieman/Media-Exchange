from mediaExchange.movies.models import Movie, Language, MovieGenre, MovieSource, DownloadFile, DownloadFileGroup, ItemRequest, UploadRequest, Vote, EncryptionKey
from django.contrib import admin

admin.site.register(Movie)
admin.site.register(Language)
admin.site.register(MovieGenre)
admin.site.register(MovieSource)
admin.site.register(DownloadFileGroup)
admin.site.register(DownloadFile)
admin.site.register(ItemRequest)
admin.site.register(UploadRequest)
admin.site.register(Vote)
admin.site.register(EncryptionKey)
