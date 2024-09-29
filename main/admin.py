from django.contrib import admin

# Register your models here.
from django.contrib import admin
from main.models import  Reaction, CustomUser, SearchQuery, ShownVideo

admin.site.register(Reaction)
admin.site.register(CustomUser)
admin.site.register(SearchQuery)
admin.site.register(ShownVideo)
