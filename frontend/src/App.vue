<template>
<!-- Окно логина или окно навигации по опросам -->
  <Error v-show="errMsg">{{ errMsg }}</Error>
  <Login @loggedIn="gotToken=true" v-if="!gotToken"/>
  <QuestionNav v-else/>
  <teleport to=".navbar">
    <div>
      <h4 class="text-light d-inline" v-if="gotToken">{{ username }}</h4>
      <ul class="navbar-nav d-inline">
        <li class="nav-item d-inline">
          <a class="nav-link d-inline" href="#" @click="logOff" v-if="gotToken"> Выйти</a>
        </li>
      </ul>
    </div>
  </teleport>
  <CurrentAct/>
</template>


<script>
import QuestionNav from './components/QuestionNav.vue'
import Login from './components/Login.vue'
import CurrentAct from './components/CurrentAct.vue'
import Error from './components/Error.vue'
import Cookies from 'js-cookie'

let mylib = require('./common_ftions/ftions.js');
export default {
  name: 'App',
  components: {
    QuestionNav,
    Login,
    CurrentAct,
    Error,
  },
  data() {
    return { 
      // флаг логина
      gotToken: false,
      AccessTokenRefreshTimeout: null, // для таймера обновления access токена
      username: '', // имя пользователя для заголовка
      }
  },
  computed: {
    errMsg() {
      // если появляется ошибка - вывести. Если убралась - убрать
      return this.$store.state.errMessage
    }

  },
  created() {
    // access токен живет минут пять, нет смысла проверять протух ли, лучше просто запросить
    this.requestAccessToken()
    this.$options.accessTokenTimer = null
  },
  methods: {
    requestAccessToken() {
      let refresh = Cookies.get('refresh_token') // refresh хранится в куках
      if ( refresh  && (mylib.parseJwt(refresh).exp-Date.now()/1000 > 300)) {
      // Если он есть и не вышел срок годности - запросим по нему access.
      // Если нету - вывод окна логина
        this.getDataAPI(this.$store.state.endpoints.refreshJWT,
          {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'refresh': refresh })
          },
          ((response) => {
              // вычленяем время жизни токена и устанавливаем таймер запроса обновления
              this.AccessTokenRefreshTimeout = (mylib.parseJwt(response.access).exp - Date.now()/1000) * 1000
              this.$store.commit('updateToken', response.access) // записываем access token в хранилище
              this.gotToken = true // флаг что авторизовались
          })                  
        )
      }
      else {
        Cookies.remove('refresh_token') // если токен устарел, удалим его
        this.gotToken = false; // не авторизованы
      }
    },
    logOff() {
      this.$store.commit('updateToken', '') // удалили access токен из хранилища
      Cookies.remove('refresh_token') // удаляем refresh токен
      this.gotToken = false // не авторизованы
      this.username = ''
    },
  },
  watch: {
    gotToken(val) { // вычленяем имя пользователя
      if (val) this.username = mylib.parseJwt(this.$store.state.jwt_access).username 
    },
    // если пришел токен и мы вычленили время, значит пускаем таймер, который будет запрашивать обновление токена каждые n минут
    AccessTokenRefreshTimeout: function() {
      if (this.gotToken) {
        clearInterval(this.$options.accessTokenTimer)
        this.$options.accessTokenTimer = setInterval(function(vue_instance) {
          vue_instance.requestAccessToken()
        }, this.AccessTokenRefreshTimeout, this)
      }
    }
  }
  }
</script>
