from mediaExchange.items.models import Language, Genre, Source, DownloadFile, DownloadFileGroup, ItemRequest, UploadRequest, Vote, EncryptionKey, Rating, Comment, ItemInstance
from django.contrib import admin

admin.site.register(Language)
admin.site.register(Genre)
admin.site.register(Source)
admin.site.register(DownloadFileGroup)
admin.site.register(DownloadFile)
admin.site.register(ItemRequest)
admin.site.register(UploadRequest)
admin.site.register(Vote)
admin.site.register(EncryptionKey)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(ItemInstance)
