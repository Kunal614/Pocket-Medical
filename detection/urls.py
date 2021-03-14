from django.urls import path , include
from .views import Signup   , Login  , Dashboard , Logout , Prediction , View_Report , Delete_Report , Edit_Report , Profile_View , GenerateQr , view_map , Medical , Hospital , Edit_Profile
from .views import Decode_qr

from django.conf import settings
from django.conf .urls.static import static
urlpatterns = [
    path('' , Login , name="Login"),
    path('signup/' , Signup , name="SignUp") , 
    path('login/' , Login , name="Login"),
    path('dashboard/' , Dashboard , name="Dashboard"),
    path('logout/' , Logout , name="Logout"),
    path('predict/' ,Prediction , name="Prediction"),
    path('view_report/<int:id>' , View_Report, name="Your_Report"),
    path('delete_report/<int:id>' ,Delete_Report, name="Delete_Report"),
    path('edit_report/<int:id>' ,Edit_Report, name="Update_Report"),
    path('profile/' ,Profile_View, name="Profile"),
    path('profile_pics/',GenerateQr , name='GenerateQr'),
    path('view_map/',view_map, name='view_map'),
    path('medicals/',Medical , name="Medical") , 
    path('hospitals/' ,Hospital, name="Hospital"),
    path('details/' ,Decode_qr, name="Details"),
    path('edit_profile/' ,Edit_Profile, name="Edit_Profile"),

]
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
