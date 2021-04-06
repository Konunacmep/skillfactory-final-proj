<template>
  <div v-if="responseQuestion && responseAnswer && styles && Object.keys(userAndCorrectAnswers).length">
    <div v-for="item in questionList" :key="item.id">
      <img :src="item.image" width="600"/>
      <div>
        <p class="d-inline-block"><b>{{ item.q_text }}</b></p>
        <p v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">Получено баллов за вопрос: {{item.points}}</p>
      </div>
      <div v-if="item.q_type==1">
        <div v-for="answer in item.answers" v-bind:key="answer.id" :class="styles[item.id]? styles[item.id][answer.id]: ''">
          <input type="radio" v-bind:id="answer.id" v-bind:value="answer.id" disabled :checked="userAndCorrectAnswers[item.id]? userAndCorrectAnswers[item.id]['user'].includes(answer.id): false" />
          <label v-bind:for="answer.id" :class="answer.a_type == 2? 'fw-bold text-success': ''">{{ answer.a_text }}</label>
          <span v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">{{ answer.weight }} балл(ов)</span>
        </div>
      </div>
      <div v-if="item.q_type==2">
        <div v-for="answer in item.answers" v-bind:key="answer.id" :class="styles[item.id][answer.id]" class="rounded-lg">
          <input type="checkbox" v-bind:id="answer.id" v-bind:value="answer.id" disabled :checked="userAndCorrectAnswers[item.id]?JSON.parse(userAndCorrectAnswers[item.id]['user']).includes(answer.id):false" />
          <label v-bind:for="answer.id" :class="answer.a_type == 2? 'fw-bold text-success': ''">{{ answer.a_text }}</label>
          <span v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">{{ answer.weight }} балл(ов)</span>
        </div>
      </div>
      <div v-if="item.q_type==0" >
        <input type="text" disabled :value="userAndCorrectAnswers[item.id]? userAndCorrectAnswers[item.id]['user']:''" :class="styles[item.id]" class="form-control"/>
        <span v-if="showWeight" style="color:grey;font-weight:bold" class="float-end">{{ item.answers[0].weight }} балл(ов)</span>
      </div>
      <hr />
    </div>
  </div>
  <div v-else>
    <h2> Похоже, что здесь нет данных</h2>
  </div>
  <teleport to=".navbar-nav">
    <li class="nav-item ms-2" v-if="menuItem">
      <a class="nav-link" href="#" @click="back">Список тестов с результатами пользователей</a>
    </li>
  </teleport>
</template>


<script>
export default {
  data() {
    return {
      questionList: {}, // список вопросов, с вариантами ответов
      userAndCorrectAnswers: {}, // список ответов, пользователя и верных. могут не совпадать
      responseQuestion: false, // получили вопросы
      responseAnswer: false, // получили ответы
      menuItem: true, // убрать из хидера когда false
    }
  },
  props: {
    userAndSurvey: Array, // получаем id выбранного пользователя, результаты которого хотим смотреть и опрос
  },
  emits: {
    // к списку опросов
    backToList: true,
  },
  computed: {
    showWeight() { // если у первого варианта ответа, первого вопроса, есть вес, то есть и у всех
      return ('weight' in this.questionList[0].answers[0])? true: false
    },
    // points() {
    //   for (item in this.questionList) {
    //     if (item.q_type == 2) {

    //     }
    //   }
    // },
    styles() {
      // формируем стили для ответов. Зеленый если ответ пользователя совпал с верным, и красным в противном случае
      let res = {} // результат
      let corr = 'alert-success' // цвета для подкраски ответов
      let incorr = 'alert-danger'
      if (this.userAndSurvey[2] == 1) {
        corr = ''
        incorr = ''
      }
      if (this.responseQuestion && this.responseAnswer) { // если получили все с сервера, начинаем формировать
        for (let item of this.questionList) {
          if (item.q_type == 1) { // с одним верным ответом
            // если ответ пользователя совпадает с верным, красим зеленым, нет - красным
            if (item.id in this.userAndCorrectAnswers) {
              let tmp = JSON.parse(this.userAndCorrectAnswers[item.id]['user'])
              if (this.userAndCorrectAnswers[item.id]['correct'][0] == tmp) {
                res[item.id] = { [tmp]: corr }
              } else {
                res[item.id] = { [tmp]: incorr }
              }
            }
          }
          if (item.q_type == 2) { // с несколькими верными ответами
            // а здесь уже нужно смотреть по каждому ответу из массива - ответ пользователя совпадает с верным - зеленый, нет - красный
            if (item.id in this.userAndCorrectAnswers) {
              res[item.id] = {}
              for (let i of JSON.parse(this.userAndCorrectAnswers[item.id]['user'])) {
                if (this.userAndCorrectAnswers[item.id]['correct'].includes(i)) res[item.id][i] = corr 
                else res[item.id][i] = incorr
              }         
            }
          }
          if (item.q_type == 0) { // ответ текстом
            res[item.id] = ''
            // а здесь сразу возвращается верность или нет, не возвращается сам вариант верного ответа
            if (item.id in this.userAndCorrectAnswers) {
              if (this.userAndCorrectAnswers[item.id]['correct'] == 0 ) {
                res[item.id] = incorr  
              } else {
                res[item.id] = corr
              }  
            }  
          }
        }
      }
      return res
    },
  },
  methods: {
    // получить список всех вопросов опроса с вариантами ответов
    getDataQuestions() {
      this.getDataAPI(`${this.$store.state.endpoints.getSurveyQuestionList + this.userAndSurvey[0]}/${this.userAndSurvey[1]}`,
      { headers: this.$store.state.headers },
      ((data) => {
          this.questionList = data
          this.responseQuestion = true
          }))
    },  
    // получить список все ответов - пользователя и верных
    getDataAnswers() {
      this.getDataAPI(`${this.$store.state.endpoints.getUserAnswers + this.userAndSurvey[0]}/${this.userAndSurvey[1]}/`,
      { headers: this.$store.state.headers },
      ((data) => {
          this.userAndCorrectAnswers = data['points_got']
          this.responseAnswer = true
          }))
    }, 
    back() {
      this.menuItem = false
      this.$emit('backToList') // обратно к списку опросов
      this.$store.commit('setAction', 'Результаты тестирования пользователей')
    },  
  },
  created() { // запрос инфы с сервера
    this.getDataAnswers()
    this.getDataQuestions()
  },  
}
</script>