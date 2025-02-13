<template>
  <v-app-bar app>
    <v-spacer></v-spacer>
    <v-btn text to="/main">Главная</v-btn>
    <v-btn text to="/books">Книги</v-btn>
    <v-btn text to="/pediatric">Калькулятор</v-btn>
    <v-btn text to="/calculationhistory">История Расчетов</v-btn>
    <v-spacer></v-spacer>
    <v-btn v-if="!username" to="/login">Войти</v-btn>
  </v-app-bar>
</template>

<script>
export default {
  name: "Menu",
  computed: {
    username() {
      return localStorage.getItem('username'); // Получаем username из localStorage
    },
  },
  methods: {
    logout() {
      localStorage.removeItem('username');
      localStorage.removeItem('access_token');
      this.$router.push('/login'); // Перенаправляем на страницу логина
    },
  },
};
</script>

<style>
.mr-2 {
  margin-right: 0.5rem;
}
</style>