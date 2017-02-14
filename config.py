import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SMS_PROVIDER_USERNAME = os.environ.get('SMS_PROVIDER_USERNAME')
    SMS_PROVIDER_KEY = os.environ.get('SMS_PROVIDER_KEY')
    DOCTORS_SEARCH_URL = os.environ.get('DOCTORS_SEARCH_URL')
    NURSE_SEARCH_URL = os.environ.get('NURSE_SEARCH_URL')
    CO_SEARCH_URL = os.environ.get('CO_SEARCH_URL')
    NHIF_SEARCH_URL = os.environ.get('NHIF_SEARCH_URL')
    HF_SEARCH_URL = os.environ.get('HF_SEARCH_URL')
    SMS_RESULT_COUNT = 5 # Number of results to be send via sms
    DOC_KEYWORDS = ['doc', 'daktari', 'doctor', 'oncologist', 'dr']
    CO_KEYWORDS = ['CO', 'clinical officer','clinic officer']
    NO_KEYWORDS = ['nurse', 'no', 'nursing officer', 'mhuguzi', 'RN', 'Registered Nurse'] # Nurses Keywords
    NHIF_KEYWORDS = ['nhif', 'bima', 'insurance', 'insurance fund', 'health insurance', 'hospital fund'] # Nurses Keywords
    HF_KEYWORDS = ['hf', 'hospital', 'dispensary', 'clinic', 'hospitali', 'sanatorium', 'health centre'] # Nurses Keywords


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SEND_SMS = False
    APP_CONFIG = 'development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or  'sqlite:///' + os.path.join(basedir, 'starhealth-dev.sqlite')
    print "DATABASE:",SQLALCHEMY_DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or  'sqlite:///' + os.path.join(basedir, 'starhealth-test.sqlite')


class ProductionConfig(Config):
    SEND_SMS = True
    APP_CONFIG = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}