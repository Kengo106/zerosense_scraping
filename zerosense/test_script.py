import os
import django

# Djangoプロジェクトの設定を設定する
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zerosense.settings')

# Djangoをセットアップする
django.setup()
from scraping.models import Race
from datetime import date
import uuid
from django.utils import timezone

race = Race(
    race_name = "tttttttttttttttttttttttttttttttttttttttttttttttttttttest",
    rank = "teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeest",
    race_date = date.today(),
    start_time = timezone.now(),
    is_votable = 5432)
race.save()
print("OK")