# Generated by Django 3.2.13 on 2022-06-03 05:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='ticker',
            new_name='stock',
        ),
        migrations.RemoveField(
            model_name='bookmark',
            name='ticker',
        ),
        migrations.AddField(
            model_name='bookmark',
            name='stock',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.stock'),
        ),
        migrations.AddField(
            model_name='index',
            name='stock',
            field=models.ManyToManyField(to='main.Stock'),
        ),
        migrations.RemoveField(
            model_name='bookmark',
            name='user',
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='IndexStocks',
        ),
    ]
