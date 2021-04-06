from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


# Вопросы могут переиспользоваться в разных опросах, но ответы у каждого свои, не переиспользуемые
# вопрос
class Question(models.Model):
    Q_TYPES = (
        (1, 'С одним верным ответом'),
        (2, 'С несколькими верными ответами'),
        (0, 'Вписать свой ответ'),
    )
    image = models.ImageField(upload_to='./images', blank=True, null=True, verbose_name=_("Изображение"))
    q_type = models.PositiveSmallIntegerField(choices=Q_TYPES, verbose_name=_("Тип вопроса"))
    q_text = models.TextField(verbose_name=_("Текст вопроса"))
    class Meta:
        verbose_name = _('Вопрос')
        verbose_name_plural = _('Вопросы')

    def __str__(self):
        return f'{self.get_q_type_display()} | {self.q_text}'


# ответ 
class Answer(models.Model):
    A_TYPES = (
        (1, 'Неверен'),
        (2, 'Верен'),
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name=_('answers')) # привязь к вопросу
    a_text = models.CharField(max_length=100, verbose_name=_("Тескт ответа"))
    a_type = models.SmallIntegerField(default=1, choices=A_TYPES, verbose_name=_("Верен/неверен")) # тип 2 - верен, 1 - не верен
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name=_('Баллов за верный ответ')) # баллы за ответ
    class Meta:
        verbose_name = _('Ответ')
        verbose_name_plural = _('Ответы')

# опрос
# в случае опросника верность ответов не проверяется
class Survey(models.Model):
    S_TYPES = (
        (0, 'Тест'),
        (1, 'Опросник'),
    )
    type = models.SmallIntegerField(choices=S_TYPES, verbose_name=_("Тип опроса"))
    title = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    questions = models.ManyToManyField(Question, related_name='surveys', verbose_name=_("Вопросы"))
    start_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Дата начала"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Дата окончания"))
    class Meta:
        verbose_name = _('Опрос')
        verbose_name_plural = _('Опросы')

    def __str__(self):
        return f'{self.get_type_display()}. {self.title}'


# ответы пользователя
class PersonAnswers(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name=_('user_answers'))
    survey_id = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name=_('user_surveys'))
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, related_name=_('user_questions'))
    type = models.BooleanField(default=True) # 1 - из базы, 0 - вписанный пользователем текст (в случае типа вопроса q_type 0 или опросника)
    text = models.CharField(max_length=250, blank=True) # сам текст ответа пользователя

    class Meta: # ответ на каждый вопрос отдельного опросника должен быть уникален. Ответы хранятся либо текстом, либо массивом, в любом случае в баз ответ один
        constraints = [models.UniqueConstraint(fields=['user_id', 'survey_id', 'question_id'], name='one_answer_per_question')]