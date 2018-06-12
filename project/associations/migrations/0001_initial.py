# Generated by Django 2.0.6 on 2018-06-11 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('left_id', models.PositiveIntegerField(db_index=True)),
                ('right_id', models.PositiveIntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssociationKind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('left_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leftk', to='contenttypes.ContentType')),
                ('right_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rightk', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='association',
            name='kind',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='associations.AssociationKind'),
        ),
        migrations.AddField(
            model_name='association',
            name='left_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='left', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='association',
            name='right_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='right', to='contenttypes.ContentType'),
        ),
        migrations.AlterUniqueTogether(
            name='association',
            unique_together={('kind', 'left_type', 'right_type', 'left_id', 'right_id')},
        ),
    ]
