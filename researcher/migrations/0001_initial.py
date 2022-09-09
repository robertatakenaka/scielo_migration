# Generated by Django 3.2.12 on 2022-09-09 17:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('institution', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearcherAffiliation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Last update date')),
                ('link_begin_year', models.CharField(blank=True, max_length=4, null=True, verbose_name='Begin Year')),
                ('link_end_year', models.CharField(blank=True, max_length=4, null=True, verbose_name='End Year')),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='researcheraffiliation_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('institution', models.ManyToManyField(to='institution.Institution')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='researcheraffiliation_last_mod_user', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Researcher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Last update date')),
                ('surname', models.CharField(max_length=128, verbose_name='Surname')),
                ('given_names', models.CharField(max_length=128, verbose_name='Given names')),
                ('suffix', models.CharField(blank=True, max_length=128, null=True, verbose_name='Suffix')),
                ('orcid', models.CharField(blank=True, max_length=128, null=True, verbose_name='ORCID')),
                ('email', models.EmailField(blank=True, max_length=128, null=True, verbose_name='E-mail')),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='researcher_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='researcher_last_mod_user', to=settings.AUTH_USER_MODEL, verbose_name='Updater')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
