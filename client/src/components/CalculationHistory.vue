<template>

   <div class="row">
   <div class="col-md-8"></div>
   <div class="col-md-4">
          <router-link v-if="!token" class="btn btn-primary btn-sm" to="/login">Вход</router-link>
          <router-link v-if="!token" class="btn btn-success btn-sm ml-2" to="/register">Регистрация</router-link>
          <span v-else class="mr-2">Привет, {{ username }}</span>
          <button v-if="token" @click="logout" class="btn btn-danger btn-sm">Выход</button>
  </div>
  </div>

  <div class="history">
    <!-- Поля для фильтрации -->
    <div class="filters">
      <div class="filter-item">
        <label>Категория препарата:</label>
        <select v-model="selectedCategory">
          <option value="">Все категории</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <div class="filter-item">
        <label>Дата с:</label>
        <input type="date" v-model="dateFrom" />
      </div>

      <div class="filter-item">
        <label>Дата по:</label>
        <input type="date" v-model="dateTo" />
      </div>

      <button @click="fetchData" class="fetch-button">Запросить данные</button>
    </div>

   <!-- Таблица с данными -->
<div v-if="history.length > 0" class="history-table">
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Дата</th>
        <th>Название препарата</th>
        <th>Категория</th>
        <th>Вес (кг)</th>
        <th>Доза (мл)</th>
        <th>Доза (мг)</th>
        <th>ID пользователя</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in history" :key="item.id">
        <td>{{ item.id }}</td>
        <td>{{ formatDate(item.created_at) }}</td>
        <td>{{ item.drug_name }}</td>
        <td>{{ item.calculation_type }}</td>
        <td>{{ item.weight }}</td>
        <td>{{ item.mls }}</td>
        <td>{{ item.mgs }}</td>
        <td>{{ item.user_id }}</td>
      </tr>
    </tbody>
  </table>
</div>

    <p v-else class="no-data">Данные отсутствуют</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      categories: [],        // Список категорий из БД
      selectedCategory: "",  // Выбранная категория
      dateFrom: "",          // Дата "с"
      dateTo: "",            // Дата "по"
      history: [],           // История расчётов
      token: localStorage.getItem('access_token') || '', // Токен авторизации
      username: '', // Имя пользователя
    };
  },
  created() {
    this.username = localStorage.getItem('user_name') || ''; // Загружаем username из localStorage
  },
  mounted() {
    this.fetchCategories(); // Загружаем категории при монтировании компонента
  },
  methods: {
    // Загрузка категорий из БД
    fetchCategories() {
      axios.get('/api/drugs')
        .then(response => {
          console.log("Загрузка категорий..."); // Отладка
          this.categories = Object.keys(response.data);
        })
        .catch(error => {
          console.error('Ошибка при загрузке категорий:', error);
        });
    },

    // Запрос данных из БД с фильтрами
    async fetchData() {
      try {
        const params = {
          user_id: `${localStorage.getItem('user_id')}`, // Получаем user_id из localStorage
          category_name: this.selectedCategory,
          date_from: this.dateFrom,
          date_to: this.dateTo,
        };
        const response = await axios.get('/api/calculation-history/', { params });
        this.history = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке истории:", error);
      }
    },

    // Форматирование даты
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  },
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

<style scoped>
.history {
  margin: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-weight: bold;
}

select,
input[type="date"] {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.fetch-button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.fetch-button:hover {
  background-color: #0056b3;
}

.history-table {
  margin-top: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}

.no-data {
  margin-top: 20px;
  font-style: italic;
  color: #666;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.history-table th, .history-table td {
  padding: 8px 12px;
  border: 1px solid #ddd;
  text-align: left;
}

.history-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.history-table tr:hover {
  background-color: #f9f9f9;
}

</style>