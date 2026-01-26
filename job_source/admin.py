from django.contrib import admin
from .models import JobSource, JobPost
# Register your models here.

@admin.register(JobSource)
class JobSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'active')
    search_fields = ('name', 'url')
    list_filter = ('active',)

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'date_posted', 'source')
    search_fields = ('title', 'company', 'location')
    list_filter = ('source', 'date_posted')

#admin.site.register(JobSource)