import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import { loadFonts } from './plugins/webfontloader';
import 'bootstrap/dist/css/bootstrap.css';
import './assets/styles/global.scss'; // Глобальные стили

// Загружаем шрифты
loadFonts();

// Создаем приложение
const app = createApp(App);
// Настройка Vuetify
app.use(vuetify, {
  defaults: {
    VMain: {
      // Отключаем автоматические отступы
      style: 'padding-top: 0;',
    },
  },
});
// Подключаем плагины
app.use(router);
app.use(vuetify);
// Создаем глобальное реактивное состояние
// Создаем реактивное состояние
// Создаем глобальное событие
app.config.globalProperties.$eventBus = new window.EventTarget();

app.use(router).mount('#app');
