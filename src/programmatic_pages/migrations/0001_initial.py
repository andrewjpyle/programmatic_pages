from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PageBuild",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("project_key", models.CharField(db_index=True, max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="running",
                        max_length=20,
                    ),
                ),
                ("pages_built", models.IntegerField(default=0)),
                ("pages_errors", models.IntegerField(default=0)),
                ("build_time_seconds", models.FloatField(default=0)),
                ("output_dir", models.CharField(blank=True, default="", max_length=500)),
                ("entity_type_filter", models.CharField(blank=True, default="", max_length=100)),
                ("error_message", models.TextField(blank=True, default="")),
                ("triggered_by", models.CharField(default="manual", max_length=50)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Page Build",
                "ordering": ["-started_at"],
            },
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("project_key", models.CharField(db_index=True, max_length=200)),
                ("entity_type", models.CharField(blank=True, db_index=True, default="", max_length=100)),
                ("url_path", models.CharField(max_length=500)),
                ("title", models.CharField(max_length=300)),
                ("meta_description", models.TextField(blank=True, default="")),
                ("h1", models.CharField(max_length=300)),
                ("body_html", models.TextField(blank=True, default="")),
                ("schema_type", models.CharField(default="WebPage", max_length=100)),
                ("schema_extras", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["project_key", "status"], name="programmatic_p_proj_st_idx"),
                    models.Index(fields=["project_key", "entity_type"], name="programmatic_p_proj_et_idx"),
                ],
                "unique_together": {("project_key", "url_path")},
            },
        ),
    ]
