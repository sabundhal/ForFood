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
      <div class="title__section-label title__section-item">Калькулятор детской дозировки</div>
    </div>

    <div class="drug_calc">
      <form id="drugform" @submit.prevent="validate">
        <div class="error__section" id="warning-message"></div>
        <div class="error__section" id="error-message"></div>


    <!-- Вес -->
    <div class="weight__section">
      <div class="weight__section-item weight__section-label">Вес (кг)</div>
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
        <option value="None">Выберите препарат</option>
        <optgroup v-for="(drugs, category) in drugsByCategories" :key="category" :label="category">
          <option v-for="drug in drugs" :key="drug.id" :value="drug.id">
            {{ drug.name }}
          </option>
        </optgroup>
      </select>
    </div>

        <div class="calculate__section">
          <input type="button" id="calcbutton" value="Рассчитать" @click=calculateDosage() />
        </div>

       <div class="result__section">
        <div class="result__section-mls" v-if="standard_dose_ml">
            <div class="result__section-mls-item result__section-mls-label">
                Дозировка <br />в миллилитрах (что набирать в шприц)
            </div>
            <div class="result__section-mls-item result__section-mls-result" id="Result" style="display: block">
                {{ standard_dose_ml }} <!-- Отображаем значение мл -->
            </div>

        </div>
        <div class="result__section-mgs" v-if="high_dose_ml">
            <div class="result__section-mgs-item result__section-mgs-label">
                Повышенная доза <br />в миллилитрах (что набирать в шприц)
            </div>
            <div class="result__section-mgs-item result__section-mgs-result" id="ResultMgs" style="display: block">
                {{ high_dose_ml }} <!-- Отображаем значение мг -->
            </div>

        </div>
    <div class="result__section-max-mgs" v-if="max_dose_ml">
            <div class="result__section-max-mgs-item result__section-max-mgs-label">
                Максимальная доза в день <br />!!!ПРЕВЫШЕНИЕ НЕДОПУСТИМО!!!
            </div>
            <div class="result__ssection-max-mgs-item result__section-max-mgs-result" id="ResultMgs" style="display: block">
                {{ max_dose_ml }} <!-- Отображаем значение мг -->
            </div>

        </div>
        <div class="result__section">
        <div class="result__section-supp-min"  v-if="suppositories_min">
            <div class="result__ssection-supp-min-item result__section-supp-min-label">
                Обычная доза <br />ректальных суппозиториев (шт)
            </div>
            <div class="result__section-supp-min-item result__section-supp-min-result" id="Result" style="display: block">
                {{ suppositories_min }} <!-- Отображаем значение мл -->
            </div>

        </div>

    </div>
             <div class="result__section">
        <div class="result__section-supp-high"  v-if="suppositories_high">
            <div class="result__section-supp-high-item result__section-supp-high-label">
                Повышенная доза <br />ректальных суппозиториев (шт)
            </div>
            <div class="result__section-supp-high-item result__section-supp-high-result" id="Result" style="display: block">
                {{ suppositories_high }} <!-- Отображаем значение мл -->
            </div>
        </div>
    </div>
    </div>

      </form>
    </div>
        <!-- Сообщения об ошибках -->
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div class="info__section" v-if="nzf_link || number_of_times_a_day || instructions">
  <!-- Инструкции по применению -->
  <div class="info__section-item" v-if="instructions">
    <div class="info__section-label">Инструкции:</div>
    <div class="info__section-text">{{ instructions }}</div>
  </div>

  <!-- Количество приемов в день -->
  <div class="info__section-item" v-if="number_of_times_a_day">
    <div class="info__section-label">Количество приемов в день:</div>
    <div class="info__section-text">{{ number_of_times_a_day }}</div>
  </div>



