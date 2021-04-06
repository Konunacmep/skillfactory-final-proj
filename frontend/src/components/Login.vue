<template lang="html">
  <form class="text-center">
      <div class="mx-auto w-25 mt-3">
        <label for="id_username" class="form-label">Имя пользователя</label>
        <input
          v-model="username"
          type="text"
          class="form-control"
          placeholder="Username"
          autofocus="autofocus"
          maxlength="150"
          id="id_username"/>
      </div>
      <div class="mx-auto w-25 mt-3">
        <label for="id_password" class="form-label">Пароль</label>
        <input
          v-model="password"
          type="password"
          class="form-control"
          placeholder="Password"
          id="id_password"/>
      </div>
      <button
        @click.prevent="onSubmit"
        class="btn btn-primary col-lg-1 mt-3"
        type="submit">
        Войти
      </button>
  </form>
</template>

<script>
import Cookies from 'js-cookie'
var mylib = require('../common_ftions/ftions.js'); // парсер jwt
export default {
  data() {
    return {
      username: '',
      password: '',
    };
  },
  // событие чтобы убрать окно логина
  emits: {
    loggedIn: true,
  },
  methods: {
    // получаем данные ввода
    onSubmit(event) {
      event.preventDefault();
      const requestData = {
        'username': this.username,
        'password': this.password,
      };
      // отправляем на сервер в надежде получить два токена
      const csrft = Cookies.get('csrftoken');
      const addr = this.$store.state.endpoints.obtainJWT;
      this.getDataAPI(addr,
          {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'X-CSRFToken': csrft,
            },
            body: JSON.stringify(requestData)
          },
          ((data) => { // полученные токены раскладываем - refresh  в куки, также ставим время жизни на основе
          // данных из токена, а access кладем в хранилище
          let expr = new Date(mylib.parseJwt(data.access).exp + Date.now())
          this.$store.commit('updateToken', data.access)
          expr = new Date(mylib.parseJwt(data.refresh).exp + Date.now())
          Cookies.set('refresh_token', data.refresh, { expires: expr })
          this.$emit('loggedIn')
          window.location.reload() // чтобы для нового пользователя все начать с чистого листа
          })                  
      )
    },
  },
  mounted() {
    // отразим в заголовке логин
    this.$store.commit('setAction', 'Вход')
  }
};
</script>