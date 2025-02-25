import { createRouter, createWebHistory } from 'vue-router';
import Register from '../components/Register.vue';
import Login from '../components/Login.vue';
import Main from '../components/Main.vue';
import Pediatric from '../components/Pediatric.vue';
import CalculationHistory from '../components/CalculationHistory.vue';
import TokenHandler from '../components/TokenHandler.vue';
import AuthButtons from '../components/AuthButtons.vue';
import Article from '../components/Article.vue';

const routes = [
  {
    path: '/',
    redirect: '/main'  // Перенаправляем с корневого пути на /main
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/tokenhandler',
    name: 'TokenHandler',
    component: TokenHandler,
  },
  {
    path: '/main',
    name: 'Main',
    component: Main,
  },
  {
    path: '/calculationhistory',
    name: 'CalculationHistory',
    component: CalculationHistory,
     meta: { requiresAuth: true }  // Добавляем мета-поле для проверки авторизации
  },
  {
    path: '/pediatric',
    name: 'Pediatric',
    component: Pediatric,
    meta: { requiresAuth: true }  // Добавляем мета-поле для проверки авторизации
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),  // Используем BASE_URL, если он есть
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');  // Проверка наличия токена
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');  // Перенаправляем на страницу логина, если пользователь не авторизован
  } else {
    next();  // Разрешаем переход
  }
});

export default router;