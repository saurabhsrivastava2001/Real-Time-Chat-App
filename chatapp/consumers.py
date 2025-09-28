from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name= self.scope['url_route']['kwargs']['room_name']
        self.room_group_name= 'chat_%s' % self.room_name


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    #disconnect
    
    async def disconnect(self):
        await self.channel_layer.group_discard(
            self.channel_layer,
            self.room_group_name
        )

    async def receive(self, text_data):
        data= json.loads(text_data)
        message= data['message']
        username= data['username']
        room= data['room']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message': message,
                'username': username,
                'room': room
            }
        )
        await self.save_message(username, room, message)
    async def chat_message(self, event):
        message= event['message']
        username= event['username']
        room= event['room']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'room': room
        }))

    
    # funciton to save message to database
    @sync_to_async
    def save_message(self, username, room, message):
        from .models import ChatMessage, ChatRoom
        from django.contrib.auth.models import User

        user= User.objects.get(username=username)
        room= ChatRoom.objects.get(slug=room)

        ChatMessage.objects.create(user=user, room=room, message=message)