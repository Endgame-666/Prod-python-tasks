## Url Shortener


### Предисловие

К огромному сожалению большого числа пользователей компания Google [закрыла свой сервис для сокращения ссылок goo.gl](https://wersm.com/google-has-shut-down-its-goo-gl-url-shortening-service/).
Теперь каждый раз приходится, как ни парадоксально, гуглить ссылочку для сокращения ссылочек.  
В этом задании мы предлагаем вам написать свой небольшой веб-сервис для этого дела.

### Само условие

Необходимо реализовать api для сокращения ссылок по описанию ниже.
Для реализации необходимо использовать библиотеку [fastapi](https://github.com/tiangolo/fastapi) ([документация](https://fastapi.tiangolo.com/tutorial/)).

**NB:** fastapi автоматически генерирует документацию к вашему api.  
В этой задаче ВАЖНО соответствовать схеме (см. тесты) и описывать свои модели соответственно.  
**NB2:** Внимательно смотрите спецификацию openapi из тестов. Тесты будут проверять названия всех методов вплоть до совпадения имён классов, функций и их сигнатур  
**NB3:** Не забудьте прописать в декораторах параметр `status_code`!


#### 1. Метод для создания ссылки
Url метода: `/shorten`
HTTP method: POST.  
Body: `{"url": "<URL>"}`  
Response: 201, `{"url": "<URL>", "key": "<KEY>"}`  

Метод для создания сокращенной ссылки. При успешном выполнении возвращается json с сокращённым ключом. Для невалидного ввода возвращается код ошибки 422.  


#### 2. Метод для перехода по ссылке
Url метода: `/go/<KEY>`  
HTTP method: GET  
Response: 307  

Для существующего ключа сервис должен возвращать код 307 и перенаправлять по полной ссылке. Для несуществующего ключа сервис должен вернуть код ошибки 404.


### Состояние
Для упрощения задачи своё состояние сервис должен целиком хранить в памяти.


### Пример

Пользователь отправляет запрос `POST` на url `/shorten` с телом запроса 
```
{"url": "https://www.python.org/dev/peps/pep-0008"}
```

Сервер должен ответить json'ом следующего вида: 
```
{
  "url": "https://www.python.org/dev/peps/pep-0008",
  "key": "ed1De1"
}
```
`ed1De1` здесь - это сгенерированное сервисом число (удобно будет генерировать через uuid).

При дальнейшем запросе на url `/go/ed1De1` сервис должен перенаправить пользователя на сайт `https://www.python.org/dev/peps/pep-0008` 