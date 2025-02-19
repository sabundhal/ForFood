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
    <v-btn v-if="!username" icon to="/login">
      <v-icon>mdi-login</v-icon>
    </v-btn>
    <v-btn v-if="!username" icon @click="logout">
  <v-icon>mdi-logout</v-icon>
    </v-btn>
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