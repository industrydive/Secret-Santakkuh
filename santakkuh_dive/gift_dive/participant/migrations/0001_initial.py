# Generated by Django 2.0 on 2017-12-14 13:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participation_year', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participation_year', models.IntegerField()),
                ('display_name', models.CharField(max_length=75, null=True)),
                ('likes', models.CharField(max_length=500)),
                ('dislikes', models.CharField(max_length=500)),
                ('allergies', models.CharField(max_length=500)),
                ('user', models.OneToOneField(on_delete='cascade', related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='giver',
            field=models.ForeignKey(on_delete='cascade', related_name='giver', to='participant.Participant'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='recipient',
            field=models.ForeignKey(on_delete='cascade', related_name='recipient', to='participant.Participant'),
        ),
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together={('participation_year', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together={('participation_year', 'giver', 'recipient')},
        ),
    ]
