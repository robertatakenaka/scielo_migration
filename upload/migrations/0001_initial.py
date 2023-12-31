# Generated by Django 4.2.6 on 2023-12-31 18:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("issue", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("article", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Package",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creation date"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Last update date"
                    ),
                ),
                ("file", models.FileField(upload_to="", verbose_name="Package File")),
                (
                    "signature",
                    models.CharField(
                        blank=True, max_length=32, null=True, verbose_name="Signature"
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("update", "Atualizar"),
                            ("erratum", "Erratum"),
                            ("new-document", "New document"),
                        ],
                        max_length=32,
                        verbose_name="Category",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("submitted", "Submetido"),
                            ("enqueued-for-validation", "Enqueued for validation"),
                            ("validated-with-errors", "Validated with errors"),
                            ("validated-without-errors", "Validated without errors"),
                            ("pending-correction", "Pending for correction"),
                            ("ready-to-be-finished", "Ready to be finished"),
                            ("quality-analysis", "Waiting for quality analysis"),
                            ("rejected", "Rejeitado"),
                            ("accepted", "Accepted"),
                            ("scheduled-for-publication", "Scheduled for publication"),
                            ("published", "Publicado"),
                        ],
                        default="enqueued-for-validation",
                        max_length=32,
                        verbose_name="Status",
                    ),
                ),
                (
                    "expiration_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Expiration date"
                    ),
                ),
                (
                    "article",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="article.article",
                    ),
                ),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_creator",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Creator",
                    ),
                ),
                (
                    "issue",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="issue.issue",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_last_mod_user",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updater",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("finish_deposit", "Can finish deposit"),
                    ("access_all_packages", "Can access all packages from all users"),
                    ("assign_package", "Can assign package"),
                ),
            },
        ),
        migrations.CreateModel(
            name="ValidationResult",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("package-file-error", "PACKAGE_FILE_ERROR"),
                            (
                                "article-journal-incompatibility-error",
                                "ARTICLE_JOURNAL_INCOMPATIBILITY_ERROR",
                            ),
                            ("article-is-not-new-error", "ARTICLE_IS_NOT_NEW_ERROR"),
                            ("xml-format-error", "XML_FORMAT_ERROR"),
                            ("bibliometrics-data-error", "BIBLIOMETRICS_DATA_ERROR"),
                            ("services-data-error", "SERVICES_DATA_ERROR"),
                            ("data-consistency-error", "DATA_CONSISTENCY_ERROR"),
                            ("criteria-issues-error", "CRITERIA_ISSUES"),
                            ("asset-error", "ASSET_ERROR"),
                            ("rendition-error", "RENDITION_ERROR"),
                        ],
                        max_length=64,
                        verbose_name="Error category",
                    ),
                ),
                (
                    "data",
                    models.JSONField(
                        blank=True, default=dict, null=True, verbose_name="Error data"
                    ),
                ),
                (
                    "message",
                    models.TextField(
                        blank=True, null=True, verbose_name="Error message"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("created", "created"),
                            ("disapproved", "disapproved"),
                            ("approved", "approved"),
                        ],
                        max_length=16,
                        null=True,
                        verbose_name="Status",
                    ),
                ),
                (
                    "package",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="upload.package"
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("send_validation_error_resolution", "Can send error resolution"),
                    (
                        "analyse_validation_error_resolution",
                        "Can analyse error resolution",
                    ),
                ),
            },
        ),
        migrations.CreateModel(
            name="QAPackage",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("upload.package",),
        ),
        migrations.CreateModel(
            name="ErrorResolutionOpinion",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creation date"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Last update date"
                    ),
                ),
                (
                    "validation_result",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="analysis",
                        serialize=False,
                        to="upload.validationresult",
                    ),
                ),
                (
                    "opinion",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("fixed", "Fixed"),
                            ("fix-demanded", "Error has to be fixed"),
                        ],
                        max_length=32,
                        null=True,
                        verbose_name="Opinion",
                    ),
                ),
                (
                    "guidance",
                    models.TextField(
                        blank=True, max_length=512, null=True, verbose_name="Guidance"
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_creator",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Creator",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_last_mod_user",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updater",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ErrorResolution",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Creation date"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Last update date"
                    ),
                ),
                (
                    "validation_result",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="resolution",
                        serialize=False,
                        to="upload.validationresult",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("to-fix", "I will fix this error"),
                            ("disagree", "This is not an error"),
                        ],
                        max_length=32,
                        null=True,
                        verbose_name="Action",
                    ),
                ),
                (
                    "rationale",
                    models.TextField(blank=True, null=True, verbose_name="Rationale"),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_creator",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Creator",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_last_mod_user",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Updater",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
