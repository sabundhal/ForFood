<template>
  <div class="user-info">
    <h2>Информация о пользователе</h2>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <p><strong>ID:</strong> {{ user.id }}</p>
      <p><strong>Имя пользователя:</strong> {{ user.username }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Yandex ID:</strong> {{ user.yandex_id || 'Не указан' }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'UserInfo',
  setup() {
    const user = ref(null);  // Данные пользователя
    const loading = ref(true);  // Состояние загрузки
    const error = ref(null);  // Сообщение об ошибке

    // Функция для получения информации о пользователе
    const fetchUserInfo = async () => {
      try {
        const token = localStorage.getItem('access_token');  // Получаем токен из localStorage
        const response = await axios.get('/api/user', {
          headers: {
            'Authorization': `Bearer ${token}`  // Передаем токен в заголовке
          }
        });
        user.value = response.data;  // Сохраняем данные пользователя
      } catch (err) {
        error.value = 'Ошибка при загрузке информации о пользователе';
        console.error(err);
      } finally {
        loading.value = false;  // Завершаем загрузку
      }
    };

    // Вызываем fetchUserInfo при монтировании компонента
    onMounted(() => {
      fetchUserInfo();
    });

    return {
      user,
      loading,
      error
    };
  }
};
</script>

<style scoped>
.user-info {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

h2 {
  margin-bottom: 20px;
  text-align: center;
}

.error {
  color: red;
  text-align: center;
}
</style>