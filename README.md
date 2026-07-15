# YTTV Project (OBS)

## RU
YTTV Project - проект, созданный для простого запуска своего телеканала, транслируемого на стриминговых платформах при помощи [OBS Studio](https://github.com/obsproject/obs-studio)

## EN
YTTV Project - a project designed for easy launching of your own TV channel, broadcast on streaming platforms using [OBS Studio](https://github.com/obsproject/obs-studio)

---

## Зависимости / Dependencies

### RU:
- Python (желательно 4, на нем запускался проект)
- OBS Studio
- os
- time
- obsws_python
- subprocess
- json
- datetime
- random

### EN:
- Python (preferably 4, the project was tested on it)
- OBS Studio
- os
- time
- obsws_python
- subprocess
- json
- datetime
- random

---

## Использование / Usage

### RU:
Перед началом убедитесь что на выбранной сцене в OBS есть:
1. Источник Media/Мультимедия с названием "Logo" *(ЛОГОТИП)*
2. Источник Media/Мультимедия с названием "Media" *(ВИДЕОПОТОК)*

(Необязательно) Привяжите ваш OBS к сервису для стриминга через Файл/Настройки/Трансляция/Служба

Включите WebSocket для OBS. С помощью него OBS может привязаться к скрипту и управлять телеканалом.
Сервис/Настройка севрера WebSocket
Пометьте галочку "Включить сервер WebSocket"
Нажмите на "Показать сведения о подключении" и на "Скопировать" возле поля ввода пароля. Так вы сможете скопировать пароль от вебсокета OBS
Поздравляю, OBS настроен!

Теперь, вам нужно настроить сам скрипт.
Зайдите в main.py из любого UTF-8 редактора и измените значение переменной PASSWORD на то, что вы скопировали (ПАРОЛЬ ДОЛЖЕН БЫТЬ ОБЯЗАТЕЛЬНО В КОВЫЧКАХ, НАПРИМЕР PASSWORD = "JIJDSOFDSJFOKDSP")
Скрипт настроен, теперь нужно настроить передачи!
Перенесите все телепрограммы в папку vid (если плейлист - vid/название папки)
Укажите все эти программы в videos.json, укажите до них путь, название, обложку и другие параметры (ОБЯЗАТЕЛЬНО: ПУТЬ, НАЗВАНИЕ, ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ)
Закиньте как минимум один логотип формата .png в папку logos, он будет показываться на телеканале 
Все программы настроены

(ОПЦИОНАЛЬНО) Настройка бамперов, перерывов, заставок и других подобных вещей

Закиньте по папкам видеофайлы (тут указаны названия папок, в видеофайлах названия необязательны):
 - bumper - Заставки между программами
 - covers - Обложки для Telegram бота
 - intro - Видео подгрузки видеофайлов
 - placeholder - Скоро в эфире (заглушка)
 - promo - Реклама

(ОПЦИОНАЛЬНО) Настройка Telegram бота

Для использования обязательно нужен любой MTPROTO прокси, автор данного проекта из РФ поэтому я выбрал локальный прокси
Что бы настроить бота, вам нужно получить ваш HASH, ID и TOKEN бота
HASH и ID можно получить на my.telegram.org
 - Войдите в аккаунт
 - Нажмите на API Development Tools (если у вас нету проекта создайте его)
 - Найдите app_hash и app_id - это ваши данные, держите их в секрете
 - Укажите app_hash в переменной API_HASH
 - Укажите app_id в переменной API_ID
Что бы создать бота и получить токен:
 - Зайдите в бота [BotFather](t.me/BotFather)
 - Введите /newbot
 - Настройте вашего бота как вам захочется
 - Потом в сообщении вам выдадут токен, укажите его в переменной BOT_TOKEN

Бот настроен! Запустите его через `python telegrambot.py` и проверьте работоспособность через юзернейм бота

Готово, ваш телеканал готов к вещанию!

---

### EN:
Before starting, make sure that on the selected scene in OBS there are:
1. Media Source named "Logo" *(LOGO)*
2. Media Source named "Media" *(VIDEO STREAM)*

(Optional) Connect your OBS to a streaming service via File/Settings/Stream/Service

Enable WebSocket for OBS. This allows OBS to connect to the script and control the TV channel.
Tools/WebSocket Server Settings
Check the "Enable WebSocket server" box
Click "Show connection info" and "Copy" next to the password field. This will copy your OBS WebSocket password
Congratulations, OBS is configured!

Now you need to configure the script itself.
Open main.py in any UTF-8 editor and change the PASSWORD variable value to what you copied (THE PASSWORD MUST BE IN QUOTES, FOR EXAMPLE PASSWORD = "JIJDSOFDSJFOKDSP")
The script is configured, now you need to set up the programs!
Move all TV programs to the vid folder (if playlist - vid/folder_name)
Specify all these programs in videos.json, specifying the path, name, cover and other parameters (REQUIRED: PATH, NAME, AGE RESTRICTION)
Upload at least one .png logo to the logos folder, it will be displayed on the TV channel
All programs are configured

(OPTIONAL) Setting up bumpers, breaks, screensavers and other similar things

Upload video files to folders (folder names are listed here, file names are optional):
 - bumper - Screensavers between programs
 - covers - Covers for Telegram bot
 - intro - Video loading screens
 - placeholder - Coming soon (standby screen)
 - promo - Advertising

(OPTIONAL) Telegram bot setup

To use it, you need any MTPROTO proxy. The author of this project is from Russia, so I chose a local proxy
To set up the bot, you need to get your HASH, ID and BOT TOKEN
HASH and ID can be obtained at my.telegram.org
 - Log in to your account
 - Click on API Development Tools (if you don't have a project, create one)
 - Find app_hash and app_id - these are your data, keep them secret
 - Set app_hash in the API_HASH variable
 - Set app_id in the API_ID variable
To create a bot and get a token:
 - Go to [BotFather](t.me/BotFather)
 - Enter /newbot
 - Configure your bot as you like
 - Then you will receive a token in the message, set it in the BOT_TOKEN variable

The bot is configured! Run it with `python telegrambot.py` and check its functionality via the bot username

Done, your TV channel is ready to broadcast!

---