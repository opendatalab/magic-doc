

from magic_doc.progress.pupdator import ConvProgressUpdator


class FileBaseProgressUpdator(ConvProgressUpdator):
    def __init__(self, progress_file_path:str):
        self.__progress_file_path = progress_file_path
    
    def do_update(self, progress:int) -> bool:
        with open(self.__progress_file_path, 'w', encoding='utf-8') as fout:
            fout.write(str(int(progress)))

        return True