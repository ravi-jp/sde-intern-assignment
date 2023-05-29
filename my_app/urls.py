from django.urls import path
from . import views

app_name='my_app'
urlpatterns=[
    path('rest/v1/calendar/init/',views.GoogleCalendarInitView),
    path('rest/v1/calendar/redirect/',views.GoogleCalendarRedirectView,name='v2'),
    # path('rest/abc',views.my_view)
    
]