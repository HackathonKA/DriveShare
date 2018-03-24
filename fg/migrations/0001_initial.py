# Generated by Django 2.0.3 on 2018-03-24 14:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Carpool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('desc', models.CharField(max_length=500)),
                ('loc_a', models.CharField(max_length=250)),
                ('loc_b', models.CharField(max_length=250)),
                ('active', models.BooleanField(default=True)),
                ('days', multiselectfield.db.fields.MultiSelectField(choices=[('mon', 'Monday'), ('tue', 'Tuesday'), ('wen', 'Wendsday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturady'), ('sun', 'Sunday')], max_length=27)),
            ],
        ),
        migrations.CreateModel(
            name='Timeframe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.TimeField()),
                ('end', models.TimeField()),
                ('trip', models.CharField(choices=[('a', 'TripA'), ('b', 'TripB')], max_length=1)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]