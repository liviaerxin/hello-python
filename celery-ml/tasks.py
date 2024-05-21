from celery import Celery, Task, signals
import time


class CeleryConfig:
    broker_url = "redis://localhost:6379/0"
    result_backend = "redis://localhost:6379/0"


app = Celery("tasks")
app.config_from_object(CeleryConfig)

class SpamModel:
    """ Wrapper for loading and serving pre-trained model"""

    def __init__(self):
        MODEL_PATH = "./ml/spam_classifier.joblib"
        self.model = self._load_model_from_path(MODEL_PATH)

    @staticmethod
    def _load_model_from_path(path):
        import joblib    
        model = joblib.load(path)
        return model

    @staticmethod
    def preprocessor(text):
        import re
        text = re.sub('<[^>]*>', '', text) # Effectively removes HTML markup tags
        emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
        text = re.sub('[\W]+', ' ', text.lower()) + ' '.join(emoticons).replace('-', '')
        return text

    def predict(self, message):
        """
        Make batch prediction on list of preprocessed feature dicts.
        Returns class probabilities if 'return_options' is 'Prob', otherwise returns class membership predictions
        """
        message = self.preprocessor(message)
        label = self.model.predict([message])[0]
        spam_prob = self.model.predict_proba([message])
        
        return {'label': label, 'spam_probability': spam_prob[0][1]}
    
class PredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.
    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None
        print("PredictTask initialized")

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            print('Loading Model...')
            # module_import = importlib.import_module(self.path[0])
            # model_obj = getattr(module_import, self.path[1])
            # self.model = model_obj()
            self.model = SpamModel()
            print('Model loaded')
        return self.run(*args, **kwargs)


@app.task(ignore_result=False,
          bind=True,
          base=PredictTask,
        #   path=('celery_task_app.ml.model', 'ChurnModel'),
          name='{}.{}'.format(__name__, 'SpamDetect'))
def detect_spam(self, msg: str):
    """
    Essentially the run method of PredictTask
    """
    result = self.model.predict(msg)
    return result