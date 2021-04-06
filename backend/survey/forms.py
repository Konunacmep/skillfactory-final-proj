from .models import Survey, Question
from django.forms import ModelForm, CheckboxSelectMultiple


# свой вариант навигации по списку вопросов для добавления в опросник, не используется
class SearchCheckboxSelectMultiple(CheckboxSelectMultiple):
    class Media:
        js = ('search.js',)   

class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = '__all__'
        widgets = {'questions': SearchCheckboxSelectMultiple()}

# создан исключитально для кастомизации админки. Для добавления подсказок на форму создания вопроса
class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
    class Media:
        js = ('tips.js',)
    