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

      <!-- Список детей -->
      <h3>Дети</h3>
      <div v-if="childrenLoading">Загрузка списка детей...</div>
      <div v-else-if="childrenError" class="error">{{ childrenError }}</div>
      <ul v-else>
        <li v-for="child in children" :key="child.id">
          <div @click="selectChild(child)" class="child-info">
            {{ child.name }} ({{ child.birth_date }})
          </div>
          <div class="child-actions">
            <v-btn icon @click.stop="editChild(child)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon @click.stop="deleteChild(child.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </div>
        </li>
      </ul>

      <!-- Информация о выбранном ребенке -->
      <div v-if="selectedChild">
        <h3>Информация о ребенке</h3>
        <p><strong>Имя:</strong> {{ selectedChild.name }}</p>
        <p><strong>Дата рождения:</strong> {{ selectedChild.birth_date }}</p>
        <p><strong>Пол:</strong> {{ selectedChild.gender === 'male' ? 'Мужской' : 'Женский' }}</p>
        <p><strong>Рост:</strong> {{ selectedChild.height }} см</p>
        <p><strong>Вес:</strong> {{ selectedChild.weight }} кг</p>
        <p><strong>Аллергены:</strong></p>
        <ul>
          <li v-for="allergen in selectedChild.allergens" :key="allergen.id">
            {{ allergen.name }}
          </li>
        </ul>
      </div>

      <!-- Кнопка для раскрытия формы -->
      <v-btn @click="showForm = !showForm" class="add-button">
        {{ showForm ? 'Скрыть форму' : 'Добавить ребенка' }}
      </v-btn>

      <!-- Форма создания/редактирования ребенка -->
      <form v-if="showForm" @submit.prevent="editingChild ? updateChild(editingChild.id) : createChild" class="child-form">
        <label>
          Имя:
          <input v-model="newChild.name" type="text" required class="form-input" />
        </label>
        <label>
          Дата рождения:
          <input v-model="newChild.birth_date" type="date" required class="form-input" />
        </label>
        <label>
          Пол:
          <select v-model="newChild.gender" required class="form-input">
            <option value="male">Мужской</option>
            <option value="female">Женский</option>
          </select>
        </label>
        <label>
          Рост (см):
          <input v-model="newChild.height" type="number" step="0.1" required class="form-input" />
        </label>
        <label>
          Вес (кг):
          <input v-model="newChild.weight" type="number" step="0.1" required class="form-input" />
        </label>
        <label>
          Аллергены (через запятую):
          <input v-model="newChild.allergens" type="text" class="form-input" />
        </label>
        <v-btn type="submit" class="submit-button">{{ editingChild ? 'Сохранить' : 'Добавить' }}</v-btn>
        <v-btn v-if="editingChild" @click="cancelEdit" class="cancel-button">Отмена</v-btn>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'UserInfo',
  setup() {
    const user = ref(null);
    const loading = ref(true);
    const error = ref(null);

    const children = ref([]);
    const childrenLoading = ref(true);
    const childrenError = ref(null);

    const selectedChild = ref(null);
    const newChild = ref({
      name: '',
      birth_date: '',
      gender: 'male',
      height: null,
      weight: null,
      allergens: ''
    });

    const showForm = ref(false);
    const editingChild = ref(null);

    const fetchUserInfo = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('/api/user', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        user.value = response.data;
      } catch (err) {
        error.value = 'Ошибка при загрузке информации о пользователе';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const fetchChildren = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('/api/children', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        children.value = response.data;
      } catch (err) {
        childrenError.value = 'Ошибка при загрузке списка детей';
        console.error(err);
      } finally {
        childrenLoading.value = false;
      }
    };

    const createChild = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const allergens = newChild.value.allergens
          ? newChild.value.allergens.split(',').map(id => parseInt(id.trim()))
          : [];
        const response = await axios.post(
          '/api/children',
          {
            user_id: user.value.id,
            name: newChild.value.name,
            birth_date: newChild.value.birth_date,
            gender: newChild.value.gender,
            height: newChild.value.height,
            weight: newChild.value.weight,
            allergens: allergens
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        children.value.push(response.data);
        newChild.value = {
          name: '',
          birth_date: '',
          gender: 'male',
          height: null,
          weight: null,
          allergens: ''
        };
        showForm.value = false;
        await fetchChildren();
      } catch (err) {
        console.error('Ошибка при создании ребенка:', err);
      }
    };

    const editChild = (child) => {
      editingChild.value = child;
      newChild.value = {
        name: child.name,
        birth_date: child.birth_date,
        gender: child.gender,
        height: child.height,
        weight: child.weight,
        allergens: child.allergens.join(',')
      };
      showForm.value = true;
    };

    const updateChild = async (childId) => {
      try {
        const token = localStorage.getItem('access_token');
        const allergens = newChild.value.allergens
          ? newChild.value.allergens.split(',').map(id => parseInt(id.trim()))
          : [];
        const response = await axios.put(
          `/api/children/${childId}`,
          {
            name: newChild.value.name,
            birth_date: newChild.value.birth_date,
            gender: newChild.value.gender,
            height: newChild.value.height,
            weight: newChild.value.weight,
            allergens: allergens
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
        await fetchChildren();
        cancelEdit();
      } catch (err) {
        console.error('Ошибка при редактировании ребенка:', err);
      }
    };

    const deleteChild = async (childId) => {
      try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`/api/children/${childId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        await fetchChildren();
      } catch (err) {
        console.error('Ошибка при удалении ребенка:', err);
      }
    };

    const cancelEdit = () => {
      editingChild.value = null;
      newChild.value = {
        name: '',
        birth_date: '',
        gender: 'male',
        height: null,
        weight: null,
        allergens: ''
      };
      showForm.value = false;
    };

    const selectChild = (child) => {
      selectedChild.value = child;
    };

    onMounted(() => {
      fetchUserInfo();
      fetchChildren();
    });

    return {
      user,
      loading,
      error,
      children,
      childrenLoading,
      childrenError,
      selectedChild,
      newChild,
      showForm,
      editingChild,
      createChild,
      editChild,
      updateChild,
      deleteChild,
      cancelEdit,
      selectChild
    };
  }
};
</script>

<style scoped>
.user-info {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}

h2, h3 {
  margin-bottom: 20px;
  text-align: center;
}

.error {
  color: red;
  text-align: center;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  padding: 10px;
  border: 1px solid #ddd;
  margin-bottom: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.child-info {
  flex-grow: 1;
}

.child-actions {
  display: flex;
  gap: 8px;
}

.add-button {
  margin-bottom: 20px;
}

.child-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-input {
  padding: 8px;
  border: none;
  border-bottom: 1px solid #ccc;
  background-color: transparent;
  outline: none;
}

.form-input:focus {
  border-bottom: 1px solid #007bff;
}

.submit-button {
  background-color: #28a745;
  color: white;
}

.cancel-button {
  background-color: #dc3545;
  color: white;
}
</style>