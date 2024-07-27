## Cronjob Action

```
* * * * * cd /home/user/scraping_odoo && /usr/bin/python3 /home/user/scraping_odoo/cron.py >> /home/user/scraping_odoo/cron.log 2>&1
```

## Cronjob Login

```
0 13 * * * cd /home/user/scraping_odoo && /usr/bin/python3 /home/user/scraping_odoo/login.py >> /home/user/scraping_odoo/login.log 2>&1
```

## Library

| Library        | How To Install             |
| -------------- | -------------------------- |
| requests       | pip install requests       |
| BeautifulSoup4 | pip install BeautifulSoup4 |
| bs4            | pip install bs4            |
| python-dotenv  | pip install python-dotenv  |
