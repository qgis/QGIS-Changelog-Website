from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('changes', '0011_auto_20200730_0531'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='image_file_thumbnail',
            field=models.ImageField(
                blank=True,
                editable=False,
                help_text='Auto-generated 1000×500 WEBP thumbnail of image_file.',
                upload_to='images/thumbnails/versions/',
            ),
        ),
    ]
