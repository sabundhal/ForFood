<template>
  <v-app-bar app>
    <v-spacer></v-spacer>
    <v-btn icon to="/main">
      <v-icon>mdi-home</v-icon>
    </v-btn>
    <v-btn icon to="/pediatric">
      <v-icon>mdi-calculator</v-icon>
    </v-btn>
    <v-btn icon to="/calculationhistory">
      <v-icon>mdi-history</v-icon>
    </v-btn>
    <v-spacer></v-spacer>
    <v-btn icon to="/login">
      <v-icon>mdi-login</v-icon>
    </v-btn>
    <v-btn icon to="/profile"> <!-- Иконка профиля для авторизованного пользователя -->
      <v-icon>mdi-account</v-icon>
    </v-btn>
    <v-btn icon @click="logout">
      <v-icon>mdi-logout</v-icon>
    </v-btn>
  </v-app-bar>
</template>

<script>
export default {
  name: "Menu",
  computed: {
    username() {
      const name = localStorage.getItem('user_name');
      console.log("Данные пользователя в localStorage:", name); // Отладочная информация
      return name;
    },
  },
  methods: {
    logout() {
      localStorage.removeItem('user_name');
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