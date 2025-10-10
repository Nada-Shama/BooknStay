from django.db import migrations

def fix_invalid_amenities(apps, schema_editor):
    Hotel = apps.get_model('hotels', 'Hotel')
    import json
    for h in Hotel.objects.all():
        value = h.amenities
        if value is None:
            continue
        try:
            if isinstance(value, (list, dict)):
                continue
            json.loads(value)
        except Exception:
            h.amenities = []
            h.save()

class Migration(migrations.Migration):
    dependencies = [
        ('hotels', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(fix_invalid_amenities),
    ]
