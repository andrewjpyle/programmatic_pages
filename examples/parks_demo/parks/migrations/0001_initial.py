# Initial migration for the parks demo (works on Django 4.2 and newer).

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Park',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('acres', models.PositiveIntegerField()),
                ('trail_miles', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('opened', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True, default='')),
            ],
        ),
    ]
