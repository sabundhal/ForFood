<template>
  <v-app>
    <Menu />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import { RouterView } from 'vue-router';
import Menu from './components/Menu.vue';

export default {
  components: {
    Menu,
  },
};
</script>

<style>
#app {
  margin-top: 60px; /* Отступ для фиксации верхнего меню */
}
</style>