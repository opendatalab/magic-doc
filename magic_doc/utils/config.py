


class Config:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # origin = super(Singleton, cls)
            # cls._instance = origin.__new__(cls, *args, **kwargs)
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def load_config(self, path: str):
        if not hasattr(self, "_loaded"):
            self._loaded = True
            # load some config !
        else:
            pass
    
    def get_bucket_info(self):
        return {"ak": "test", "sk": "txxx", "endpoint": "xxxx"}
    
    def get_layout_model_config(self):
        return {} 
    

    def get_latex_model_config(self):
        return {}
    



