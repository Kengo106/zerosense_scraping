from django.contrib import admin
from django.urls import path
from scraping.views import  GradeRaceScraping, GradeRaceResultScraping, FinishVoteView,home_site_view
from django.views.generic import RedirectView

urlpatterns = [
    path('home',home_site_view,name='home'),
    path("getgraderace", GradeRaceScraping.as_view(), name='grade-race'),
    path("getgraderaceresult", GradeRaceResultScraping.as_view(),
         name="grade-race-result"),
    path('finishvote', FinishVoteView.as_view(), name='finish-vote'),
    path('admin',admin.site.urls),
    path('',RedirectView.as_view(url='/home')),
]
