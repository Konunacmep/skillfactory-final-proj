<template>
    <teleport to=".current-action">
        <h2 class="text-light d-inline">{{ action }}</h2>
    </teleport>
</template>


<script>
export default {
    computed: {
        action() { // просто выводит в заголовке текущее действие, которое компоненты пишут во vuex
            return this.$store.state.action
        }
    },
}
</script>