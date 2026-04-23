Модуль Micropython для работы с ENS160.
ENS160 — это цифровой мультигазовый датчик, специально разработанный для мониторинга качества воздуха в помещении, обеспечивающий оптимальное обнаружение широкого спектра летучих органических соединений (ЛОС) и окисляющих газов.

Загрузите прошивку Micropython на плату NANO (ESP и т. д.), файлы *.py: main.py, ens160sciosense.py и папку service_pack_2.
Затем откройте main.py в вашей IDE и запустите его.

## Важное правило: первые 24 часа работы

Если вы видите надпись Initial Start-Up и ждете, пока датчик начнет показывать данные, прочтите этот раздел.

Как работает датчик при первом включении:
1. Внутри чипа есть память NVM, где хранится информация о чистом воздухе.
2. При самой первой установке датчик пуст. Ему нужно понять, какой воздух вокруг него сейчас.
3. Для этого он работает ровно 24 часа без выключения. В это время он калибруется и запоминает параметры.
4. Если выключить питание раньше, чем пройдут 24 часа, датчик забудет все и начнет калибровку заново.
5. После успешных 24 часов информация сохраняется навсегда. При следующих включениях датчик будет запускаться за 3 минуты, а не за час.

Что нужно сделать вам:
- Включите датчик и оставьте его работать непрерывно сутки.
- Не вынимайте кабель, не отключайте питание, не перезагружайте плату.
- Можете закрыть окно терминала. Датчик будет работать сам.
- Через 24 часа он запомнит чистый воздух и будет готов к работе сразу после включения.

Почему так сделано:
Это не ошибка программы. Все газовые датчики такого типа работают именно так. Им нужно время, чтобы прогреться, стабилизировать внутренние элементы и записать базовые значения в энергонезависимую память.

Коротко:
- Первые 24 часа = датчик учится. Не трогайте его.
- После 24 часов = датчик запомнил. Будет включаться быстро.
- Если выключить раньше 24 часов = начнет учиться заново (снова 1 час ожидания).

