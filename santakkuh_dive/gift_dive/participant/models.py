from django.db import models
from django.contrib.auth.models import User


class Participant(models.Model):
    participation_year = models.IntegerField()
    user = models.OneToOneField(User, related_name="profile", on_delete='cascade')
    display_name = models.CharField(max_length=75, null=True)
    likes = models.CharField(max_length=500)
    dislikes = models.CharField(max_length=500)
    allergies = models.CharField(max_length=500)

    class Meta:
        unique_together = (('participation_year', 'user'),)

    def __str__(self):
        return ('%s, "%s", %d') % (self.user.username, self.display_name, self.participation_year)


class Assignment(models.Model):
    participation_year = models.IntegerField()
    giver = models.ForeignKey(Participant, on_delete='cascade', related_name='giver')
    recipient = models.ForeignKey(Participant, on_delete='cascade', related_name='recipient')

    class Meta:
        unique_together = (('participation_year', 'giver', 'recipient'))

    def __str__(self):
        return ('Assignment (giver: %s)' % self.giver.display_name)
