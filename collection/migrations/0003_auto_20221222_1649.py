# Generated by Django 3.2.12 on 2022-12-22 16:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0001_initial'),
        ('issue', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('article', '0003_auto_20221222_1649'),
        ('collection', '0002_documentincollections_issueincollections_journalcollections_scielodocument_scieloissue_scielojournal'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassicWebsiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Last update date')),
                ('title_path', models.CharField(blank=True, help_text='Title path: title.id path or title.mst path without extension', max_length=255, null=True, verbose_name='Title path')),
                ('issue_path', models.CharField(blank=True, help_text='Issue path: issue.id path or issue.mst path without extension', max_length=255, null=True, verbose_name='Issue path')),
                ('serial_path', models.CharField(blank=True, help_text='Serial path', max_length=255, null=True, verbose_name='Serial path')),
                ('cisis_path', models.CharField(blank=True, help_text='Cisis path where there are CISIS utilities such as mx and i2id', max_length=255, null=True, verbose_name='Cisis path')),
                ('bases_work_path', models.CharField(blank=True, help_text='Bases work path', max_length=255, null=True, verbose_name='Bases work path')),
                ('bases_pdf_path', models.CharField(blank=True, help_text='Bases translation path', max_length=255, null=True, verbose_name='Bases pdf path')),
                ('bases_translation_path', models.CharField(blank=True, help_text='Bases translation path', max_length=255, null=True, verbose_name='Bases translation path')),
                ('bases_xml_path', models.CharField(blank=True, help_text='Bases XML path', max_length=255, null=True, verbose_name='Bases XML path')),
                ('htdocs_img_revistas_path', models.CharField(blank=True, help_text='Htdocs img revistas path', max_length=255, null=True, verbose_name='Htdocs img revistas path')),
            ],
        ),
        migrations.CreateModel(
            name='FilesStorageConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Last update date')),
                ('host', models.CharField(blank=True, max_length=255, null=True, verbose_name='Host')),
                ('bucket_root', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bucket root')),
                ('bucket_app_subdir', models.CharField(blank=True, max_length=64, null=True, verbose_name='Bucket app subdir')),
                ('bucket_public_subdir', models.CharField(blank=True, max_length=64, null=True, verbose_name='Bucket public subdir')),
                ('bucket_migration_subdir', models.CharField(blank=True, max_length=64, null=True, verbose_name='Bucket migration subdir')),
                ('bucket_temp_subdir', models.CharField(blank=True, max_length=64, null=True, verbose_name='Bucket temp subdir')),
                ('bucket_versions_subdir', models.CharField(blank=True, max_length=64, null=True, verbose_name='Bucket versions subdir')),
                ('access_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='Access key')),
                ('secret_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='Secret key')),
                ('secure', models.BooleanField(default=True, verbose_name='Secure')),
            ],
        ),
        migrations.CreateModel(
            name='NewWebSiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Last update date')),
                ('url', models.CharField(blank=True, max_length=255, null=True, verbose_name='New website url')),
                ('db_uri', models.CharField(blank=True, help_text='mongodb://login:password@host:port/database', max_length=255, null=True, verbose_name='Mongodb Info')),
            ],
        ),
        migrations.CreateModel(
            name='SciELOFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='ID')),
                ('relative_path', models.CharField(blank=True, max_length=255, null=True, verbose_name='Relative Path')),
                ('name', models.CharField(max_length=255, verbose_name='Filename')),
                ('uri', models.URLField(max_length=255, null=True, verbose_name='URI')),
                ('object_name', models.CharField(max_length=255, null=True, verbose_name='Object name')),
            ],
        ),
        migrations.RemoveField(
            model_name='documentincollections',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='documentincollections',
            name='scielo_docs',
        ),
        migrations.RemoveField(
            model_name='documentincollections',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='issueincollections',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='issueincollections',
            name='official_issue',
        ),
        migrations.RemoveField(
            model_name='issueincollections',
            name='scielo_issues',
        ),
        migrations.RemoveField(
            model_name='issueincollections',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='journalcollections',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='journalcollections',
            name='official_journal',
        ),
        migrations.RemoveField(
            model_name='journalcollections',
            name='scielo_journals',
        ),
        migrations.RemoveField(
            model_name='journalcollections',
            name='updated_by',
        ),
        migrations.AddField(
            model_name='scielodocument',
            name='official_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='article.article'),
        ),
        migrations.AddField(
            model_name='scieloissue',
            name='official_issue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='issue.issue'),
        ),
        migrations.AddField(
            model_name='scielojournal',
            name='availability_status',
            field=models.CharField(blank=True, choices=[('?', 'Unknown'), ('C', 'Current')], max_length=10, null=True, verbose_name='Availability Status'),
        ),
        migrations.AddField(
            model_name='scielojournal',
            name='official_journal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='journal.officialjournal'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='acron',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Collection Acronym'),
        ),
        migrations.AlterField(
            model_name='scielodocument',
            name='file_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='File ID'),
        ),
        migrations.AlterField(
            model_name='scielodocument',
            name='pid',
            field=models.CharField(blank=True, max_length=23, null=True, verbose_name='PID'),
        ),
        migrations.AlterField(
            model_name='scieloissue',
            name='issue_folder',
            field=models.CharField(max_length=23, verbose_name='Issue Folder'),
        ),
        migrations.AlterField(
            model_name='scieloissue',
            name='issue_pid',
            field=models.CharField(max_length=23, verbose_name='Issue PID'),
        ),
        migrations.AlterField(
            model_name='scieloissue',
            name='scielo_journal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='collection.scielojournal'),
        ),
        migrations.AlterUniqueTogether(
            name='scielodocument',
            unique_together={('pid', 'file_id'), ('scielo_issue', 'file_id'), ('scielo_issue', 'pid')},
        ),
        migrations.AlterUniqueTogether(
            name='scieloissue',
            unique_together={('scielo_journal', 'issue_pid'), ('scielo_journal', 'issue_folder'), ('issue_pid', 'issue_folder')},
        ),
        migrations.AlterUniqueTogether(
            name='scielojournal',
            unique_together={('collection', 'scielo_issn'), ('collection', 'acron')},
        ),
        migrations.AddIndex(
            model_name='scielodocument',
            index=models.Index(fields=['scielo_issue'], name='collection__scielo__5bef2c_idx'),
        ),
        migrations.AddIndex(
            model_name='scielodocument',
            index=models.Index(fields=['pid'], name='collection__pid_837f75_idx'),
        ),
        migrations.AddIndex(
            model_name='scielodocument',
            index=models.Index(fields=['file_id'], name='collection__file_id_a2e87a_idx'),
        ),
        migrations.AddIndex(
            model_name='scielodocument',
            index=models.Index(fields=['official_document'], name='collection__officia_9656d6_idx'),
        ),
        migrations.AddIndex(
            model_name='scieloissue',
            index=models.Index(fields=['scielo_journal'], name='collection__scielo__caa1e6_idx'),
        ),
        migrations.AddIndex(
            model_name='scieloissue',
            index=models.Index(fields=['issue_pid'], name='collection__issue_p_b24fd5_idx'),
        ),
        migrations.AddIndex(
            model_name='scieloissue',
            index=models.Index(fields=['issue_folder'], name='collection__issue_f_e45b9f_idx'),
        ),
        migrations.AddIndex(
            model_name='scieloissue',
            index=models.Index(fields=['official_issue'], name='collection__officia_bd2f58_idx'),
        ),
        migrations.AddIndex(
            model_name='scielojournal',
            index=models.Index(fields=['acron'], name='collection__acron_fd9a83_idx'),
        ),
        migrations.AddIndex(
            model_name='scielojournal',
            index=models.Index(fields=['collection'], name='collection__collect_9538b6_idx'),
        ),
        migrations.AddIndex(
            model_name='scielojournal',
            index=models.Index(fields=['scielo_issn'], name='collection__scielo__dac95a_idx'),
        ),
        migrations.AddIndex(
            model_name='scielojournal',
            index=models.Index(fields=['availability_status'], name='collection__availab_c5b518_idx'),
        ),
        migrations.AddIndex(
            model_name='scielojournal',
            index=models.Index(fields=['official_journal'], name='collection__officia_6d9e77_idx'),
        ),
        migrations.CreateModel(
            name='AssetFile',
            fields=[
                ('scielofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collection.scielofile')),
                ('is_supplementary_material', models.BooleanField(default=False)),
            ],
            bases=('collection.scielofile',),
        ),
        migrations.CreateModel(
            name='FileWithLang',
            fields=[
                ('scielofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collection.scielofile')),
                ('lang', models.CharField(max_length=4, verbose_name='Language')),
            ],
            bases=('collection.scielofile',),
        ),
        migrations.DeleteModel(
            name='DocumentInCollections',
        ),
        migrations.DeleteModel(
            name='IssueInCollections',
        ),
        migrations.DeleteModel(
            name='JournalCollections',
        ),
        migrations.AddField(
            model_name='scielofile',
            name='scielo_issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.scieloissue'),
        ),
        migrations.AddField(
            model_name='newwebsiteconfiguration',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='newwebsiteconfiguration_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='newwebsiteconfiguration',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='newwebsiteconfiguration_last_mod_user', to=settings.AUTH_USER_MODEL, verbose_name='Updater'),
        ),
        migrations.AddField(
            model_name='filesstorageconfiguration',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='filesstorageconfiguration_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='filesstorageconfiguration',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filesstorageconfiguration_last_mod_user', to=settings.AUTH_USER_MODEL, verbose_name='Updater'),
        ),
        migrations.AddField(
            model_name='classicwebsiteconfiguration',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.collection'),
        ),
        migrations.AddField(
            model_name='classicwebsiteconfiguration',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='classicwebsiteconfiguration_creator', to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AddField(
            model_name='classicwebsiteconfiguration',
            name='updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='classicwebsiteconfiguration_last_mod_user', to=settings.AUTH_USER_MODEL, verbose_name='Updater'),
        ),
        migrations.CreateModel(
            name='SciELOHTMLFile',
            fields=[
                ('filewithlang_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collection.filewithlang')),
                ('part', models.CharField(max_length=6, verbose_name='Part')),
            ],
            bases=('collection.filewithlang',),
        ),
        migrations.CreateModel(
            name='XMLFile',
            fields=[
                ('filewithlang_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collection.filewithlang')),
                ('languages', models.JSONField(null=True)),
                ('public_uri', models.URLField(max_length=255, null=True, verbose_name='Public URI')),
                ('public_object_name', models.CharField(max_length=255, null=True, verbose_name='Public object name')),
            ],
            bases=('collection.filewithlang',),
        ),
        migrations.AddIndex(
            model_name='scielofile',
            index=models.Index(fields=['file_id'], name='collection__file_id_770a89_idx'),
        ),
        migrations.AddIndex(
            model_name='scielofile',
            index=models.Index(fields=['relative_path'], name='collection__relativ_6cd669_idx'),
        ),
        migrations.AddIndex(
            model_name='scielofile',
            index=models.Index(fields=['name'], name='collection__name_dd19c6_idx'),
        ),
        migrations.AddIndex(
            model_name='scielofile',
            index=models.Index(fields=['object_name'], name='collection__object__dd3e6a_idx'),
        ),
        migrations.AddIndex(
            model_name='scielofile',
            index=models.Index(fields=['scielo_issue'], name='collection__scielo__995583_idx'),
        ),
        migrations.AddIndex(
            model_name='newwebsiteconfiguration',
            index=models.Index(fields=['url'], name='collection__url_aaa55d_idx'),
        ),
        migrations.AddIndex(
            model_name='filewithlang',
            index=models.Index(fields=['lang'], name='collection__lang_4177e6_idx'),
        ),
        migrations.AddIndex(
            model_name='filesstorageconfiguration',
            index=models.Index(fields=['host'], name='collection__host_831dfb_idx'),
        ),
        migrations.AddIndex(
            model_name='filesstorageconfiguration',
            index=models.Index(fields=['bucket_root'], name='collection__bucket__65c090_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='filesstorageconfiguration',
            unique_together={('host', 'bucket_root')},
        ),
        migrations.AddIndex(
            model_name='classicwebsiteconfiguration',
            index=models.Index(fields=['collection'], name='collection__collect_565bb2_idx'),
        ),
        migrations.AddIndex(
            model_name='assetfile',
            index=models.Index(fields=['is_supplementary_material'], name='collection__is_supp_106058_idx'),
        ),
        migrations.AddField(
            model_name='scielodocument',
            name='renditions_files',
            field=models.ManyToManyField(null=True, related_name='renditions_files', to='collection.FileWithLang'),
        ),
        migrations.AddField(
            model_name='xmlfile',
            name='assets_files',
            field=models.ManyToManyField(to='collection.AssetFile'),
        ),
        migrations.AddField(
            model_name='scielohtmlfile',
            name='assets_files',
            field=models.ManyToManyField(to='collection.AssetFile'),
        ),
        migrations.AddField(
            model_name='scielodocument',
            name='html_files',
            field=models.ManyToManyField(null=True, related_name='html_files', to='collection.SciELOHTMLFile'),
        ),
        migrations.AddField(
            model_name='scielodocument',
            name='xml_files',
            field=models.ManyToManyField(null=True, related_name='xml_files', to='collection.XMLFile'),
        ),
        migrations.AddIndex(
            model_name='scielohtmlfile',
            index=models.Index(fields=['part'], name='collection__part_d49aa5_idx'),
        ),
    ]
