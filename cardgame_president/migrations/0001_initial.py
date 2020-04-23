# Generated by Django 3.0.5 on 2020-04-17 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('code', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('round_num', models.IntegerField(default=0)),
                ('current_card', models.IntegerField()),
                ('play_turn', models.IntegerField()),
                ('order_up', models.BooleanField()),
                ('play_stack', models.IntegerField()),
                ('consecutive', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('play_order', models.IntegerField()),
                ('skip_turn', models.BooleanField(default=False)),
                ('role', models.CharField(choices=[('PR', 'President'), ('VPR', 'Vice President'), ('VSC', 'Vice Scum'), ('SC', 'Scum')], max_length=3)),
                ('h', models.CharField(max_length=13)),
                ('d', models.CharField(max_length=13)),
                ('c', models.CharField(max_length=13)),
                ('s', models.CharField(max_length=13)),
                ('j', models.IntegerField()),
                ('game_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cardgame_president.Game')),
            ],
        ),
    ]
