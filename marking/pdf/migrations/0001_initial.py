# Generated by Django 4.2.7 on 2023-11-22 13:41

from django.db import migrations, models
import django.db.models.deletion
import pdf.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_id', models.IntegerField()),
                ('file', models.FileField(blank=True, null=True, upload_to=pdf.models.upload_pdf_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_number', models.IntegerField()),
                ('question_number', models.IntegerField()),
                ('marks', models.IntegerField()),
                ('question_text', models.CharField(max_length=500)),
                ('marking_guide', models.TextField()),
                ('question_type', models.CharField(blank=True, max_length=50, null=True)),
                ('model_answer', models.CharField(blank=True, max_length=50, null=True)),
                ('topic', models.CharField(blank=True, max_length=50, null=True)),
                ('learning_outcome', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdf.assessment')),
            ],
        ),
        migrations.CreateModel(
            name='Attempts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt_id', models.IntegerField()),
                ('student_id', models.IntegerField()),
                ('section_id', models.IntegerField()),
                ('question_id', models.IntegerField()),
                ('answer', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdf.assessment')),
            ],
        ),
    ]
