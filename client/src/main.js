import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import { loadFonts } from './plugins/webfontloader';
import 'bootstrap/dist/css/bootstrap.css';

// Загружаем шрифты
loadFonts();

// Создаем приложение
const app = createApp(App);

// Подключаем плагины
app.use(router);
app.use(vuetify);
// Создаем глобальное реактивное состояние
// Создаем реактивное состояние
// Создаем глобальное событие
app.config.globalProperties.$eventBus = new window.EventTarget();

app.use(router).mount('#app');
