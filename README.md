
## Что это

Это приложение командной строки, которое использует [Open API Тинькофф Инвестиций][openapi]
для получения информации о вашем портфеле, чтобы вести точный учет.
Оно не предназначено и не совершает никаких сделок,
использует только методы API для чтения.


## Зачем это

Инвестируя какое-то время с помощью сервиса [Тинькофф Инвестиции][referral]
(реферальная ссылка) я задался вопросом, а насколько мои инвестиции эффективны.

На первый взгляд кажется, что узнать это довольно просто,
ведь в шапке приложения показывается стоимость моего текущего портфеля
и изменение его стоимости.

<img alt="tinkoff application header" src="./static/app_header.png" width="375"/>

Но у этого отображения есть огромное количество недостатков:

* Самое главное — не учитываются уже проданные бумаги
* Не учитывается разница в курсе на момент покупки бумаги
* Не учитываются купоны и дивиденды
* Не учитывается комиссия брокера и налоги

Поэтому я решил создать удобный инструмент для получения истории всех
операций в портфеле, что позволило вести учет всего вышеперечисленного
и наглядно видеть успехи инвестирования.


## Безопасность

При разработке приложения безопасность была поставлена во главу угла.
Open API Тинькофф Инвестиций на мой взгляд имеет ряд недостатков,
связанных с безопасностью:

* Токен передается в явном виде в заголовке запроса ([issue][open-token-issue])
* Нет разграничения прав токена, любой токен может быть использован
  для операций с вашим портфелем ([issue][restrict-token-issue])

Поэтому я считаю особенно важно не допускать компрометации токена.

По этой причине **ваш токен хранится только в зашифрованном виде**,
а для каждого запуска приложения нужно заново вводить пароль,
которым зашифрован токен. Это может показаться утомительным,
однако это позволяет полностью исключить доступ к вашим бумагам,
даже если злоумышленник получит полный доступ к вашему комьютеру.

Для шифровки токена используется [алгорит шифрования Salsa20][salsa20-resistance],
на текущий момент не имеющий доказанный уязвимостей,
а к паролю предъявляются строгие треботвания по входящим символам и длине.


## Установка

Приложение написано на языке [Python][python-wiki],
для его работы понадобится [интерпретатор не ниже версии 3.7][python-download].

```sh
$ git checkout https://github.com/homm/invest.git
$ cd invest
$ python3 -m venv env && source ./env/bin/activate
$ pip install -r requirements.txt
```


## Токен и первый запуск

При первом запуски приложение попросит вас придумать пароль,
которым будет зашифрован токен.

```sh
$ ./run.py
Seems like this is the first run. Please fill the credentials to continue.
At first, you need to choose a password.

Password should be at least 12 ASCII chars length.
It can't consist of digits only. At least one char in UPPER and lower case is required.
New password: 🔒
```

После ввода пароля приложение попросит вставить из буфера обмена токен.

```
New password: 
Repeat password: 

Now please paste the token once.
Do not store it anywhere else.

Paste token: 🔒
```

Токен — это ключ, необходимый для авторизации вас как пользователя Open API
Тинькофф Инвестиций. Это длинная последовательность почти случайных символов,
что исключает угадывание этого ключа другими пользователями.

Получить токен можно в [настройках аккаунта Тинькофф Инвестиций][invest-settings].
На данный момент этот блок выглядит так:

<img alt="tinkoff invest settings. Issue token" src="./static/issue-token.png" width="570"/>

Для сохранности токена рекомендуется закрыть страницу с настройками аккаунта
сразу после того, как вы скопируете токен в буфер обмена.
А после того как вы вставите токен из буфера обмена в приложение и нажмете энтер,
рекомендуется скопировать в буфер обмена любой другой текст,
чтобы потом случайно не вставить токен куда-то ещё.



Отозвать ранее выпущенный токен можно на [странице безопасности акканта][tinkoff-security] банка.
На данный момент этот блок выглядит так:

<img alt="tinkoff account settings. Release token" src="./static/release-token.png" width="686"/>


[openapi]: https://tinkoffcreditsystems.github.io/invest-openapi/
[referral]: https://www.tinkoff.ru/sl/4NJDEmwpqsn
[open-token-issue]: https://github.com/TinkoffCreditSystems/invest-openapi/issues/161
[restrict-token-issue]: https://github.com/TinkoffCreditSystems/invest-openapi/issues/12
[salsa20-resistance]: https://en.wikipedia.org/wiki/Salsa20#Cryptanalysis_of_Salsa20
[python-wiki]: https://ru.wikipedia.org/wiki/Python
[python-download]: https://www.python.org/downloads/
[invest-settings]: https://www.tinkoff.ru/invest/settings/
[tinkoff-security]: https://id.tinkoff.ru/account/security
