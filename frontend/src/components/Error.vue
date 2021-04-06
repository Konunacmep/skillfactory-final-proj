<!-- просто выводит алерт, если произошла ошибка сети, в слот текст ошибки -->
<template>
  <div class="alert alert-warning alert-dismissible fade show position-sticky" role="alert">
    <strong>Error! </strong><slot></slot>
    <button type="button" class="btn-close" data-dismiss="alert" aria-label="Close" @click="this.$store.commit('setErrMessage', '')">
    </button>
  </div>
</template>
