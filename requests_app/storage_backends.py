from storages.backends.gcloud import GoogleCloudStorage


class ChatImageStorage(GoogleCloudStorage):
    location = "chat-images"
    file_overwrite = False