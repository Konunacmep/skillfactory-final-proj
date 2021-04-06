<template>
  <div v-if="responseQuestion && responseAnswer && styles">
    <img :src="question.image" width="600"/>
    <div>
      <p class="d-inline-block">{{ question.q_text }}</p>
      <p v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">Получено баллов за вопрос: {{question.points}}</p>
    </div>
    <div v-if="question.q_type==1">
      <div v-for="answer in question.answers" v-bind:key="answer.id" :class="styles[answer.id]" >
        <input type="radio" v-bind:id="answer.id" :disabled="survey.survey_over" v-model="userAnswer[0]" :checked="userAnswer[0] == answer.id" :value="answer.id" />
        <label v-bind:for="answer.id" :class="answer.a_type == 2? 'fw-bold text-success': ''">{{ answer.a_text }}</label>
        <span v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">{{ answer.weight }} балл(ов)</span>
      </div>
    </div>
    <div v-if="question.q_type==2">
      <div v-for="answer in question.answers" v-bind:key="answer.id" :class="styles[answer.id]">
        <input type="checkbox" :id="answer.id" :value="answer.id" :disabled="survey.survey_over" v-model="userAnswer" />
        <label v-bind:for="answer.id" :class="answer.a_type == 2? 'fw-bold text-success': ''">{{ answer.a_text }}</label>
        <span v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">{{ answer.weight }} балл(ов)</span>
      </div>
    </div>
    <div v-if="question.q_type==0">
      <input type="text" :disabled="survey.survey_over" v-model="userAnswer" class="form-control" :class="styles[question.answers[0].id]"/>
      <span v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">{{ question.answers[0].weight }} балл(ов)</span>
    </div>
    <button @click="submit" class="btn btn-secondary" :disabled="submitButtonActive">{{ survey.survey_over? 'Далее': 'Ответ' }}</button>
    <teleport to=".navbar-nav">
      <li class="nav-item ms-2" v-if="menuItem">
        <a class="nav-link" href="#" @click="$emit('backToList')">Все тесты</a>
      </li>
    </teleport>
  </div>
</template>


