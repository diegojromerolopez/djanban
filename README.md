
# Django Trello stats

Statistics and charts for Trello boards, now in a Django app.

# Sign up

First you need to sign up with the api key, token and token secret.

This action will create a new user in the system.

User your email to log in the application.

# Initialize boards and lists

Later, you need to initialize the boards.

```python
python src/manage.py init <trello_username>
```

# Fetch cards

And of course, you have to fetch the cards.

```python
python src/manage.py fetch <trello_username>
```

One good idea is set this action in a cron action and call it each day.

# Description of computed stats

- Card spent and estimated times.
- Daily spent and estimated times.
- Average time cards are in each list.
- Spent time by member by week. 

# TODO
  - Workflow stats


# Questions? Suggestions?

Don't hesitate to contact me, write me to diegojREMOVETHISromeroREMOVETHISlopez@REMOVETHISgmail.REMOVETHIScom.

(remove REMOVETHIS to see the real email address)