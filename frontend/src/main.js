import { createApp } from 'vue'
import { createStore } from 'vuex'
import App from './App.vue'
import getData from './mixins/getData.js'


const store = createStore({
    state () {
      const thisURL = '/backend/' // url backend
      return {
        questionlist: Object, // список id вопросов в выбранном опросе. Используется для запроса следующего вопроса с сервера
        doneQuestionlist: Object, // список отвеченных вопросов в текущем опросе. Нужен для запроса ответов с сервера (моих, а не правильных)
        currentquestionpos: null, // отображаемый на экране вопрос
        currentSurveyId: null, // потому-что props не успел
        action: '', // для header, отображает текущее дествие
        jwt_access: '', // access токен, не хранится в куках, в куках хранится refresh
        errMessage: '', // выводится в алерте на случай проблем с сервером/сетью
        headers: {
            'Content-Type': 'application/json'
          },
        endpoints: {
          obtainJWT: thisURL + 'token/', // получить пару токенов
          refreshJWT: thisURL + 'refresh/', // обновить access токен
          getSurveyList: thisURL + 'surveylist/', // получить список всех опросов
          getSurveyDetail: thisURL + 'survey/', // получить данные конкретного опроса (со списком id вопросов)
          getQuestionDetail: thisURL + 'question/', // получить вопрос с вариантами ответа (либо полем ввода)
          getMyAnswers: thisURL + 'getanswer/', // получить мои ранее отмеченные ответы
          postMyAnswer: thisURL + 'answer/', // ответить
          getSurveyResults: thisURL + 'getstatsurvey/', // получить данные по всем опросам
          getUserAnswers: thisURL + 'getallanswers/', // для администраторов, получить ответы пользователей (на истекшие по сроку опросы)
          getSurveyQuestionList: thisURL + 'questionlist/' // для администраторов, получить полный список вопросов опроса с вариантами ответа
          },
      }
    },
    mutations: {
        setAction: (state, payload) => state.action = payload,
        setQuestionlist: ( state, payload ) => state.questionlist['question_ids'] = payload.q_ids,
        setDoneQuestionlist: ( state, payload ) => state.doneQuestionlist['ids'] = payload.q_ids,
        addDoneQuestionList: (state, payload) => {
          if (!state.doneQuestionlist['ids'].includes(payload)) // имеет смысл клать только уникальные значения
            state.doneQuestionlist['ids'].push(payload)
        },
        setCurrentSurveyId: ( state, payload ) => state.currentSurveyId = payload,
        setCurrentquestionpos: ( state, payload ) => state.currentquestionpos = payload,
        setErrMessage: ( state, payload ) => state.errMessage = payload,
        updateToken: (state, newToken) => { // формируем готовые headers с токеном
          state.headers.Authorization = `Bearer ${newToken}`
          state.jwt_access = newToken
        },
    }
  })

const app = createApp(App)
app.config.globalProperties.$store=store; // подключаем хранилище
app.use(store)
app.mixin(getData) // и свой миксин
app.mount('#app')