</div>



    <div class="message__section-dosing" id="dosing-section" style="display: none">
      <div class="message__section-dosing-item message__section-dosing-label" id="instructions"></div>
    </div>

    <div class="calculator__footer">
    <div class="result__section" v-if="link2">
    <div class="result__section-mls" v-if="link1">
        <div class="result__section-mls-item result__section-mls-label">
            Ссылка Горминздрав:
        </div>
        <div class="result__section-mls-item result__section-mls-result">
            <a :href="link1" target="_blank">{{ link1 }}</a>
        </div>
    </div>

    <div class="result__section-mls" v-if="link2">
        <div class="result__section-mls-item result__section-mls-label">
            Ссылка Аптека:
        </div>
        <div class="result__section-mls-item result__section-mls-result">
            <a :href="link2" target="_blank">{{ link2 }}</a>
        </div>
    </div>
</div>

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
      standard_dose_ml: '', // Реактивное свойство для мл
      high_dose_ml: '', // Реактивное свойство для мг
      max_dose_ml: '', // Реактивное свойство для мг
      suppositories_high: '',
      suppositories_min: '',
      errorMessage: "",
      warningMessage: "",
      weightBorder: "1px solid #cacaca",
      drugBorder: "1px solid #cacaca",
      token: localStorage.getItem('access_token') || '', // Токен авторизации
      username: '', // Имя пользователя
      instructions: '',
      number_of_times_a_day: '',
      nzf_link: '',
      link1: null, // Инициализация для первой ссылки
      link2: null  // Инициализация для второй ссылки
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
        this.standard_dose_ml = data.standard_dose_ml; // Обновляем молярные данные
        this.high_dose_ml = data.high_dose_ml;
        this.max_dose_ml = data.max_dose_ml;
        this.suppositories_high = data.suppositories_high;
        this.suppositories_min = data.suppositories_min;
        this.instructions = data.instructions;
        this.number_of_times_a_day = data.number_of_times_a_day;
        // Разделяем строку на две ссылки и обрезаем пробелы
        const links = data.nzf_link.split(' ').map(link => link.trim());
        console.log('Разделенные ссылки:', links); // Проверка в консоли

        if (links.length > 1) {
            this.link1 = links[0]; // Первая ссылка
            this.link2 = links[2]; // Вторая ссылка
        } else if (links.length === 1) {
            this.link1 = links[0]; // Только первая ссылка
            this.link2 = null; // Очищаем вторую ссылку
        } else {
            this.link1 = null;
            this.link2 = null;
        }

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
        splitLinks(links) {
      // Разделяем строку по пробелам и фильтруем пустые значения
      return links.split(/\s+/).filter(link => link.trim() !== '');
    },
    validate() {
     console.log('Validate method called'); // Лог для проверки
      this.clearErrors();

      if (this.weight === "") {
        this.showError("Введите вес", "weight");
      } else if (this.weight < 0) {
        this.showError("Вес не может быть отрицательным", "weight");
      } else if (this.weight > 100) {
        console.log('Validate 100'); // Лог для проверки
        this.showError("Введите вес менее 100кг.", "weight");
      } else if (this.selectedDrug === "None") {
        this.showError("Выберите препарат", "drug");
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
      this.max_dose_ml = null;
      this.suppositories_high = null;
      this.suppositories_min = null;

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
  logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_name');
      localStorage.removeItem('user_id');
      this.token = ''; // Очищаем токен
      this.username = ''; // Очищаем username
      this.$router.push('/login'); // Перенаправляем на страницу входа
    }

 }
}

</script>
<style scoped>
/* Добавьте ваши стили здесь */
@import '../assets/calculator-style.css';
.info__section {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.info__section-item {
  margin-bottom: 15px;
}

.info__section-label {
  font-weight: bold;
  margin-bottom: 5px;
}

.info__section-text {
  white-space: pre-line; /* Сохраняет форматирование текста */
}

.info__section-link {
  color: #007bff;
  text-decoration: none;
}

.info__section-link:hover {
  text-decoration: underline;
}
</style>
