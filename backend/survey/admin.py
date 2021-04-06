from django.contrib import admin
from .models import PersonAnswers, Question, Survey, Answer
from .forms import SurveyForm, QuestionForm
from django.forms import CheckboxSelectMultiple
from django.db import models
from django.utils.safestring import mark_safe


class QuestionInline(admin.TabularInline):
    model = Answer

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else: 
            return 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ["image_field",]
    search_fields = ('q_text',)
    list_filter = ('q_type',)
    inlines = [QuestionInline,]
    list_display = ('q_type', 'q_text')
    form = QuestionForm # объявлена своя форма, не отличающаяся от стандартной но нужная для подключания своего js
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super(QuestionAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super(QuestionAdmin, self).add_view(request, form_url, extra_context=extra_context)


# для отображения изображения в админке
    def image_field(self, obj):
        width = obj.image.width if obj.image.width < 600 else 600
        return mark_safe(f'<img src="{obj.image.url}" width="{width}"/>')    

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('type', 'start_date', 'end_date')
    list_display = ('type', 'title', 'start_date', 'end_date')
    date_hierarchy = 'end_date'
    list_select_related = True
    filter_horizontal = ('questions',) # виджет с двумя полями для выбора вопросов
