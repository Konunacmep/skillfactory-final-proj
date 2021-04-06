from .models import Answer, PersonAnswers, Question, Survey
from .serializers import QuestionSerizlizer, SurveySerializer, PersonAnswerSerializer, MyTokenObtainPairSerializer
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.utils.timezone import now
from django.conf import settings
    

# получение списка опросов
class SurveyList(generics.ListAPIView):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()


# список вопросов
class QuestionList(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerizlizer

    # дополняем id опроса для того, чтобы в сериалайзере проверить
    # если он кончился, то выводим и баллы и правильность
    def get_queryset(self):
        return Question.objects.filter(surveys=self.kwargs['sur_pk'])


# возвращает оидн вопрос с вариантами ответа
class QuestionDetail(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerizlizer


# полная инфа по одному опросу
class SurveyDetail(generics.RetrieveAPIView):
    # queryset = Survey.objects.filter(start_date__lte=now())
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    
    # флаг, который означает, возвращаем информацию по одному опросу или для списка
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["called_for_single"] = True
        return context
    

# ответ на вопрос, только POST
@api_view(['POST',])
def postAnswer(request):
    validated = False
    if request.data['type']: # превратим порлученный ответ в массив, на всякий случай, если ответ не словесный, т.е. type  1 или 2
        if isinstance(request.data['text'], list):
            id_to_list = request.data['text']
        else:
            id_to_list = [request.data['text']]
        # Проверим входные данные, а именно:
        # что пришедший id ответа есть среди id вариантов ответа данного вопроса и вопрос есть среди вопросов опроса
        if Survey.objects.filter( Q(questions__answers__id__in=id_to_list) & Q(id=request.data['survey_id']) & Q(questions__id=request.data['question_id']) ).exists():
            validated = True
    else:
        validated = True
    if validated:
        survey = Survey.objects.get(id=request.data['survey_id'])
        if survey.end_date >= now(): # проверим, что опрос еще не кончился, иначе ответ не принимается
            request.data['user_id'] = request.user.id
            serializer = PersonAnswerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('данный опрос закончился', status=status.HTTP_400_BAD_REQUEST)
    return Response('такого сочетания вопроса, опроса и ответа не существует', status=status.HTTP_400_BAD_REQUEST)

# Можно было бы отдавать сразу больше информации в SurveySerializer и хранить в памяти браузера,
# но переответ старых вопросов - это скорей редкий случай, чем обычный режим работы
@api_view(['GET',])
def getUserAnswer(request, sur_pk, qw_pk):
    q = PersonAnswers.objects.filter(Q(user_id=request.user.id) & Q(survey_id=sur_pk) & Q(question_id=qw_pk))
    if q.exists():
        return Response(q.first().text, status=status.HTTP_200_OK)
    return Response([])


# получить данные по опросам и пользователям всем сразу
class getStatSurvey(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        surveys = Survey.objects.all()
        users = User.objects.all()
        result = []
        for user in users:
            request.user = user
            serializer = SurveySerializer(surveys, many=True, context={'request': request})
            result += serializer.data
        return Response(result)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# для просмотра результатов конкретного пользователя
class getAllUserAnswers(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request, *args, **kwargs):
        request.user.id = kwargs.get('user_id', request.user.id)
        survey = Survey.objects.get(pk=kwargs.get('sur_pk', 1))
        serializer = SurveySerializer(survey, context={'request': request, 'called_for_single': True})
        return Response(serializer.data)
