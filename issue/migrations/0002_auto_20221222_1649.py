# Generated by Django 3.2.12 on 2022-12-22 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0001_initial'),
        ('issue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='publication_date_text',
            field=models.CharField(max_length=255, null=True, verbose_name='Publication date text'),
        ),
        migrations.AddField(
            model_name='issue',
            name='publication_final_month_name',
            field=models.CharField(max_length=20, null=True, verbose_name='Publication final month name'),
        ),
        migrations.AddField(
            model_name='issue',
            name='publication_final_month_number',
            field=models.IntegerField(choices=[(1, 'JANUARY'), (2, 'FEBRUARY'), (3, 'MARCH'), (4, 'APRIL'), (5, 'MAY'), (6, 'JUNE'), (7, 'JULY'), (8, 'AUGUST'), (9, 'SEPTEMBER'), (10, 'OCTOBER'), (11, 'NOVEMBER'), (12, 'DECEMBER')], null=True, verbose_name='Publication final month number'),
        ),
        migrations.AddField(
            model_name='issue',
            name='publication_initial_month_name',
            field=models.CharField(max_length=20, null=True, verbose_name='Publication initial month name'),
        ),
        migrations.AddField(
            model_name='issue',
            name='publication_initial_month_number',
            field=models.IntegerField(choices=[(1, 'JANUARY'), (2, 'FEBRUARY'), (3, 'MARCH'), (4, 'APRIL'), (5, 'MAY'), (6, 'JUNE'), (7, 'JULY'), (8, 'AUGUST'), (9, 'SEPTEMBER'), (10, 'OCTOBER'), (11, 'NOVEMBER'), (12, 'DECEMBER')], null=True, verbose_name='Publication initial month number'),
        ),
        migrations.AddField(
            model_name='issue',
            name='publication_year',
            field=models.IntegerField(null=True, verbose_name='Publication year'),
        ),
        migrations.AlterUniqueTogether(
            name='issue',
            unique_together={('official_journal', 'volume', 'number', 'supplement'), ('official_journal', 'publication_year', 'volume', 'number', 'supplement')},
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['official_journal'], name='issue_issue_officia_c32d0a_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['publication_year'], name='issue_issue_publica_a3a5c7_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['volume'], name='issue_issue_volume_71bce1_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['number'], name='issue_issue_number_780a64_idx'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['supplement'], name='issue_issue_supplem_bd88be_idx'),
        ),
        migrations.RemoveField(
            model_name='issue',
            name='year',
        ),
    ]
