from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.environmental_impact, name="index"),
    path("lookup", views.lookup, name='lookup'),
    path("environment", views.environmental_impact, name="environmental_impact"),
    path("impact", views.impact, name="impact"),
    path("credits", views.credits, name='credits'),
    path("addteam", views.addteam, name='addteam'),
    path("team", views.teamview, name='teamview'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("about", views.about_user, name="about_user"),
    path("profile", views.profile, name="profile"),
    path("invite", views.invite, name='invite'),
    path("addevent", views.addevent, name='addevent'),
    path('event', views.event_details, name='event_details')
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
