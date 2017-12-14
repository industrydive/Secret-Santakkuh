from django.contrib import admin

from .models import Participant, Assignment
from django import forms


class ParticipantForm(forms.ModelForm):
    # likes = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Participant
        fields = [
            'display_name',
            'likes',
            'dislikes',
            'allergies',
        ]


class ParticipantAdmin(admin.ModelAdmin):
    form = ParticipantForm
    ordering = ('display_name', )


admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Assignment)
