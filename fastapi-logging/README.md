# FastAPI Logging in Uvicorn

The key is turing the logging configuration in `Uvicorn`.

When running `FastAPI` app, all the logs in console are from `Uvicorn` and they do not have timestamp and other useful information. As `Uvicorn` applies python `logging` module, we can override `Uvicorn` logging formatter by applying a new logging configuration.

Meanwhile, it's able to unify the your endpoints logging with the `Uvicorn` logging by configuring all of them in the config file `log_conf.yaml`.

Before overriding:

```sh
uvicorn main:app --reload
```

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [34318] using StatReload
INFO:     Started server process [34320]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:50062 - "GET / HTTP/1.1" 200 OK
```


After applying `log_conf.yaml`:

```sh
uvicorn main:app --reload --log-config=log_conf.yaml
```

```sh
2023-03-08 15:40:41,170 - uvicorn.error - INFO - Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
2023-03-08 15:40:41,170 - uvicorn.error - INFO - Started reloader process [34322] using StatReload
2023-03-08 15:40:41,297 - asyncio - DEBUG - Using selector: EpollSelector
2023-03-08 15:40:41,432 - uvicorn.error - INFO - Started server process [34324]
2023-03-08 15:40:41,432 - uvicorn.error - INFO - Waiting for application startup.
2023-03-08 15:40:41,432 - uvicorn.error - INFO - Application startup complete.
2023-03-08 15:48:21,450 - main - INFO - request / endpoint!
2023-03-08 15:48:21,450 - uvicorn.access - INFO - 127.0.0.1:59782 - "GET / HTTP/1.1" 200
```

```sh
uvicorn main:app --reload --log-config=log_conf.yaml --log-level error
```


Or use your own logging configuration without using `--log-config`.

```sh
uvicorn app1:app --reload
```

[logs with FastAPI and Uvicorn · tiangolo/fastapi · Discussion #7457 · GitHub](https://github.com/tiangolo/fastapi/discussions/7457)

[Python Comprehensive Logging using YAML Configuration · GitHub](https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19)

[Settings - Uvicorn](https://www.uvicorn.org/settings/#logging)