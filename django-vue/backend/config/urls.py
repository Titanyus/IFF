from django.urls import path
from records import views

urlpatterns = [
    path("api/session/", views.session_info),
    path("api/login/", views.login),
    path("api/logout/", views.logout),
    path("api/cases/", views.cases),
    path("api/cases/<int:case_id>/", views.case_detail),
    path("api/cases/<int:case_id>/transition/", views.transition),
    path("api/cases/<int:case_id>/trash/", views.trash),
    path("api/cases/<int:case_id>/restore/", views.restore),
    path("api/guardians/", views.guardians),
]
