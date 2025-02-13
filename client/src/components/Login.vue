<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Вход</h1>
        <hr><br><br>
        <alert :message="message" v-if="showMessage"></alert>
        <form @submit.prevent="handleLoginSubmit">
          <div class="mb-3">
            <label for="loginEmail" class="form-label">Username:</label>
            <input
              type="email"
              class="form-control"
              id="loginEmail"
              v-model="loginForm.username"
              placeholder="Введите email">
          </div>
          <div class="mb-3">
            <label for="loginPassword" class="form-label">Пароль:</label>
            <input
              type="password"
              class="form-control"
              id="loginPassword"
              v-model="loginForm.password"
              placeholder="Введите пароль">
          </div>
          <div class="btn-group" role="group">
            <button
              type="submit"
              class="btn btn-primary btn-sm">
              Войти
            </button>
          </div>
          <p class="mt-3">Еще не зарегистрированы? <router-link to="/register">Зарегистрируйтесь</router-link></p>
        </form>

        <!-- Кнопка для авторизации через Яндекс -->
        <div class="mt-4">
          <button class="btn btn-secondary btn-sm" @click="startYandexAuth">Войти через Яндекс</button>
        </div>
        <!-- Контейнер для кнопки SDK -->
    <div id="buttonContainerId"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';

export default {
  data() {
    return {
      yandexAuthInProgress: false,
      loginForm: {
        username: '',
        password: '',
      },
      message: '',
      showMessage: false,
    };
  },

  methods: {
    startYandexAuth() {
      console.log('Кнопка "Войти через Яндекс" нажата');
      if (this.yandexAuthInProgress) {
        console.warn('Авторизация уже в процессе.');
        return;
      }
      this.yandexAuthInProgress = true;

      const script = document.createElement('script');
      script.src = 'https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-with-polyfills-latest.js';
      script.onload = () => {
        console.log('SDK Яндекса успешно загружен');

        window.YaAuthSuggest.init(
          {
            client_id: 'e5b8dfc63c3c47f4965c09159fdd779c', // Ваш client_id
            response_type: 'token',
            redirect_uri: 'http://localhost:8080/tokenhandler', // Ваш redirect_uri
          },
          'http://localhost:8080', // Ваш origin
          {
            view: 'button',
            parentId: 'buttonContainerId',
            buttonSize: 'm',
            buttonView: 'main',
            buttonTheme: 'light',
            buttonBorderRadius: '0',
            buttonIcon: 'ya',
          }
        )
          .then(({ handler }) => {
            console.log('Инициализация SDK Яндекс успешна');
            return handler();
          })
          .then(data => {
            console.log('Данные после авторизации:', data);
            if (!data || !data.access_token) {
              throw new Error('Токен не получен.');
            }
            console.log('Токен получен:', data.access_token);
            this.sendTokenToServer(data.access_token);
          })
          .catch(error => {
            console.error('Ошибка авторизации:', error);
            alert(`Ошибка при входе через Яндекс: ${error.message}`);
          })
          .finally(() => {
            this.yandexAuthInProgress = false;
          });
      };
      script.onerror = () => {
        console.error('Ошибка при загрузке SDK Яндекса.');
        alert('Ошибка при загрузке модуля авторизации. Попробуйте снова.');
        this.yandexAuthInProgress = false;
      };
      document.head.appendChild(script);
    },

    sendTokenToServer(token) {
  axios.post('/api/auth/yandex', { token: token })
    .then(response => {
      console.log('Ответ от бекенда:', response.data);
      // Извлекаем данные пользователя
      const user = response.data.user;
      const user_id = user.id; // Извлекаем user_id
      // Сохраняем токен и данные пользователя в localStorage
       // Проверки
        if (!user) {
          throw new Error('Данные пользователя не найдены в ответе Яндекса');
        }

        const user_name = user.login;

        if (!user_name) {
          throw new Error('Логин пользователя не найден в ответе Яндекса');
        }

        // Сохраняем данные
       localStorage.setItem('access_token', token);
      localStorage.setItem('user_name', user_name);
      localStorage.setItem('user_id', user_id);

      // Закрываем окно только после успешного завершения
      if (window.opener) {
        window.opener.postMessage({ type: 'yandexAuthSuccess', token: response.data.user.access_token }, '*');
        window.close();
        // Отправляем событие
        this.$root.$eventBus.dispatchEvent(new CustomEvent('login-success'));
      } else {
        this.$router.push({ name: 'Main' });
      }
    })
    .catch(error => {
      console.error('Ошибка при отправке токена:', error);
      alert('Ошибка при входе через Яндекс. Попробуйте снова.');
    });
},

    handleLoginSubmit() {
      const payload = {
        username: this.loginForm.username,
        password: this.loginForm.password,
      };
      this.loginUser(payload);
    },

    loginUser(payload) {
      const path = `/api/login`;
      axios.post(path, payload)
        .then((response) => {
          const token = response.data.access_token;
          const user_id = response.data.user_id;
          localStorage.setItem('access_token', token);
          localStorage.setItem('user_name', this.loginForm.username);
          localStorage.setItem('user_id', user_id);
          this.message = 'Вход выполнен успешно!';
          this.showMessage = true;
          this.resetForm();
          // Отправляем событие
          this.$root.$eventBus.dispatchEvent(new CustomEvent('login-success'));
          this.$router.push({ name: 'Main' });
        })
        .catch((error) => {
          console.error(error);
          this.showMessage = false;
          this.message = 'Ошибка при входе. Проверьте правильность email и пароля.';
        });
    },

    resetForm() {
      this.loginForm.username = '';
      this.loginForm.password = '';
    },

    handleMessage(event) {
      if (event.data.type === 'yandexAuthSuccess') {
        const token = event.data.token;
        console.log('Токен получен во всплывающем окне:', token);
        // Сохраняем токен и перенаправляем пользователя
        localStorage.setItem('access_token', token);
          // Вызываем sendTokenToServer в основном окне
      this.sendTokenToServer(token);
        this.$router.push({ name: 'Books' });
      }
    },
  },

  mounted() {
    window.addEventListener('message', this.handleMessage);
  },

  beforeDestroy() {
    window.removeEventListener('message', this.handleMessage);
  },

  beforeRouteEnter(to, from, next) {
  const token = localStorage.getItem('access_token');
  const user_id = localStorage.getItem('user_id');

  console.log('Токен в localStorage:', token);
  console.log('Данные пользователя в localStorage:', user_id);

  if (to.name === 'Login' && token) {
    // Если пользователь уже авторизован и пытается зайти на страницу логина
    next({ name: 'Main' });
  } else if (!token && to.name !== 'Login') {
    // Если пользователь не авторизован и пытается зайти на другую страницу
    next({ name: 'Login' });
  } else {
    // В остальных случаях разрешаем переход
    next();
  }
},
};
</script>