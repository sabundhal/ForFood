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
  <div id="calculator">
    <div class="title__section">
      <div class="title__section__image title__section-item">
        <img id="calcicon" src="https://www.jackofallorgans.com/wp-content/uploads/2017/12/SyrupBottle2.png" alt="Calculator Icon" />
      </div>
      <div class="title__section-label title__section-item">Paediatric Dose Calculator</div>
    </div>

    <div class="drug_calc">
      <form id="drugform" @submit.prevent="validate">
        <div class="error__section" id="warning-message"></div>
        <div class="error__section" id="error-message"></div>


    <!-- Вес -->
    <div class="weight__section">
      <div class="weight__section-item weight__section-label">Weight (kg)</div>
      <input
        class="weight__section-item weight__section-input"
        id="theweight"
        v-model="weight"
        min="1"
        max="100"
        type="number"
        ref="weightInput"
        @click="clearResults"
        @select="clearResults"
      />
    </div>

     <!-- Выбор препарата -->
    <div class="drug__section">
      <select id="drug" ref="drugIdInput" v-model="selectedDrug" @change="validate">
        <option value="None">Select Drug</option>
        <optgroup v-for="(drugs, category) in drugsByCategories" :key="category" :label="category">
          <option v-for="drug in drugs" :key="drug.id" :value="drug.id">
            {{ drug.name }}
          </option>
        </optgroup>
      </select>
    </div>

        <div class="calculate__section">
          <input type="button" id="calcbutton" value="Calculate" @click=calculateDosage() />
        </div>

       <div class="result__section">
        <div class="result__section-mls">
            <div class="result__section-mls-item result__section-mls-label">
                Dose <br />in millilitres
            </div>
            <div class="result__section-mls-item result__section-mls-result" id="Result" style="display: block">
                {{ mlsTotal }} <!-- Отображаем значение мл -->
            </div>
            <button class="result__section-mls-item clipboard btn tippy copy"
                    data-tippy-content="Copied to Clipboard"
                    title="Copy to Clipboard"
                    @click="copyToClipboard('Result')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="16" height="16">
    <path d="M502.6 70.63l-61.25-61.25C435.4 3.371 427.2 0 418.7 0H255.1c-35.35 0-64 28.66-64 64l.0195 272C191.1 372.4 220.7 400 256 400h192c35.2 0 64-28.8 64-64V93.25C512 84.77 508.6 76.63 502.6 70.63zM464 320c0 8.836-7.164 16-16 16H255.1c-8.838 0-16-7.164-16-16L239.1 64.13c0-8.836 7.164-16 16-16h128L384 96c0 17.67 14.33 32 32 32h47.1V320zM272 448c0 8.836-7.164 16-16 16H63.1c-8.838 0-16-7.164-16-16L47.98 224.1c0-8.836 7.164-16 16-16H160V256H64.02L63.99 416h192V448z"/>
  </svg>
  Копировать
</button>
        </div>
        <div class="result__section-mgs">
            <div class="result__section-mgs-item result__section-mgs-label">
                Dose <br />in milligrams
            </div>
            <div class="result__section-mgs-item result__section-mgs-result" id="ResultMgs" style="display: block">
                {{ mgsTotal }} <!-- Отображаем значение мг -->
            </div>
            <button class="result__section-mgs-item clipboard btn tippy copy"
                    data-tippy-content="Copied to Clipboard"
                    title="Copy to Clipboard"
                    @click="copyToClipboard('ResultMgs')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="16" height="16">
    <path d="M502.6 70.63l-61.25-61.25C435.4 3.371 427.2 0 418.7 0H255.1c-35.35 0-64 28.66-64 64l.0195 272C191.1 372.4 220.7 400 256 400h192c35.2 0 64-28.8 64-64V93.25C512 84.77 508.6 76.63 502.6 70.63zM464 320c0 8.836-7.164 16-16 16H255.1c-8.838 0-16-7.164-16-16L239.1 64.13c0-8.836 7.164-16 16-16h128L384 96c0 17.67 14.33 32 32 32h47.1V320zM272 448c0 8.836-7.164 16-16 16H63.1c-8.838 0-16-7.164-16-16L47.98 224.1c0-8.836 7.164-16 16-16H160V256H64.02L63.99 416h192V448z"/>
  </svg>
  Копировать
</button>
        </div>
    </div>
      </form>
    </div>
        <!-- Сообщения об ошибках -->
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div class="message__section-dosing" id="dosing-section" style="display: none">
      <div class="message__section-dosing-item message__section-dosing-label" id="instructions"></div>
    </div>

    <div class="calculator__footer">
      <div class="calculator__footer-item calculator__footer-information">Further Information:</div>
      <div class="tippy" data-tippy="NZ Formulary">
        <a class="calculator__footer-item" href="https://nzfchildren.org.nz" target="_blank" id="nzflink">
          <img border="0" alt="nzf" src="https://www.jackofallorgans.com/wp-content/uploads/2018/11/nzf.png" width="32" height="32" />
        </a>
      </div>
      <div class="tippy" data-tippy="BPAC Antibiotic Guide">
        <a class="calculator__footer-item" href="https://bpac.org.nz/antibiotics/guide.aspx" target="_blank">
          <img border="0" alt="nzf" src="https://www.jackofallorgans.com/wp-content/uploads/2018/11/bpac-1.png" width="32" height="32" />
        </a>
      </div>
      <div class="tippy" data-tippy="Antimicrobial Susceptibility Report for 2017">
        <a class="calculator__footer-item" href="https://www.jackofallorgans.com/wp-content/uploads/AST-2017-Table-1.pdf" target="_blank">
          <img border="0" alt="nzf" src="https://www.jackofallorgans.com/wp-content/uploads/labtest-logo.png" width="32" height="32" />
        </a>
      </div>
    </div>


  </div>

