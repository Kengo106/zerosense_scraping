from django.shortcuts import render

from django.shortcuts import render
from django.views import View
from .models import Race
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import pytz
from django.conf import settings
import os
# Create your views here.
from django.shortcuts import render

from .scraping import initialize_browser, scrape_grade_race, scrape_grade_race_result
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


def home_site_view(request):
    return render(request, 'home.html')

@method_decorator(csrf_exempt, name='dispatch')
class GradeRaceScraping(View):
    def post(self, request):
        browser = initialize_browser()
        scrape_grade_race(browser)
        return render(request, "finish.html")

@method_decorator(csrf_exempt, name='dispatch')
class GradeRaceResultScraping(View):
    def post(self, request):
        browser = initialize_browser()
        scrape_grade_race_result(browser)
        return render(request, "finish.html")

@method_decorator(csrf_exempt, name='dispatch')
class FinishVoteView(View):
    def post(self, request):
        utc_now = timezone.now()
        jst = pytz.timezone('Asia/Tokyo')
        jst_now = utc_now.astimezone(jst)
        now_date = jst_now.date()
        print(jst_now, now_date)
        vote_deadline_plusone = (jst_now + timedelta(hours=1)).time()
        if jst_now.time() > vote_deadline_plusone: # 23時以降は1足すと0時になるため
            races = Race.objects.filter(
                Q(race_date=now_date)
            )
        else:
            races = Race.objects.filter(
                Q(race_date=now_date)
                & Q(start_time__lte=vote_deadline_plusone)
            )
        print(len(races))

        for race in races:
            print(race.race_name)
            race.is_votable = 2
            race.save()

        past_race_date = (now_date - timedelta(days=4))
        print(past_race_date)
        past_races = Race.objects.filter(
            Q(race_date__lte=past_race_date)
        )
        for race in past_races:
            race.is_votable = 0
            race.save()
        return render(request, 'finish.html')