<script>
export default {
  name: 'QuestionConstructor',
  data() {
    return {
      userAnswer: [], // массив ответов пользователя, если он  просматривает уже отвеченные вопросы
      question: Object, // текущий вопрос
      menuItem: true, // отображение текущего действия (ответа/просмотра на вопрос) в меню
      responseQuestion: false, // флаг, что promise разрешился
      responseAnswer: false, // флаг, что promise разрешился
    }
  },
  emits: {
    backToList: true, // если следующего вопроса нет, возвращение к списку
  },
  props: {
    survey: Object, // текущий опрос
  },
  computed: { 
    submitButtonActive() { // флаг, что кнопка "ответ" должна быть неактивна, если никакой ответ не выбран
      if (this.survey.survey_over) return false
      return this.userAnswer.length? false: true
    },
    actualQuestionId() {
      // в vuex хранится массив с id всех пвопросов опроса, номер вопроса на интерфейсе соответствует индексу элемента массива
      return this.$store.state.questionlist['question_ids'][this.$store.state.currentquestionpos] 
    },
    showWeight() { // если есть баллы у первого вопроса, то должны быть у всех
      return ('weight' in this.question.answers[0])? true: false
    },
    styles() {
      // формируем стили для ответов. Зеленый если ответ пользователя совпал с верным, и красным в противном случае
      let res = {} // результат
      if (this.survey.survey_over) { // мы видим баллы только если опрос закончен
        let corr = 'alert-success' // цвета для подкраски ответов
        let incorr = 'alert-danger'
        if (this.survey.type == 1) {
          corr = ''
          incorr = ''
        }
        if (this.responseQuestion && this.responseAnswer) { // если получили все с сервера, начинаем формировать
          if (this.question.q_type == 1) { // с одним верным ответом  
            for (let answer of this.question.answers) {
              if (answer.a_type == 2) { // сравним, если ответ пользователя совпадает с верным ответом
                if (this.userAnswer != answer.id) {
                  res[this.userAnswer] = incorr
                } else {
                  res[answer.id] = corr
                }
              }
            }
          }
          if (this.question.q_type == 2) { // с несколькими верными ответами
            for (let answer of this.question.answers) {
              // а здесь уже нужно смотреть по каждому ответу из массива - ответ пользователя совпадает с верным - зеленый, нет - красный
              if (Object.values(this.userAnswer).indexOf(answer.id) > -1) {
                if (answer.a_type == 1) res[answer.id] = incorr
                else res[answer.id] = corr
              }     
            }  
          }
          if (this.question.q_type == 0) { // ответ текстом
            // а здесь сразу возвращается верность или нет в виде баллов, не возвращается сам вариант верного ответа
            if (this.question.answers[0].points > 0 ) {
              res[this.question.answers[0].id] = corr  
            } else {
              res[this.question.answers[0].id] = incorr
            } 
          }
        }
      }
      return res
    },
  },
  methods: {
    getData() {
      // получить с сервера вопрос со всем причитающимся
      this.getDataAPI(`${this.$store.state.endpoints.getQuestionDetail + this.actualQuestionId}/${this.$store.state.currentSurveyId}/`,
        { headers: this.$store.state.headers },
        ((data) => {
          this.question = data
          this.getUserAnswer() // запросим ответ на случай, если пользователь уже отвечал и хочет переответить
          this.responseQuestion = true;
          }))
    },
    getUserAnswer() {
      // получить ответы, если на вопрос отвечено (не правильные, свои)
      this.getDataAPI(`${this.$store.state.endpoints.getMyAnswers + this.$store.state.currentSurveyId}/${this.actualQuestionId}/`,
        { headers: this.$store.state.headers },
        ((data) => {
          try {
            this.userAnswer = JSON.parse(data)
            this.responseAnswer = true;
          }
          catch {
            this.userAnswer = data
            this.responseAnswer = true;
          }
          }))
    },
    goNextQuestion() { // функция для перехода к следующему не отвеченному вопросу, либо если таковых нет, то просто к следующему
        if (!this.survey.survey_over) {
        let notDoneQuestions = []; // вычислим массив не отвеченных вопросов. массив объектов вида "question id" : "answered or not"
        for ( let value of this.$store.state.questionlist['question_ids']) {
          if (this.$store.state.doneQuestionlist['ids'].includes(value)) notDoneQuestions.push({ [value]: false }) 
          else notDoneQuestions.push({ [value]: true })
          }
        let key = notDoneQuestions.flatMap(x => Object.keys(x)) // изымаем индексы вопросов
        let offs = key.indexOf(this.actualQuestionId.toString()) // вычисляем позицию текущего вопроса
        let len = key.length // всего вопросов
        for( let i=0; i < len; i++) { // ищем следующий неотвеченный вопрос
          let pointer = (i + offs) % len; 
          if (Object.values(notDoneQuestions[pointer])[0]) {
            this.$store.commit('setCurrentquestionpos', pointer)
            return;
          }
        } // если нет неотвеченных, то просто идем к следующему
      }
      if (this.$store.state.currentquestionpos+1 < this.$store.state.questionlist['question_ids'].length) this.$store.commit('setCurrentquestionpos', this.$store.state.currentquestionpos+1)
      else { // если дошли до последнего - выход к списку
        this.menuItem = false
        this.$emit('backToList')       
      }
    },
    submit() {
      // отправка ответа
      if (!this.survey.survey_over) {
        if (this.userAnswer.length) {
          this.getDataAPI(this.$store.state.endpoints.postMyAnswer,
          { 
            method: 'POST',
            headers: this.$store.state.headers,
            body: JSON.stringify({
              'survey_id': this.survey.id,
              'question_id': this.actualQuestionId,
              'type': this.question.q_type==0? 0: 1,
              'text': this.userAnswer,
              })
            },
            (() => { 
              this.$store.commit('addDoneQuestionList', this.actualQuestionId) // помещаем в массив отвеченных
              this.goNextQuestion() // переход к следующему вопросу
              
              }))
        } 
      }
      else {
        this.goNextQuestion()
      }    
    }
  },
  watch: {
    // при переключении вопросов кнопками либо просто по средствам перехода к следующему вопросу, нужно его запросить с сервера
    '$store.state.currentquestionpos': function () { 
      this.responseQuestion = false; // если изменился текущий вопрос, обнуляем все флаги ответа и запрашиваем данные
      this.responseAnswer = false;
      this.getData(); 
    },
  },
  mounted() {
    // запрос первого вопроса в списке когда открыли опрос
    if (('question_ids' in this.$store.state.questionlist) && (this.survey.id !== undefined)) {
      this.getData()
    }
  },
}
</script>