<template>
<!-- компонент выбора опроса и переключения между вопросами -->
  <!-- кнопка перехода в окно результатов опросов - для админа -->
  <teleport to=".navbar-nav">
    <li class="nav-item ms-2" v-if="showButton">
      <a class="nav-link" href="#" @click="showResults">{{!results?'Список тестов с результатами пользователей':'Пройти тесты'}}</a>
    </li>
  </teleport>
  <div v-if="results">
    <SurveyResults :myList="surveyList"/>
  </div>
  <!-- список опросов -->
  <div v-else>
    <div v-if="showList" class="list-group">
        <a v-for="item in surveyList" :key="item.id" @click="surveyListElementToggleDisplayClass" href="#" class="list-group-item list-group-item-action" :class="item.survey_over? 'bg-light': ''">
          <h4><span :class="item.type == 0?'badge bg-warning': 'badge bg-info'">{{ item.type == 0? 'Тест': 'Опросник' }} </span>   {{ item.title }} ({{testState(item)}})</h4>
          <p>Вопросов отвечено: <span>{{ item.answered_questions? item.answered_questions: 0 }}/{{ item.total_questions? item.total_questions: 0 }}</span></p>
          <p>Начало: {{formatDat(item.start_date)}}</p>
          <p>Окончание: {{formatDat(item.end_date)}}</p>
          <div class="d-none">
            <p>{{ item.description }}</p>
            <button v-if="(new Date(item.start_date)).getTime() < (new Date()).getTime()" @click="start(item.id, item.title)" class="btn btn-secondary">{{ item.survey_over? 'Просмотреть ответы': 'Приступить к прохождению'}}</button>
          </div>
        </a>
    </div>
    <!-- навигация по выбранному опросу -->
    <div v-else>
      <div id="question-switcher" class="mt-3">
        <button v-for="(item, itemObjKey) in survey.questions"
          v-bind:key="item" v-on:click="pickQuestion(itemObjKey)"
          class="btn text-light"
          :class="buttonClassStyle[item]">{{ itemObjKey + 1 }}</button>
      </div>
      <QuestionConstructor @backToList="showList = true" :survey="survey"/>
    </div>
  </div>
</template>


<script>
import QuestionConstructor from './QuestionConstructor.vue'
import SurveyResults from './SurveyResults.vue'
let mylib = require('../common_ftions/ftions.js') // парсер jwt и не только
export default {
  name: 'QuestionNav',
  components: {
    QuestionConstructor,
    SurveyResults,
  },
  data() {
    return {
      survey: Object, // текущий опрос
      surveyList: null, // список опросов
      showList: true, // флаг показа списка опросов
      showButton: false,  // флаг показа кнопки админа
      results: false, // переключатель в панель результатов и обратно
    }
  },
  computed: {
    buttonClassStyle() { // если вопрос отвечен, то кнопку красим в один цвет, не отвечен - в другой
      let res = {}
      for (let item of this.survey.questions) {
        if (this.$store.state.doneQuestionlist['ids'].indexOf(item) > -1) {
          res[item] = 'btn-success'
        } else {
          res[item] = 'btn-info'
        }
      } // текущий вопрос, вешаем класс активный
      res[this.$store.state.questionlist['question_ids'][this.$store.state.currentquestionpos]] += ' active'
      return res
    },
  },
  methods: {
    // получить список опросов текущего пользователя
    getSurveyList() {
      this.getDataAPI(this.$store.state.endpoints.getSurveyList, { 'headers': this.$store.state.headers }, ((data) => {
        this.surveyList = data
        }))
    },
    // получить список вопросов выбранного опроса и запись этих вопросов и данных ответов в хранилище
    getSurvey(surId) {
      this.getDataAPI(this.$store.state.endpoints.getSurveyDetail + surId +'/',
        { 'headers': this.$store.state.headers },
        ((data) => {
          this.survey = data
          this.$store.commit('setQuestionlist', {q_ids: data.questions}) // список id вопросов
          this.$store.commit('setDoneQuestionlist', {q_ids: data.answered_questions}) // список отвеченных
          this.$store.commit('setCurrentquestionpos', 0) // текущая позиция на начало
          })
      )
    },
    // переход к вопросу возможно с вариантами ответов
    pickQuestion(key) {
      this.$store.commit('setCurrentquestionpos', key)
    },
    // раскрыть описание опроса или закрыть
    surveyListElementToggleDisplayClass(event) {
      event.currentTarget.querySelector('div').classList.toggle('d-none')
    },
    // начать опрос
    start(surId, surTitle) {
      this.getSurvey(surId);
      this.showList = false;
      this.$store.commit('setAction', surTitle)
      this.$store.commit('setCurrentSurveyId', surId)
    },
    // показать результаты других участников, только для админа
    showResults() {
      this.results = !this.results
      this.$store.commit('setAction', 'Список опросов')
    },
    formatDat(dat) {
      return mylib.dateFormat(dat)
    },
    testState(item) {
      if (item.survey_over) return 'Окончен'
      else return ((new Date(item.start_date)).getTime() < (new Date()).getTime())? 'Доступен': 'Скоро начнется'
    },
  },
  watch: {
    // если нужно вернуться к списку опросов, запросить с сервера, отразить в хидере
    showList: function(val) {
      this.getSurveyList()
      if (val) this.$store.commit('setAction', 'Список опросов')
    }
  },
  // получить список опросов 
  beforeMount() {
    if (this.showList) {
      this.getSurveyList()
    }
    // если админ - показывать админскую кнопку. Флаг админ или нет зашифрован в токене
      if (mylib.parseJwt(this.$store.state.jwt_access).is_staff) {
      this.showButton = true
      }
      this.$store.commit('setAction', 'Список опросов')
  }
}
</script>