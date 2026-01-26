from django.db import models

# Create your models here.

class JobSource(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, default='website')
    url = models.URLField(max_length=500)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.name}"

class JobPost(models.Model):
    #This links the post to a source
    #if the source is deleted, 'on_delete=models.CASCADE' deletes the posts too

    source = models.ForeignKey('JobSource', on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    date_posted = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    url = models.URLField(max_length=500)