</template>

<script>
import axios from 'axios';

export default {
  name: 'PediatricCalculator',
  data() {
    return {
      weight: "",
      selectedDrug: "None",
      drugsByCategories: {}, // Данные, сгруппированные по категориям
      mlsTotal: '', // Реактивное свойство для мл
      mgsTotal: '', // Реактивное свойство для мг
      errorMessage: "",
      warningMessage: "",
      weightBorder: "1px solid #cacaca",
      drugBorder: "1px solid #cacaca",
      token: localStorage.getItem('access_token') || '', // Токен авторизации
      username: '', // Имя пользователя
    };
  },
  created() {
    // Загружаем данные при создании компонента
    this.loadDrugs();
    this.username = localStorage.getItem('user_name') || ''; // Загружаем username из localStorage
  },
  methods: {
    calculateDosage() {
     const user_id = localStorage.getItem('user_id');

    // Проверяем, что user_id существует
    if (!user_id) {
        this.error = 'Пользователь не авторизован. Пожалуйста, войдите в систему.';
        return; // Прерываем выполнение, если user_id отсутствует
    }

    // Получаем значения из элементов формы
    const drugId = this.$refs.drugIdInput.value;
    const weight = this.$refs.weightInput.value;

    // Проверяем, что все поля заполнены
    if (!drugId || !weight) {
        this.error = 'Пожалуйста, заполните все поля.';
        return; // Прерываем выполнение, если данные не заполнены
    }

    // Создаем объект данных для отправки
    const requestData = {
        user_id: `${localStorage.getItem('user_id')}`, // Получаем user_id из localStorage
        drug_id: drugId, // ID препарата
        weight: weight // Вес пациента
    };

    // Отправляем запрос на сервер
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData) // Преобразуем данные в JSON
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка сервера: ' + response.status);
        }
        return response.json(); // Парсим ответ от сервера
    })
    .then(data => {
        this.result = data; // Устанавливаем результат
        this.mlsTotal = data.mlsTotal; // Обновляем молярные данные
        this.mgsTotal = data.mgsTotal;
    })
    .catch(error => {
        this.error = 'Ошибка при выполнении запроса: ' + error.message;
    });
        },
        // Метод для копирования в буфер обмена
        copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            navigator.clipboard.writeText(element.textContent).then(() => {
                alert('Скопировано в буфер обмена!');
            });
        },
    validate() {
     console.log('Validate method called'); // Лог для проверки
      this.clearErrors();

      if (this.weight === "") {
        this.showError("Please input a weight", "weight");
      } else if (this.weight < 0) {
        this.showError("Cannot be negative weight.", "weight");
      } else if (this.weight > 100) {
        console.log('Validate 100'); // Лог для проверки
        this.showError("Please enter a weight below 100kg.", "weight");
      } else if (this.selectedDrug === "None") {
        this.showError("Please select a drug", "drug");
      }
    },

    showError(message, field) {
      this.errorMessage = message;

      if (field === "weight") {
        this.weightBorder = "1px solid red";
      } else if (field === "drug") {
        this.drugBorder = "1px solid red";
      }
    },
    clearErrors() {
      this.errorMessage = "";
      this.weightBorder = "1px solid #cacaca";
      this.drugBorder = "1px solid #cacaca";
    },
    clearResults() {
      this.mlsTotal = null;
      this.mgsTotal = null;
    },
    calculateMlsTotal() {
      // Пример расчета (замените на вашу логику)
      this.mlsTotal = this.weight * 2; // Пример: 2 мл на каждый кг
    },
    calculateMgsTotal() {
      // Пример расчета (замените на вашу логику)
      this.mgsTotal = this.weight * 5; // Пример: 5 мг на каждый кг
    },
    copyToClipboard(elementId) {
      const element = document.getElementById(elementId);
      if (element) {
        const text = element.innerText;
        navigator.clipboard.writeText(text);
      }
    },
    loadDrugs() {
      // Загружаем данные из API
      axios.get('/api/drugs')
        .then(response => {
          this.drugsByCategories = response.data;
        })
        .catch(error => {
          console.error('Error fetching drugs:', error);
        });
    },
  },
  logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_name');
      localStorage.removeItem('user_id');
      this.token = ''; // Очищаем токен
      this.username = ''; // Очищаем username
      this.$router.push('/login'); // Перенаправляем на страницу входа
    }

};

</script>
<style scoped>
/* Добавьте ваши стили здесь */
@import '../assets/calculator-style.css';
</style>
