// делает запрос к серверу, обрабатывает, или точнее выводит ошибки. Принимат url, опции, коллбэк
export default {
  methods: {
    getDataAPI(URL, optns, ftia) {
      try {
        (async function () {
          let rawResponse = await fetch(URL, optns)
          if (!rawResponse.ok) { // если сервер вернул ошибку то выведем её
            throw new Error( `${rawResponse.statusText} (${rawResponse.status})` );
          }
          return rawResponse.json();       
        })().then(ftia)
        .catch(err => { // выведем ошибку с переводом для двух самых особо частых
          let transl_dict = {
            'Failed to fetch' : 'Сервер недоступен',
            'Unauthorized (401)' : 'Ошибка авторизации, проверьте учётные данные',
            'Not Found (404)': 'Нет данных',
          } // помещаем текст ошибки в хранилище чтобы вывести на экран
          this.$store.commit('setErrMessage', err.message in transl_dict ? transl_dict[err.message] : err.message )
        })      
    }
      catch (error) { // дополнительно
        this.$store.commit('setErrMessage', error)
        return null
      }
    }
  }
};