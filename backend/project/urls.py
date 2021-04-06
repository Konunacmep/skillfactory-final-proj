from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from survey.views import QuestionList, SurveyList, QuestionDetail, SurveyDetail, postAnswer, getUserAnswer, MyTokenObtainPairView, getStatSurvey, getAllUserAnswers
from django.contrib.staticfiles.urls import static
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.site.site_url = None
admin.site.site_header = "Администрирование опросов"
admin.site.unregister(Group)


# app один, поэтому проще использовать один файл url, а не добавлять его сюда через includ
urlpatterns = [
    path('admin/', admin.site.urls), # админка
    path('surveylist/', SurveyList.as_view()), # список всех доступных опросов для пользователя (доступных, т.е. начавшихся и/или закончившихся)
    # не включает те, что не начались
    path('questionlist/<int:sur_pk>/<int:usr_id>', QuestionList.as_view()), # список вопросов опроса для окна результатов
    path('question/<int:pk>/<int:sur_pk>/', QuestionDetail.as_view()), # детальная информация по вопросу, с вариантами ответов
    path('survey/<int:pk>/', SurveyDetail.as_view()), # детальная информация по опросу. Предоставляет также список id вопросов
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # получить пару токенов, только post
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'), # получить новый access токен
    path('answer/', postAnswer, name='post_answer'), # ответить, только post
    path('getanswer/<int:sur_pk>/<int:qw_pk>/', getUserAnswer), # получить ранее отвеченный ответ, пользователя
    path('getstatsurvey/', getStatSurvey.as_view()), # получить данные по всем опросам, кратко
    path('getallanswers/<int:sur_pk>/<int:user_id>/', getAllUserAnswers.as_view()), # получить ответы пользователя и правильные по конкретному опросу
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + staticfiles_urlpatterns()
