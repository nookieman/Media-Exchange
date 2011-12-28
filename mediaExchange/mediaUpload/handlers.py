from django.core.files.uploadhandler import FileUploadHandler, UploadFileException   

class ProgressUploadHandler(FileUploadHandler):
    """
    Store progress in the session
    """
    def __init__(self, *args, **kwargs):
        super(ProgressUploadHandler, self).__init__(*args, **kwargs)
        self.progress_id = None
        self.cache_key = None
        self.done_size = 0

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET :
            self.progress_id = self.request.GET['X-Progress-ID']
            self.cache_key = self.progress_id
            self.request.session['upload_progress_%s' % self.cache_key] =  {
                'length': self.content_length,
                'uploaded' : 0
            }


    def file_complete(self, filesize):
        pass

#    def new_file(self, field_name, file_name, content_type, content_length, charset):
#        pass

    def upload_complete(self):
        del self.request.session['upload_progress_%s' % self.cache_key]

    def receive_data_chunk(self, raw_data, start):
        data = self.request.session['upload_progress_%s' % self.cache_key]
        data['uploaded'] += len(raw_data)
        self.request.session['upload_progress_%s' % self.cache_key] = data
        self.request.session.save()
        return raw_data

