# Generated by Django 2.1.1 on 2018-09-20 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idolmaster', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idol',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]