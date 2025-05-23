# Generated by Django 5.1.4 on 2025-02-11 01:55

import django.db.models.deletion
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
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('deadline', models.DateTimeField()),
                ('weight', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('score', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grades.assignment')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('grader', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='graded_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
