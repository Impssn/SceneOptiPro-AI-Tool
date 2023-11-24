# image_to_essay/forms.py

from django import forms
from .models import ImageEssay

class ImageEssayForm(forms.ModelForm):
    class Meta:
        model = ImageEssay
        fields = ['image']
