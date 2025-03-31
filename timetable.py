import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock

Builder.load_string('''
<LessonButton>:
    size_hint_y: None
    height: dp(40)
    canvas.before:
        Color:
            rgba: (1, 0.5, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.description
        text_size: self.width, None
        halign: 'center'
        valign: 'middle'
        size: self.texture_size
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

<TimetableScreen>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)

    Label:
        text: 'Plan Studenta'
        font_size: dp(24)
        bold: True
        size_hint_y: None
        height: dp(40)

    GridLayout:
        cols: 6
        size_hint_y: None
        height: dp(25)
        spacing: dp(2)
        
        Label:
            text: 'Hours'
            bold: True

        Label:
            text: 'poniedziałek'
            bold: True
        Label:
            text: 'wtorek'
            bold: True
        Label:
            text: 'środa'
            bold: True
        Label:
            text: 'czwartek'
            bold: True
        Label:
            text: 'piątek'
            bold: True

    ScrollView:
        GridLayout:
            id: timetable_grid
            cols: 6
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(2)
            padding: dp(2)
''')


class LessonButton(BoxLayout):
    description = StringProperty('')
    info = StringProperty('')
    even = ObjectProperty(False)


class TimetableScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.populate_timetable, 0.1)

    def populate_timetable(self, dt):
        grid = self.ids.timetable_grid
        grid.clear_widgets()

        # Time slots from 06:00 to 21:00
        times = [f"{hour:02d}:00" for hour in range(6, 22)]

        # Load lessons from JSON
        with open('lessons.json', 'r', encoding='utf-8') as f:
            lessons = json.load(f)

        # Create day columns (5 days - Monday to Friday)
        days = {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": []
        }

        # Organize lessons by day of week
        for lesson in lessons:
            day = lesson['info']['dayOfWeek']
            if day in days:
                days[day].append(lesson)

        # Create timetable grid
        for time_slot in times:
            # Time label
            grid.add_widget(Label(text=time_slot, size_hint_y=None, height=dp(40)))

            # Lessons for each day
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                found = False
                for lesson in days[day]:
                    # Compare just the hour part (HH:00 vs HH:MM)
                    if lesson['info']['startTime'].split(':')[0] == time_slot.split(':')[0]:
                        btn = LessonButton(
                            description=lesson['description'],
                            info=lesson['raw_info'],  # Using raw_info for tooltip if needed
                            even=(int(time_slot.split(':')[0]) % 2 == 0)
                        )
                        grid.add_widget(btn)
                        found = True
                        break

                if not found:
                    grid.add_widget(Label(text='', size_hint_y=None, height=dp(40)))


class TimetableApp(App):
    def build(self):
        return TimetableScreen()


if __name__ == '__main__':
    TimetableApp().run()