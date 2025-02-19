<template>
<div>
  <div class="row">
   <div class="col-md-8"></div>
   <div class="col-md-4">
          <span  v-if="!token" class="mr-2">Привет, выполни регистрацию и вход</span>
          <span v-else class="mr-2">Привет, {{ username }}</span>
  </div>
  </div>

    <!-- Остальная часть страницы -->
    <h1>Главная страница</h1>
    <p>Здесь будет список...</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      token: localStorage.getItem('access_token') || '', // Токен авторизации
      username: '', // Имя пользователя
    };
  },
  created() {
    this.username = localStorage.getItem('user_name') || ''; // Загружаем username из localStorage
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_name');
      localStorage.removeItem('user_id');
      this.token = ''; // Очищаем токен
      this.username = ''; // Очищаем username
      this.$router.push('/login'); // Перенаправляем на страницу входа
    },
  },
};
</script>

<style>
.greeting {
  margin-bottom: 1rem;
}
.btn {
  margin-left: 0.5rem;
}
</style>