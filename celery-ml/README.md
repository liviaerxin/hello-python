# A celery worker with integrating ML model efficiently and briefly

## Getting start

1. Training a trial ML model

```sh
python3 ml/train_spam_detector.py
```

1. Starting **redis** as **Celery** broker and backend

```sh
redis-server --bind 0.0.0.0
```

3. Serving the ML model through running a **Celery** worker server

```sh
celery -A tasks worker -l INFO
```

4. Calling the ML task

```sh
>>> from tasks import detect_spam
>>> detect_spam("Congratulations! You've won a $1000 gift card. Click here to claim now!")
PredictTask initialized
Loading Model...
Model loaded
{'label': np.str_('spam'), 'spam_probability': np.float64(0.9996196581727181)}
>>> detect_spam("Hey, are we still on for dinner tomorrow night?")
{'label': np.str_('ham'), 'spam_probability': np.float64(1.0643811378210551e-08)}
>>> 
>>> detect_spam("Make $$$ working just 1 hour per day! Click to learn how.")
{'label': np.str_('ham'), 'spam_probability': np.float64(2.1231341266699193e-07)}
```

As it shows, the following calls are free from the model loading but the first invocation loads the model which still cost time. To prepare the model even before the first trigger, we need to warm up!