# Картинки
## IDE
![alt text](https://github.com/octaprog7/ens160/blob/master/ide_ens160.png)
## Макетная плата
![alt text](https://github.com/octaprog7/ens160/blob/master/brd_ens160.png)
## График CO2 и TVOC
![alt text](https://github.com/octaprog7/ens160/blob/master/co2_graph.png)

## Время первичной калибровки (Initial Start-Up)

При первом включении датчика ENS160 (или после хранения без питания более 24 часов) вы увидите в выводе:
```console
[1] Initial Start-Up (~1 hour) | Validity: 2 | NewData: True
[2] Initial Start-Up (~1 hour) | Validity: 2 | NewData: True
```

Это нормальное поведение, а не ошибка!

### Хронология запуска:

| Время от старта | Validity Flag | Статус           | Что происходит                                                                                              |
|-----------------|---------------|------------------|-------------------------------------------------------------------------------------------------------------|
| 00:00 - ~60:00  | 2             | Initial Start-Up | Первичная калибровка 4 нагревателей, стабилизация MOX-элементов, формирование базовой линии чистого воздуха |
| ~60:00 - ~63:00 | 1             | Warm-Up          | Финальный прогрев, алгоритм TrueVOC выходит на рабочий режим                                                |
| > ~63:00        | 0             | Operating OK     | Стабильные показания eCO2 [ppm], TVOC [ppb], AQI                                                            |

### Важно:

1. Не отключайте питание в течение первых 24 часов непрерывной работы.
   После этого базовая линия сохранится во внутренней NVM-памяти чипа, и при последующих включениях фаза Initial Start-Up больше не повторится (только Warm-Up ~3 мин).

2. Данные в фазе Validity: 2 невалидны -> драйвер корректно возвращает None и не выводит нулевые показания.

3. Это особенность всех MOX-сенсоров (металлооксидных полупроводниковых), а не ошибка драйвера. Физический процесс прогрева и стабилизации нагревателей требует времени.

### Рекомендации:

- В готовых устройствах не обесточивайте ENS160 полностью. Используйте режим DEEP_SLEEP (потребление ~10 uA) вместо отключения VDD.
- Если питание всё же снимается, информируйте пользователя: "Sensor calibration... ~1 hour" вместо показа нулей.
- Для тестов можно временно игнорировать validity_flag, но точность показаний будет низкой.

### Пример вывода после калибровки:

```console
[3601] Warm-Up (~3 min) | Validity: 1 | NewData: True
[3602] Warm-Up (~3 min) | Validity: 1 | NewData: True
...
[3781] Operating OK | eCO2: 485 ppm | TVOC: 62 ppb | AQI: 1
[3782] Operating OK | eCO2: 492 ppm | TVOC: 68 ppb | AQI: 2
```

Просто оставьте плату включённой на ~1.5 часа — и датчик начнёт отдавать точные данные о качестве воздуха!

## Качество воздуха и приготовление пищи
### На кухне ничего не готовят
```console
[3962] Operating OK | eCO2: 465 ppm | TVOC: 54 ppb | AQI: 1
[3963] Operating OK | eCO2: 457 ppm | TVOC: 50 ppb | AQI: 1
[3964] Operating OK | eCO2: 494 ppm | TVOC: 69 ppb | AQI: 2
[3965] Operating OK | eCO2: 446 ppm | TVOC: 45 ppb | AQI: 1
[3966] Operating OK | eCO2: 473 ppm | TVOC: 58 ppb | AQI: 1
[3967] Operating OK | eCO2: 493 ppm | TVOC: 69 ppb | AQI: 2
[3968] Operating OK | eCO2: 480 ppm | TVOC: 62 ppb | AQI: 1
[3969] Operating OK | eCO2: 455 ppm | TVOC: 49 ppb | AQI: 1
[3970] Operating OK | eCO2: 489 ppm | TVOC: 66 ppb | AQI: 2
[3971] Operating OK | eCO2: 461 ppm | TVOC: 52 ppb | AQI: 1
[3972] Operating OK | Validity: 0 | NewData: False
[3973] Operating OK | eCO2: 478 ppm | TVOC: 61 ppb | AQI: 1
[3974] Operating OK | eCO2: 470 ppm | TVOC: 57 ppb | AQI: 1
[3975] Operating OK | eCO2: 480 ppm | TVOC: 61 ppb | AQI: 1
[3976] Operating OK | eCO2: 488 ppm | TVOC: 66 ppb | AQI: 2
[3977] Operating OK | eCO2: 459 ppm | TVOC: 51 ppb | AQI: 1
[3978] Operating OK | eCO2: 452 ppm | TVOC: 48 ppb | AQI: 1
[3979] Operating OK | eCO2: 462 ppm | TVOC: 52 ppb | AQI: 1
[3980] Operating OK | eCO2: 467 ppm | TVOC: 55 ppb | AQI: 1
[3981] Operating OK | eCO2: 470 ppm | TVOC: 57 ppb | AQI: 1
[3982] Operating OK | eCO2: 470 ppm | TVOC: 57 ppb | AQI: 1
[3983] Operating OK | eCO2: 451 ppm | TVOC: 47 ppb | AQI: 1
[3984] Operating OK | eCO2: 444 ppm | TVOC: 44 ppb | AQI: 1
[3985] Operating OK | eCO2: 450 ppm | TVOC: 47 ppb | AQI: 1
[3986] Operating OK | eCO2: 467 ppm | TVOC: 55 ppb | AQI: 1
[3987] Operating OK | eCO2: 468 ppm | TVOC: 55 ppb | AQI: 1
[3988] Operating OK | eCO2: 452 ppm | TVOC: 48 ppb | AQI: 1
[3989] Operating OK | eCO2: 444 ppm | TVOC: 44 ppb | AQI: 1
[3990] Operating OK | eCO2: 479 ppm | TVOC: 61 ppb | AQI: 1
[3991] Operating OK | eCO2: 436 ppm | TVOC: 40 ppb | AQI: 1
...
```
### На кухне, на газу жарят мясо!!!
```console
[7766] Operating OK | eCO2: 700 ppm | TVOC: 205 ppb | AQI: 2
[7767] Operating OK | eCO2: 694 ppm | TVOC: 201 ppb | AQI: 2
[7768] Operating OK | eCO2: 744 ppm | TVOC: 243 ppb | AQI: 3
[7769] Operating OK | eCO2: 704 ppm | TVOC: 209 ppb | AQI: 2
[7770] Operating OK | eCO2: 678 ppm | TVOC: 188 ppb | AQI: 2
[7771] Operating OK | eCO2: 706 ppm | TVOC: 210 ppb | AQI: 2
[7772] Operating OK | eCO2: 729 ppm | TVOC: 230 ppb | AQI: 3
[7773] Operating OK | eCO2: 707 ppm | TVOC: 212 ppb | AQI: 2
[7774] Operating OK | eCO2: 722 ppm | TVOC: 224 ppb | AQI: 3
[7775] Operating OK | eCO2: 721 ppm | TVOC: 223 ppb | AQI: 3
[7776] Operating OK | eCO2: 736 ppm | TVOC: 236 ppb | AQI: 3
[7777] Operating OK | eCO2: 710 ppm | TVOC: 214 ppb | AQI: 2
[7778] Operating OK | Validity: 0 | NewData: False
[7779] Operating OK | eCO2: 724 ppm | TVOC: 226 ppb | AQI: 3
[7780] Operating OK | eCO2: 708 ppm | TVOC: 212 ppb | AQI: 2
[7781] Operating OK | eCO2: 746 ppm | TVOC: 245 ppb | AQI: 3
[7782] Operating OK | eCO2: 722 ppm | TVOC: 224 ppb | AQI: 3
[7783] Operating OK | eCO2: 727 ppm | TVOC: 229 ppb | AQI: 3
[7784] Operating OK | eCO2: 735 ppm | TVOC: 235 ppb | AQI: 3
[7785] Operating OK | eCO2: 733 ppm | TVOC: 234 ppb | AQI: 3
```