from django.db import models

# Create your models here.
from django.db import models

class ImageEssay(models.Model):
    image = models.ImageField(upload_to='images/')
    essay = models.TextField(blank=True, null=True)
