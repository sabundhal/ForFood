<template>
  <div>Обработка токена...</div>
</template>

<script>
export default {
  mounted() {
    this.handleToken();
  },
  methods: {
    handleToken() {
      // Извлекаем токен из URL (пример URL: main#access_token=...)
      const hash = window.location.hash.substring(1); // Убираем "#"
      const params = new URLSearchParams(hash);
      const token = params.get('access_token');

      if (token) {
        console.log('Токен получен:', token);
        // Передаем токен в основное окно
        if (window.opener) {
          window.opener.postMessage({ type: 'yandexAuthSuccess', token: token }, '*');
          window.close(); // Закрываем всплывающее окно
        } else {
          console.error('Нет связи с родительским окном.');
          // Если окна нет, сохраняем токен и перенаправляем пользователя
          localStorage.setItem('access_token', token);
          this.$router.push({ name: 'Main' });
        }
      } else {
        console.error('Токен не найден в URL.');
        alert('Ошибка: токен не найден.');
      }
    },
  },
};
</script>