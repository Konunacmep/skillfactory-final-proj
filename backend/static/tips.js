// js для удаления лишних элементов с формы а также для добавления подсказок
window.onload = function() { // нужны полная загрузка
    const questSelect = document.querySelector('#id_q_type') // переключатель типа вопроса
    const subButtons = document.querySelector('.submit-row') // кнопка "Сохранить"
    let addrowdd = document.querySelector('.add-row') // кнопка "добавить еще"
    const tip_field = document.createElement("div") // поле подсказок
    subButtons.insertBefore(tip_field, subButtons.children[0]) // добавляем его над кнопкой сохранить
    const saveBtn = document.querySelector('[name="_save"]')
    // костыль для фаерфокса.. document.querySelector('.add-row td a') работает в хроме, но не в ряде версий фокса
    let style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = '.new-hide a { display: none; }';
    document.getElementsByTagName('head')[0].appendChild(style);

// коллбэк, который будет срабатывать каждый раз, когда меняются важнеые поля
    function hinter(event) {
        saveBtn.disabled = false
        let closeBtn = document.querySelectorAll('.inline-deletelink') // кнопка удаления строки ответа "крестик"
        let hint = '' // подсказка, которую формируем
        let answers = document.querySelectorAll('.dynamic-answers') // все строки с ответами
        let found_correct = null
        function get_row_data(row) { 
            // функция проходит по всем ячейкам строки, выбирает те, элементы которых отвечают за верность ответа и баллы за него
            // и в зависимости от их значений выводит предупреждения
            let ans_weight = 0
            let ans_type = 1            
            for (let cell of row.cells) {
                if (cell.className == 'field-a_type') ans_type = cell.children[0]
                if (cell.className == 'field-weight') ans_weight = cell.children[0]
            }
            return {
                'ans_type': ans_type,
                'ans_weight': ans_weight,
            }
        }
        function chk_weight(ans_type, ans_weight, index) {
            if (ans_type == 1) {
                if (ans_weight > 0) hint += '<p>Вариант ответа ' + ( index + 1 ) + ' имеет положительный балл для неверного ответа, вы уверены?</p>'
                }
            else {
                if (ans_weight <= 0) hint += '<p>Вариант ответа ' + ( index + 1 ) + ' не имеет положительного балла, хоть и верен, вы уверены?</p>'
            }
        }
        if (questSelect) {
            // в зависимости от типа вопроса (значения 0, 1, 2) выполняем соответствующие приготовления
            switch(questSelect.value) {
                case '0':
                    // здесь мы формируем одну строку для ответа без функций
                    hint = '<p>Проверка может производиться как по точному вхождению слова или фразы в ответ, так и по частям. Например, если ответом на вопрос подразумевается фраза "лакокрасочное покрытие", то чтобы фраза, отвеченная в другом падеже ("лакокрасчоным покрытием") или множественном числа также засчиталась, в поле ответа необходимо указато только обязательные части слов, которые будут присутствовать в любой верной фразе т.е. "лакокрасоч покрыт"</p>'
                    addrowdd.classList.add("new-hide"); // скрываем кнопку добавления ответа
                    let { ans_type, ans_weight } = get_row_data(answers[0])
                    ans_type.value = '2' // неверного ответа быть не может
                    // ans_type.disabled = true 
                    function deleter() {
                        // удаляем лишние строки ответов
                        closeBtn = document.querySelectorAll('.inline-deletelink')
                        if (closeBtn.length > 1) {
                            closeBtn[closeBtn.length - 1].click()
                            deleter()
                        }
                    }
                    if (closeBtn.length) {
                        deleter()
                    } else {
                        closeBtn = document.querySelectorAll('.delete')
                    }
                    // скрываем кнопку удаления ответа
                    closeBtn[0].style.cssText = 'display:none;'
                    chk_weight(ans_type.value, ans_weight.value, 0)
                    break;
                case '1':
                    // нужно найти правильный ответ и задизейблить все остальные, пока остается "верный" хоть в одной строчке. Если их больше - оставить только первый
                    if (answers.length < 2) hint = '<p>Рекомендуем добавить несколько вариантов ответа для "вопроса с одним правильным ответом"</p>'
                    found_correct = 0
                    let corr_array = [] // массив всех селекторов верный/неверный
                    for (let row of answers) {
                        let { ans_type, ans_weight } = get_row_data(row)
                        corr_array.push([ans_type, ans_weight])
                        if (ans_type.value == 2) found_correct += 1
                    }
                    // если есть хоть один верный, дизейблим остальные                   
                    if (found_correct > 1) {
                        corr_array.forEach(x => {
                            console.log(x[0].id, event.target.id)
                            if (x[0].id != event.target.id) x[0].value = '1'
                        })
                    } else {
                        if (found_correct < 1) {
                            hint += '<p style="color:red;">Необходимо выбрать верный ответ</p>'
                            saveBtn.disabled = true
                        }
                    }  
                    corr_array.forEach((x,y) => {
                        chk_weight(x[0].value, x[1].value, y)
                    })
                    // возвращаемв се кнопки на форму
                    addrowdd.classList.remove("new-hide");
                    if (closeBtn.length) closeBtn[0].style.cssText = 'display:;'
                    break;
                case '2':
                    if (answers.length < 2) hint = '<p>Рекомендуем добавить несколько вариантов ответа для "вопроса с несколькими правильными ответами"</p>'
                    found_correct = false
                    for (let [index, row] of answers.entries()) {
                        let { ans_type, ans_weight } = get_row_data(row)
                            if (ans_type.value == 1 & ans_weight.value >= 0) hint += '<p>Рекомендуем поставить небольшой минус в баллах за неверный ответ ' + ( index + 1 ) + ', т.к. если этого не сделать, то можно отметить все ответы</p>'
                            if (ans_type.value == 2) found_correct = true
                            chk_weight(ans_type.value, ans_weight.value, index)
                    }    
                    if (!found_correct) {
                        saveBtn.disabled = true
                        hint += '<p style="color:red;">Необходимо выбрать хоть один верный ответ</p>'
                    }
                    // возвращаем все конопки на форму
                    addrowdd.classList.remove("new-hide");
                    if (closeBtn.length) closeBtn[0].style.cssText = 'display:;'           
            }
        // добавляем текст подсказки
        tip_field.innerHTML = hint
        }
    }

hinter(null)
questSelect.addEventListener('change', hinter)
// добавляем листенеры ко всем элементам, изменение которых должно влиять на подсказки или форму
addrowdd.addEventListener('click', function(event) {
    hinter(event)
    document.querySelectorAll('table > tbody > tr > td > select').forEach(x => x.addEventListener('change', hinter))
    document.querySelectorAll('table > tbody > tr > td > input').forEach(x => {
        if (x.name.endsWith('weight')) x.addEventListener('change', hinter)
    })    
})
// questSelect.addEventListener('change', hinter)
document.querySelectorAll('table > tbody > tr > td > select').forEach(x => x.addEventListener('change', hinter))
document.querySelectorAll('table > tbody > tr > td > input').forEach(x => {
    if (x.name.endsWith('weight')) x.addEventListener('change', hinter)
})
}