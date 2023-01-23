from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='skillblog-home'),
    path("about/", views.about, name='skillblog-about'),
    path("resumeanalyzer/",views.ResumeAnalyzer, name='resumeanalyzer'),
]