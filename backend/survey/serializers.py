from rest_framework import serializers
from .models import Question, Answer, PersonAnswers, Survey
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, Case, When, DecimalField, Value, F
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import datetime
import ast
from django.conf import settings
from django.utils.timezone import now


# функция для проверки правильности ответа когда пользователь его вписывает
def check_free_type_question(obj):
    result = True
    right_answer = obj.question_id.answers.first()
    person_answer = [ i for i in obj.text.strip(' ').split(' ') if len(i) > 0 ]
    for x in person_answer:
        if not x in right_answer.a_text:
            result = False
        return right_answer.weight if result else 0


# Функция для подсчета баллов по одному вопросу
def calc_one_quest_ball(item):
    # в зависимости от типа вопроса
    if item.question_id.q_type == 0:
        return check_free_type_question(item)
    elif item.question_id.q_type == 1:
        answer = ast.literal_eval(item.text)[0]
        return item.question_id.answers.get(id=answer).weight
    else:
        answer_list = ast.literal_eval(item.text)
        # print('list', answer_list)
        # print('filtered', item.question_id.answers.filter(id__in=answer_list))
        # print('all', [ x.weight for x in item.question_id.answers.filter(id__in=answer_list) ])
        return sum([ x.weight for x in item.question_id.answers.filter(id__in=answer_list) ])

# данные о пользователе в реальном проекте было бы логично взять имя и фамилию
# но я для простоты беру username, их потом и выведу на фронтэнде
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff',]


