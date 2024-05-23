import oss2
from magic_doc.restful_api.common.ext import singleton_func
from loguru import logger


@singleton_func
class Oss(object):
    def __init__(self, access_key_id, access_secret_key, bucket_name, endpoint, expires=60):
        self.access_key_id = access_key_id
        self.access_secret_key = access_secret_key
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.expires = expires
        self.auth = oss2.Auth(self.access_key_id, self.access_secret_key)

    def create_bucket(self, bucket_name=None):
        """
        创建存储空间
        :param bucket_name:  bucket名称
        :return:
        """
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name if bucket_name else self.bucket_name)
        # 设置存储空间为私有读写权限
        # bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)
        bucket.create_bucket()
        return True

    def delete_bucket(self, bucket_name=None):
        """
        删除存储空间
        :param bucket_name:  bucket名称
        :return:
        """
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name if bucket_name else self.bucket_name)
        try:
            bucket.delete_bucket()
            return True
        except oss2.exceptions.BucketNotEmpty:
            logger.error('bucket is not empty.')
            return False
        except oss2.exceptions.NoSuchBucket:
            logger.error('bucket does not exist')
            return False

    def pub_object(self, bucket_name=None, object_name=None, object_data=None):
        """
        上传文件
            Str
            Bytes
            Unicode
            Stream
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :param object_data:
        :return:
        """
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name if bucket_name else self.bucket_name)
        result = bucket.put_object(object_name, object_data)
        file_link = bucket.sign_url('GET', object_name, self.expires, slash_safe=True)
        return {
            "status": result.status,
            "request_id": result.request_id,
            "etag": result.etag,
            "date": result.headers['date'],
            "file_link": file_link
        }

    def put_file(self, bucket_name=None, object_name=None, file_path=None):
        """
        上传文件
            file
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :param file_path:   文件路径
        :return:
        """
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name if bucket_name else self.bucket_name)
        result = bucket.put_object_from_file(object_name, file_path)
        file_link = bucket.sign_url('GET', object_name, self.expires, slash_safe=True)
        return {
            "status": result.status,
            "request_id": result.request_id,
            "etag": result.etag,
            "date": result.headers['date'],
            "file_link": file_link
        }

    def delete_objects(self, bucket_name=None, object_name=None):
        """
        批量删除文件
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径列表
        :return:
        """
        if object_name is None:
            object_name = []
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name if bucket_name else self.bucket_name)
        result = bucket.batch_delete_objects(object_name)
        return result.deleted_keys

    def download_file(self, bucket_name=None, object_name=None, save_path=None):
        """
        下载文件到本地
        :param bucket_name:  bucket名称
        :param object_name:  不包含Bucket名称组成的Object完整路径
        :param save_path:  保存路径
        :return:
        """
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name if bucket_name else self.bucket_name)
        bucket.get_object_to_file(object_name, save_path)
