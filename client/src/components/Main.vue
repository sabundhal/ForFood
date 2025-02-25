<template>
  <div>
    <div class="row">
      <div class="col-md-8"></div>
      <div class="col-md-4">
        <span v-if="!token" class="mr-2">Привет, выполни регистрацию и вход</span>
        <span v-else class="mr-2">Привет, {{ username }}</span>
      </div>
    </div>

    <!-- Остальная часть страницы -->
    <h1>Главная страница</h1>
    <p>Здесь будет список статей:</p>
    <div v-for="article in articles" :key="article.id">
      <div class="article-preview" @click="toggleArticle(article.id)">
        <h3>{{ article.title }}</h3>
        <p>{{ article.preview }}</p>
      </div>
      <div v-if="article.isOpen" class="article-content">
        <Article :content="article.content" />
      </div>
    </div>
  </div>
</template>

<script>
import Article from '@/components/Article.vue';
import termo from '@/articles/termo.md?raw'; // Импортируем Markdown как сырой текст
import emegency from '@/articles/emegency.md?raw'; // Импортируем Markdown как сырой текст

export default {
  components: {
    Article,
  },
  data() {
    return {
      token: localStorage.getItem('access_token') || '',
      username: '',
      articles: [
        {
          id: 1,
          title: 'Статья 1',
          preview: 'Краткое описание статьи 1...',
          content: termo, // Полный текст статьи
          isOpen: false, // Статья свёрнута по умолчанию
        },
        {
          id: 2,
          title: 'Статья 2',
          preview: 'Краткое описание статьи 2...',
          content: emegency, // Полный текст статьи
          isOpen: false, // Статья свёрнута по умолчанию
        },
      ],
    };
  },
  created() {
    this.username = localStorage.getItem('user_name') || '';
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_name');
      localStorage.removeItem('user_id');
      this.token = '';
      this.username = '';
      this.$router.push('/login');
    },
    toggleArticle(articleId) {
      // Переключаем состояние статьи (раскрыть/свернуть)
      const article = this.articles.find((a) => a.id === articleId);
      if (article) {
        article.isOpen = !article.isOpen;
      }
    },
  },
};
</script>

<style>
.article-preview {
  cursor: pointer;
  padding: 10px;
  border: 1px solid #ccc;
  margin-bottom: 10px;
}
.article-content {
  padding: 10px;
  border: 1px solid #eee;
  background-color: #f9f9f9;
}
.greeting {
  margin-bottom: 1rem;
}
.btn {
  margin-left: 0.5rem;
}
</style>