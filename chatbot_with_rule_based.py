import sqlite3
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
import pytesseract
from PIL import Image as PILImage

def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def recover_password(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

create_user_table()

def chatbot_response(user_input):
    user_input = user_input.lower()

    if 'hello' in user_input or 'hi' in user_input:
        return "Hello! How can I help you today?"
    elif 'how are you' in user_input:
        return "I'm just a bot, but I'm here to help you!"
    elif 'bye' in user_input or 'goodbye' in user_input:
        return "Goodbye! Have a great day!"
    elif 'name' in user_input:
        return "I am Beso Chatbot, here to assist you."
    elif 'help' in user_input:
        return "Sure! How can I assist you today?"
    else:
        return answer_general_question(user_input)

def answer_general_question(question):
    try:
        response = requests.get(f"https://api.duckduckgo.com/?q={question}&format=json")
        answer = response.json().get("AbstractText", "I'm sorry, I don't know the answer to that.")
        return answer
    except:
        return "Sorry, I couldn't process that question."

class LoginRegisterScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginRegisterScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [50, 50, 50, 50]

        self.add_widget(Label(text="Welcome to Beso Chatbot", font_size=24, size_hint=(1, 0.2), halign='center', color=(1, 1, 0, 1)))

        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.2))
        self.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.2))
        self.add_widget(self.password_input)

        self.login_button = Button(text="Login", background_color=(0.2, 0.6, 0.8, 1), size_hint=(1, 0.2))
        self.login_button.bind(on_press=self.login)
        self.add_widget(self.login_button)

        self.register_button = Button(text="Register", background_color=(0.2, 0.8, 0.4, 1), size_hint=(1, 0.2))
        self.register_button.bind(on_press=self.register)
        self.add_widget(self.register_button)

        self.recover_button = Button(text="Recover Password", background_color=(0.8, 0.5, 0.2, 1), size_hint=(1, 0.2))
        self.recover_button.bind(on_press=self.recover_password)
        self.add_widget(self.recover_button)

    def login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if authenticate_user(username, password):
            App.get_running_app().show_chat_screen()
        else:
            self.show_popup("Login failed", "Invalid username or password")

    def register(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if add_user(username, password):
            self.show_popup("Registration successful", "You can now login with your credentials")
        else:
            self.show_popup("Registration failed", "Username already exists")

    def recover_password(self, instance):
        username = self.username_input.text
        password = recover_password(username)
        if password:
            self.show_popup("Password Recovery", f"Your password is: {password}")
        else:
            self.show_popup("Recovery failed", "Username not found")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

class ChatBotApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.login_screen = Screen(name='login')
        self.login_screen.add_widget(LoginRegisterScreen())
        self.chat_screen = Screen(name='chat')
        self.chat_screen.add_widget(self.create_chat_screen())

        self.screen_manager.add_widget(self.login_screen)
        self.screen_manager.add_widget(self.chat_screen)

        return self.screen_manager

    def create_chat_screen(self):
        chat_layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=10)
        
        with chat_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(size=chat_layout.size, pos=chat_layout.pos)
        
        chat_layout.bind(size=self._update_rect, pos=self._update_rect)

        scroll_view = ScrollView(size_hint=(1, 1), scroll_type=['bars'], bar_width=10)
        self.chat_history = Label(size_hint_y=None, height=400, width=400, text="Beso Chatbot: Hello! I am Beso Chatbot. Type 'bye' to exit.\n", valign='top', halign='left', markup=True)
        self.chat_history.bind(size=self.chat_history.setter('text_size'))

        scroll_view.add_widget(self.chat_history)
        chat_layout.add_widget(scroll_view)

        self.user_input = TextInput(multiline=False, size_hint_y=None, height=50)
        chat_layout.add_widget(self.user_input)

        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.submit_button = Button(text="Send", background_color=(0.2, 0.6, 0.8, 1))
        self.submit_button.bind(on_press=self.on_button_press)
        button_layout.add_widget(self.submit_button)

        self.clear_button = Button(text="Clear Chat", background_color=(0.8, 0.2, 0.2, 1))
        self.clear_button.bind(on_press=self.clear_chat)
        button_layout.add_widget(self.clear_button)

        self.logout_button = Button(text="Logout", background_color=(0.6, 0.4, 0.8, 1))
        self.logout_button.bind(on_press=self.logout)
        button_layout.add_widget(self.logout_button)

        # Add button for uploading files
        self.upload_button = Button(text="Upload Image/File", background_color=(0.8, 0.8, 0.2, 1))
        self.upload_button.bind(on_press=self.open_file_chooser)
        button_layout.add_widget(self.upload_button)

        # Add toggle for Dark Mode
        self.dark_mode_toggle = ToggleButton(text='Dark Mode', size_hint=(None, None), size=(100, 50), pos_hint={'center_x': .5, 'center_y': .5})
        self.dark_mode_toggle.bind(on_press=self.toggle_dark_mode)
        button_layout.add_widget(self.dark_mode_toggle)

        chat_layout.add_widget(button_layout)

        return chat_layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def show_chat_screen(self):
        self.screen_manager.current = 'chat'

    def on_button_press(self, instance):
        user_message = self.user_input.text
        if user_message.lower() == 'bye':
            self.update_chat_history("Goodbye! Have a great day!", bot_response=True)
            self.user_input.disabled = True
            self.submit_button.disabled = True
        else:
            response = chatbot_response(user_message)
            self.update_chat_history(f"[color=00FF00]You: {user_message}[/color]", bot_response=False)
            self.update_chat_history(f"[color=FF4500]Beso Chatbot: {response}[/color]", bot_response=True)
            self.user_input.text = ""

    def update_chat_history(self, message, bot_response):
        self.chat_history.text += message + "\n"
        self.chat_history.height += 20

    def clear_chat(self, instance):
        self.chat_history.text = "Beso Chatbot: Hello! I am Beso Chatbot. Type 'bye' to exit.\n"
        self.chat_history.height = 400

    def logout(self, instance):
        self.screen_manager.current = 'login'
        self.user_input.disabled = False
        self.submit_button.disabled = False
        self.clear_chat(None)

    def open_file_chooser(self, instance):
        content = FileChooserIconView()
        file_chooser_popup = Popup(title="Choose an Image or File", content=content, size_hint=(0.9, 0.9))
        content.bind(on_selection=lambda *x: self.process_selected_file(content.selection, file_chooser_popup))
        file_chooser_popup.open()

    def process_selected_file(self, selection, popup):
        if selection:
            file_path = selection[0]
            popup.dismiss()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                # Process image file
                text = pytesseract.image_to_string(PILImage.open(file_path))
                self.update_chat_history(f"[color=00FF00]You (from image): {text}[/color]", bot_response=False)
            elif file_path.lower().endswith(('.txt', '.pdf', '.docx')):
                # Process text file
                with open(file_path, 'r') as file:
                    text = file.read()
                self.update_chat_history(f"[color=00FF00]You (from file): {text}[/color]", bot_response=False)

    def toggle_dark_mode(self, instance):
        if instance.state == 'down':
            Window.clearcolor = (0, 0, 0, 1)  # Dark Mode
            self.rect.color = (1, 1, 1, 1)  # White background for chat box
        else:
            Window.clearcolor = (1, 1, 1, 1)  # Light Mode
            self.rect.color = (0, 0, 0, 1)  # Black background for chat box

if __name__ == "__main__":
    ChatBotApp().run()
