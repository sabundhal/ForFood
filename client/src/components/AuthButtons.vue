<template>
  <div>
    <!-- Кнопки входа и регистрации, если пользователь не авторизован -->
    <router-link v-if="!token" class="btn btn-primary btn-sm" to="/login">Вход</router-link>
    <router-link v-if="!token" class="btn btn-success btn-sm ml-2" to="/register">Регистрация</router-link>

    <!-- Приветствие и кнопка выхода, если пользователь авторизован -->
    <span v-else class="mr-2">Привет, {{ username }}</span>
    <button v-if="token" @click="logout" class="btn btn-danger btn-sm">Выход</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      token: localStorage.getItem('access_token') || '',
      username: localStorage.getItem('username') || '',
    };
  },
  methods: {
    logout() {
      // Очищаем данные пользователя
      localStorage.removeItem('access_token');
      localStorage.removeItem('username');
      localStorage.removeItem('user_name'); // Если используется для данных Яндекса

      // Перенаправляем на страницу логина
      this.$router.push({ name: 'Login' });
    },
  },
};
</script>