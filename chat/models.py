from django.db import models
from users.models import User

class ChatConversation(models.Model):
    """Chat conversations between customers and professionals"""
    conversation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_conversations')
    professional = models.ForeignKey(User, on_delete=models.CASCADE, related_name='professional_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'chat'
        db_table = 'chat_conversations'
    
    def __str__(self):
        return f"{self.customer} - {self.professional}"


class ChatMessage(models.Model):
    """Individual chat messages"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('location', 'Location'),
        ('document', 'Document'),
    ]
    
    message_id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    
    class Meta:
        app_label = 'chat'
        db_table = 'chat_messages'
    
    def __str__(self):
        return f"{self.sender} - {self.sent_at}"


class ChatMedia(models.Model):
    """Media files shared in chat messages"""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]
    
    chat_media_id = models.AutoField(primary_key=True)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file_name = models.CharField(max_length=200)
    file_uri = models.CharField(max_length=500)
    thumbnail_uri = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'chat'
        db_table = 'chat_media'
    
    def __str__(self):
        return f"{self.message} - {self.file_name}"