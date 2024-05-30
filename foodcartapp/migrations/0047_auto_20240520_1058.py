# Generated by Django 3.2.15 on 2024-05-20 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20240520_1047'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Online', 'Электронно'), ('Cash', 'Наличными')], db_index=True, default='Cash', max_length=12),
        ),
    ]