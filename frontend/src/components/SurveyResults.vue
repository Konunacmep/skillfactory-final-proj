<template>
  <div v-if="showList" class="list-group">
      <a v-for="item in myList" @click="surveyListElementToggleDisplayClass" :key="item.id" href="#" class="list-group-item list-group-item-action">
        <h4><span :class="item.type == 0?'badge bg-warning': 'badge bg-info'">{{ item.type == 0? 'Тест': 'Опросник' }}</span>   {{ item.title }} ({{item.survey_over? 'Окончен': 'Доступен'}})</h4>
          <p>Начало: {{ formatDat(item.start_date) }}</p>
          <p>Окончание: {{ formatDat(item.end_date) }}</p>
        <div class="d-none">
          <p>{{ item.description }}</p>
          <h5>Пользователи</h5>
          <div v-if="gotResponse" class="list-group">
            <a v-for="obj in surveyListUser[item.id]" 
              :key="obj[item.id]+'a'"
              @click="open_result(item.id, obj.user_id, item.title, obj.username, item.survey_over, item.type)"
              href="#" class="list-group-item list-group-item-action" :class="item.survey_over? '': 'bg-light'">
              <h6>{{ obj.username }}</h6>
              <p class="mb-1">вопросов отвечено: {{ obj.answered_questions }}/{{ obj.total_questions }}</p>
              <p class="mb-1">баллов получено: {{ obj.points_got?obj.points_got:'дата окончания теста еще не наступила, данных нет' }}</p>
              <p class="mb-1">баллов максимально возможно: {{ obj.points_total }}</p>
            </a>
          </div>
        </div>
      </a>
  </div>
  <div v-else>
    <ResultList :userAndSurvey="$options.userAndSurvey" @backToList="showList=true"/>
  </div>
</template>


<script>
import ResultList from './ResultList.vue'
let mylib = require('../common_ftions/ftions.js')
export default {
  components: {
    ResultList, // подробно по выбранному юзеру
  },
  props: {
    myList: Object // передаем свой список опросов как пример полного списка, все равно админу доступно все
    },
  data() {
    return {
      survey: Object, // результаты людей по конкретному опросу
      showList: true, // обратно к списку
      surveyList: [], // список опросов
      gotResponse: false, // получен ответ, promise разрешился
    }
  },
  userAndSurvey: null, // выбранные пользователь и опрос
  computed: {
    surveyListUser() {
      let res = {}
      // распаковка данных по отдельным пользователям, для показа в списке (для всех опросов)
      for (let obj of Object.entries(this.myList)) {
        res[obj[1].id] = []
        for (let item of Object.entries(this.surveyList)) {
          if (obj[1].id == item[1].id) {
            res[obj[1].id].push({
              'user_id': item[1].user.id,
              'username': item[1].user.username,
              'is_staff': item[1].user.is_staff, // админ или нет
              'answered_questions': item[1].answered_questions, // сколько отвечено
              'total_questions': item[1].total_questions, // сколько всего
              'points_got': item[1].points_got, // баллов
              'points_total': item[1].points_total, // баллов возможно было
            })
          }
        }
      }
      return res
    },
  },
  methods: {
    getData() { // получить результаты опроса по всем пользователям
      this.getDataAPI(this.$store.state.endpoints.getSurveyResults,
      { headers: this.$store.state.headers },
      ((data) => {
          this.surveyList = data
          this.gotResponse = true
          }))
    },
    surveyListElementToggleDisplayClass(event) { // показать "подробнее" по опросу - список пользователей
      event.currentTarget.querySelector('div').classList.toggle('d-none')
    },
    open_result(sur_id, user_id, title, username, sur_over, sur_type) { // переход к просмотру ответов
      if (sur_over) { // возможен только для завершенных опросов
        this.showList = false
        this.$options.userAndSurvey = [sur_id, user_id, sur_type] // поскольку админу доступны все опросы, их список мы и пошлем в компонент
        this.$store.commit('setAction', `Опрос "${title}" (результаты пользователя ${username})`)
      } else {
        this.$store.commit('setErrMessage', 'Данный опрос еще не окончен, нельзя просмотреть результаты пользователя')
      }
    },
    formatDat(val) {
      return mylib.dateFormat(val)
    }
  },
  created() {
    this.getData()
    this.$store.commit('setAction', 'Результаты тестирования пользователей')
  }
}
</script>