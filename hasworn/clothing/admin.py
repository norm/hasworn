from django.contrib import admin

from .models import Clothing, Wearing, Worn


class ClothingAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Clothing, ClothingAdmin)
admin.site.register(Wearing)
admin.site.register(Worn)
