# Generated by Django 3.1.2 on 2022-01-28 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('territorios', '0002_csv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csv',
            name='csv_file',
            field=models.FileField(upload_to='csvs'),
        ),
        migrations.AlterField(
            model_name='csv',
            name='file_name',
            field=models.CharField(max_length=120),
        ),
    ]
