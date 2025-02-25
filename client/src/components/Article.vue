<template>
  <div class="article" v-html="compiledMarkdown"></div>
</template>

<script>
import { marked } from 'marked'; // Установите библиотеку marked

export default {
  props: ['content'],
  computed: {
    compiledMarkdown() {
      return marked(this.content);
    }
  }
}
</script>