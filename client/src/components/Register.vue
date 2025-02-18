<template>
  <div class="container-fluid px-3">
    <div class="row justify-content-center">
      <div class="col-12 col-md-6 col-lg-4">
        <h1 class="text-center mb-3">Регистрация</h1>
        <hr class="mb-4">
        <alert :message="message" v-if="showMessage"></alert>
        <form>
          <div class="mb-3">
            <label for="registerUsername" class="form-label">Имя пользователя:</label>
            <input
              type="text"
              class="form-control"
              id="registerUsername"
              v-model="registerForm.username"
              placeholder="Введите имя пользователя"
            />
          </div>
          <div class="mb-3">
            <label for="registerEmail" class="form-label">Email:</label>
            <input
              type="email"
              class="form-control"
              id="registerEmail"
              v-model="registerForm.email"
              placeholder="Введите email"
            />
          </div>
          <div class="mb-3">
            <label for="registerPassword" class="form-label">Пароль:</label>
            <input
              type="password"
              class="form-control"
              id="registerPassword"
              v-model="registerForm.password"
              placeholder="Введите пароль"
            />
          </div>
          <div class="mb-3">
            <label for="registerConfirmPassword" class="form-label">Подтвердите пароль:</label>
            <input
              type="password"
              class="form-control"
              id="registerConfirmPassword"
              v-model="registerForm.confirmPassword"
              placeholder="Подтвердите пароль"
            />
          </div>
          <div class="d-grid gap-2">
            <button
              type="button"
              class="btn btn-primary"
              @click="handleRegisterSubmit"
            >
              Зарегистрироваться
            </button>
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="handleRegisterCancel"
            >
              Отмена
            </button>
          </div>
          <p class="text-center mt-4">
            Если вы уже зарегистрированы,
            <router-link to="/login" class="text-primary text-decoration-none">Войдите</router-link>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      },
      message: '',
      showMessage: false,
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
    registerUser(payload) {
      const path = `/api/register`;
      axios
        .post(path, payload)
        .then(() => {
          this.message = 'Пользователь зарегистрирован!';
          this.showMessage = true;
          this.resetForm();
          router.push({ name: 'Login' });
        })
        .catch((error) => {
          console.error(error);
          this.showMessage = false;
          this.message = 'Ошибка при регистрации пользователя.';
        });
    },
    handleRegisterSubmit() {
      let payload = {
        username: this.registerForm.username,
        email: this.registerForm.email,
        password: this.registerForm.password,
        confirmPassword: this.registerForm.confirmPassword,
      };
      this.registerUser(payload);
    },
    handleRegisterCancel() {
      this.resetForm();
    },
    resetForm() {
      this.registerForm.username = '';
      this.registerForm.email = '';
      this.registerForm.password = '';
      this.registerForm.confirmPassword = '';
    },
  },
};
</script>