# не отдаем верен/неверен, опрос еще актуален, не просрочен. Поэтому в контексте получаем флаг, брать по минимуму или нет
class AnswerSerizlizer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(AnswerSerizlizer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            if kwargs['context'] == 'short':
                self.fields.pop('a_type')
                self.fields.pop('weight')
    class Meta:
        model = Answer
        exclude = ('question', )



# добавляем вложенное поле ответов в вопрос
class QuestionSerizlizer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField('get_answers')
    points = serializers.SerializerMethodField('points_count')
    
    # считаем баллы для отдельного вопроса
    def points_count(self, obj):
        kwarg_sur_id = self.context.get('view').kwargs.get('sur_pk')
        survey = Survey.objects.get(id=kwarg_sur_id)
        other_user = self.context.get('view').kwargs.get('usr_id')
        usr_id = self.context['request'].user.id
        if other_user:
            usr_id = other_user
        if survey.end_date < now():
            qwest = survey.user_surveys.filter(user_id=usr_id).filter(question_id=obj.id).first()
            if qwest:
                return calc_one_quest_ball(qwest)
            else:
                return 0

    # вешаем флаг для вложенного сериалайзера, чтобы выводить баллы и правильность, если опрос кончился
    def get_answers(self, obj):
        kwarg_sur_id = self.context.get('view').kwargs.get('sur_pk')
        answers = Question.objects.get(id=obj.id).answers
        survey = Survey.objects.get(id=kwarg_sur_id)
        if survey.end_date < now():
            serializer_context = 'all'
        else:
            serializer_context = 'short'
        serializer = AnswerSerizlizer(answers, many=True, context=serializer_context)
        return serializer.data
    
    class Meta:
        model = Question
        fields = ['id', 'image', 'q_type', 'q_text', 'answers', 'points']


# возвращает всю инфрмацию об опросе. Получился перегружен, из-за того, что хотел переиспользовтаь имеющееся
# позже понял, что лучше пусть будет дублирование и лучше бы написал два для разных задач, но переделывать не захотел
class SurveySerializer(serializers.ModelSerializer):
    # добавляем дополнительные возвращаемые поля. Только для чтения
    answered_questions = serializers.SerializerMethodField('answered_count') # количество вопросов на которые пользователь ответил
    total_questions = serializers.SerializerMethodField('total_count') # всего вопросов в опросе
    user = serializers.SerializerMethodField('add_user_id') # id пользователя, что сделал запрос
    points_got = serializers.SerializerMethodField('count_points_got') # количество очков, набранных пользователем
    points_total = serializers.SerializerMethodField('count_points_total') # всего очков
    survey_over = serializers.SerializerMethodField('survey_is_over') # опрос закончен если true
    def answered_count(self, inst):
        if self.context.get('called_for_single'): # вызван для одного опроса
            # список отвеченных
            return PersonAnswers.objects.filter(Q(user_id=self.context['request'].user.id) & Q(survey_id=inst.id)).values_list('question_id', flat=True)
        else:
            # количество отвеченных
            return PersonAnswers.objects.filter(Q(user_id=self.context['request'].user.id) & Q(survey_id=inst.id)).count()
    
    def total_count(self, inst):
        # Если в списке, то выводим сколько всего отвечено из опроса, не выдаем ничего для detail
        if self.context.get('called_for_single'):
            q = ''
        else:
            q = Survey.objects.get(pk=inst.id).questions.count()
        return q

    # добавляем пользователя
    def add_user_id(self, inst):
        usr = UserSerializer(self.context['request'].user)
        return usr.data

    # считаем баллы только для закончившихся опросов
    def count_points_got(self, inst):
        q = ''
        if inst.end_date < now():
            qwer = Survey.objects.get(id=inst.id).user_surveys.filter(user_id=self.context['request'].user.id)
            if self.context.get('called_for_single'):
                # формируем списое 'верных' и 'пользовательских' ответов
                q = {}
                for item in qwer:
                    if item.question_id.q_type > 0:
                        temp = item.question_id.answers.filter(a_type=2)
                        q[item.question_id.id] = { 'correct': [ x.id for x in temp ], 'user': item.text }
                    else:
                        res = check_free_type_question(item)
                        q[item.question_id.id] = { 'correct': res, 'user': item.text }
            else:
                # либо общие цифры для списка пользователей
                q = 0
                for item in qwer:
                    q += calc_one_quest_ball(item)
        return q  

    def count_points_total(self, inst):
        # q = Survey.objects.get(pk=inst.id).questions.aggregate(Sum('answers__weight'))
        q = Survey.objects.get(pk=inst.id).questions.aggregate(
            answers__weight__sum=Sum(Case(When(answers__weight__gt=0, then=F('answers__weight')), default=Value(0), output_field=DecimalField())))
        return q['answers__weight__sum']

    def survey_is_over(self, inst):
        # True, если уже кончился
        return True if inst.end_date < now() else False

    # проверим, что конец не раньше начала
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"end_date": "Опрос должен заканчиваться после того как начнется"})
        return data

    # не выдаем вопросы для опросов, дата которых еще не пришла
    def get_questions(self, inst):
        if now() >= inst.start_date:
            return inst.questions
        else:
            return []

    class Meta:
        model = Survey
        # выводи все нужные поля, в том числе добавленные
        fields = ['id', 'type', 'title', 'description', 'questions', 'start_date', 'end_date', 'answered_questions', 'total_questions', 'user', 'points_got', 'points_total', 'survey_over']


# возвращает ответы конкретного пользователя по запрошенному опросу
class PersonAnswerSerializer(serializers.ModelSerializer):
    text = serializers.JSONField()

    # пробуем сохранить ответ. В 99% случаем оно сработает
    def save(self, **kwargs):
        try:
            super().save(**kwargs)
        except:
            # ищем и перезаписываем ответ, если пользователь почему-то решил переответить
            q = PersonAnswers.objects.filter(Q(user_id=self.validated_data["user_id"].id) & Q(survey_id=self.validated_data["survey_id"]) & Q(question_id=self.validated_data["question_id"])).first()
            self.instance = q
            super().save(**kwargs)
        
    class Meta:
        model = PersonAnswers
        fields = ['user_id', 'survey_id', 'question_id', 'type', 'text']


# добавим пару полей в токен
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # добавим свои поля
        token['is_staff'] = user.is_staff
        token['username'] = user.username
        return token
