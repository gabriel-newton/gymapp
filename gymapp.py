# main.py
import kivy
import json
import uuid
from kivy.config import Config

# --- Configuration for Window Size (9x16 aspect ratio) ---
Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty, DictProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

kivy.require('2.1.0')

# --- Kivy Design Language String (with Back Buttons) ---
KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

# --- Color and Style Definitions (Dark Mode) ---
#:set BG_COLOR get_color_from_hex('#121212')
#:set SURFACE_COLOR get_color_from_hex('#1E1E1E')
#:set PRIMARY_COLOR get_color_from_hex('#2C2C2E')
#:set TEXT_COLOR get_color_from_hex('#E0E0E0')
#:set MUTED_TEXT_COLOR get_color_from_hex('#8A8A8E')
#:set ACCENT_COLOR get_color_from_hex('#0A84FF')
#:set DANGER_COLOR get_color_from_hex('#FF3B30')
#:set RADIUS 20

# --- Base Widget Styles ---
<Label>:
    color: TEXT_COLOR
    font_size: '16sp'

<Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    color: ACCENT_COLOR
    font_size: '18sp'
    canvas.before:
        Color:
            rgba: PRIMARY_COLOR
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [RADIUS]

<TextInput>:
    background_color: 0, 0, 0, 0
    foreground_color: TEXT_COLOR
    cursor_color: ACCENT_COLOR
    padding: [15, 10, 15, 10]
    canvas.before:
        Color:
            rgba: PRIMARY_COLOR
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [RADIUS]
        Color:
            rgba: ACCENT_COLOR if self.focus else (0,0,0,0)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, RADIUS)
            width: 1.5

<Spinner>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    color: TEXT_COLOR
    canvas.before:
        Color:
            rgba: PRIMARY_COLOR
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [RADIUS]

# --- Custom Widgets ---
<DeleteConfirmationPopup>:
    size_hint: 0.8, 0.3
    background_color: 0,0,0,0
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        canvas.before:
            Color:
                rgba: SURFACE_COLOR
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [RADIUS]
        Label:
            id: message_label
            text: 'Are you sure?'
            font_size: '18sp'
        BoxLayout:
            spacing: '10dp'
            Button:
                text: 'Cancel'
                on_press: root.dismiss()
            Button:
                text: 'Delete'
                on_press: root.confirm_delete()
                canvas.before:
                    Color:
                        rgba: DANGER_COLOR
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [RADIUS]
                color: get_color_from_hex('#FFFFFF')

<ListItemWithDelete>:
    size_hint_y: None
    height: '60dp'
    spacing: '10dp'
    Button:
        id: main_button
        size_hint_x: 0.85
    Button:
        text: 'X'
        size_hint_x: 0.15
        font_size: '22sp'
        bold: True
        id: delete_button
        canvas.before:
            Color:
                rgba: DANGER_COLOR
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [RADIUS]
        color: get_color_from_hex('#FFFFFF')

<WorkoutProgressBar>:
    size_hint_y: None
    height: '20dp'
    canvas:
        Color:
            rgba: PRIMARY_COLOR
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [RADIUS/2]
        Color:
            rgba: ACCENT_COLOR
        RoundedRectangle:
            pos: self.pos
            size: self.width * root.progress_percentage, self.height
            radius: [RADIUS/2]
        Color:
            rgba: get_color_from_hex('#FFFFFF')
        Line:
            points: self.x + self.width * (1 / 1.1), self.y, self.x + self.width * (1 / 1.1), self.y + self.height
            width: 1.5
            dash_offset: 4
            dash_length: 4

<SetEntry>:
    size_hint_y: None
    height: '50dp'
    spacing: '10dp'
    Label:
        text: f"Set {root.set_number}"
        size_hint_x: 0.2
    TextInput:
        id: weight_input
        hint_text: 'Weight'
        input_filter: 'float'
        multiline: False
        on_focus: if not self.focus: app.root.get_screen('active_workout_screen').update_workout_progress()
    Label:
        text: "x"
        size_hint_x: 0.1
    TextInput:
        id: reps_input
        hint_text: 'Reps'
        input_filter: 'int'
        multiline: False
        on_focus: if not self.focus: app.root.get_screen('active_workout_screen').update_workout_progress()
    Button:
        text: '-'
        size_hint_x: 0.15
        on_press: app.root.get_screen('active_workout_screen').remove_set(root)
        canvas.before:
            Color:
                rgba: DANGER_COLOR if self.disabled == False else PRIMARY_COLOR
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [RADIUS]
        color: get_color_from_hex('#FFFFFF') if self.disabled == False else MUTED_TEXT_COLOR
        disabled: not root.can_be_removed

# --- Screen Definitions ---
<Screen>:
    canvas.before:
        Color:
            rgba: BG_COLOR
        Rectangle:
            pos: self.pos
            size: self.size

<PlanSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        Label:
            text: 'Select a Plan'
            font_size: '34sp'
            bold: True
            size_hint_y: 0.2
        ScrollView:
            bar_width: 0 
            effect_cls: 'ScrollEffect'
            BoxLayout:
                id: plan_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        Button:
            text: '+'
            font_size: '40sp'
            size_hint_y: 0.15
            on_press: root.manager.current = 'workout_plan_screen'; root.manager.get_screen('workout_plan_screen').load_plan(new_plan=True)

<WorkoutPlanScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        BoxLayout: # Header
            size_hint_y: 0.2
            spacing: '10dp'
            Button:
                text: '<'
                font_size: '24sp'
                bold: True
                size_hint_x: 0.2
                on_press: root.manager.current = 'plan_select_screen'
            TextInput:
                id: plan_title_input
                text: 'Workout Plan'
                font_size: '34sp'
                bold: True
                multiline: False
                on_text_validate: root.rename_plan(self.text)
        ScrollView:
            bar_width: 0
            effect_cls: 'ScrollEffect'
            BoxLayout:
                id: exercise_list_in_plan
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        Button:
            text: '+'
            font_size: '40sp'
            size_hint_y: 0.15
            on_press: root.manager.current = 'exercise_creation_screen'

<ExerciseCreationScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        BoxLayout: # Header
            size_hint_y: 0.2
            Button:
                text: '<'
                font_size: '24sp'
                bold: True
                size_hint_x: 0.2
                on_press: root.manager.current = 'workout_plan_screen'
            Label:
                text: 'Create Exercise'
                font_size: '34sp'
                bold: True
        TextInput:
            id: exercise_name_input
            hint_text: 'Exercise Name'
            size_hint_y: 0.1
        Spinner:
            id: primary_spinner
            text: 'Primary Muscle'
            size_hint_y: 0.1
        Spinner:
            id: secondary_spinner
            text: 'Secondary Muscle (Optional)'
            size_hint_y: 0.1
        Spinner:
            id: tertiary_spinner
            text: 'Tertiary Muscle (Optional)'
            size_hint_y: 0.1
        BoxLayout:
            size_hint_y: 0.15
            spacing: '10dp'
            Button:
                text: 'Save'
                on_press: root.save_exercise()
            Button:
                text: 'Cancel'
                on_press: root.manager.current = 'workout_plan_screen'

<ActiveWorkoutScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        BoxLayout: # Header
            size_hint_y: 0.15
            Button:
                text: '<'
                font_size: '24sp'
                bold: True
                size_hint_x: 0.2
                on_press: root.manager.current = 'workout_plan_screen'
            Label:
                id: active_exercise_title
                text: 'Active Workout'
                font_size: '34sp'
                bold: True
        
        WorkoutProgressBar:
            id: workout_progress_bar
        
        Label:
            id: volume_label
            text: 'Volume: 0 / 0'
            size_hint_y: 0.1
            color: MUTED_TEXT_COLOR
            
        ScrollView:
            bar_width: 0
            effect_cls: 'ScrollEffect'
            BoxLayout:
                id: set_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: '+ Add Set'
                on_press: root.add_set()
        
        Button:
            text: 'Workout Complete'
            size_hint_y: 0.15
            on_press: root.finish_workout()
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#34C759')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [RADIUS]
            color: get_color_from_hex('#FFFFFF')
'''

# --- Python Logic ---

class DeleteConfirmationPopup(ModalView):
    item_type = StringProperty('')
    item_id = StringProperty('')
    plan_id = StringProperty(None)

    def confirm_delete(self):
        App.get_running_app().delete_item(self.item_type, self.item_id, self.plan_id)
        self.dismiss()

class ListItemWithDelete(BoxLayout):
    pass

class WorkoutProgressBar(BoxLayout):
    progress_percentage = NumericProperty(0)

class SetEntry(BoxLayout):
    set_number = NumericProperty(0)
    can_be_removed = BooleanProperty(True)

class PlanSelectScreen(Screen):
    def on_enter(self, *args):
        self.populate_plans()

    def populate_plans(self):
        self.ids.plan_list.clear_widgets()
        for plan in App.get_running_app().data['plans']:
            item = ListItemWithDelete()
            item.ids.main_button.text = plan['name']
            item.ids.main_button.bind(on_press=lambda instance, p_id=plan['id']: self.select_plan(p_id))
            item.ids.delete_button.bind(on_press=lambda instance, p_id=plan['id']: self.confirm_delete_plan(p_id))
            self.ids.plan_list.add_widget(item)

    def select_plan(self, plan_id):
        self.manager.current = 'workout_plan_screen'
        self.manager.get_screen('workout_plan_screen').load_plan(plan_id=plan_id)

    def confirm_delete_plan(self, plan_id):
        popup = DeleteConfirmationPopup(item_type='plan', item_id=plan_id)
        popup.ids.message_label.text = f"Delete plan '{App.get_running_app().get_plan_name(plan_id)}'?"
        popup.open()

class WorkoutPlanScreen(Screen):
    current_plan_id = StringProperty(None)

    def load_plan(self, plan_id=None, new_plan=False):
        app = App.get_running_app()
        if new_plan:
            new_id = f"plan_{uuid.uuid4().hex[:6]}"
            new_plan_data = {"id": new_id, "name": f"New Plan", "exercises": []}
            app.data['plans'].append(new_plan_data)
            app.save_data()
            self.current_plan_id = new_id
        else:
            self.current_plan_id = plan_id

        plan = next((p for p in app.data['plans'] if p['id'] == self.current_plan_id), None)
        if not plan: 
            self.manager.current = 'plan_select_screen'
            return

        self.ids.plan_title_input.text = plan['name']
        self.ids.exercise_list_in_plan.clear_widgets()
        for exercise in plan['exercises']:
            item = ListItemWithDelete()
            item.ids.main_button.text = f"{exercise['name']} (PB: {int(exercise['pb_total_volume'])})"
            item.ids.main_button.bind(on_press=lambda instance, e_id=exercise['id']: self.select_exercise(e_id))
            item.ids.delete_button.bind(on_press=lambda instance, e_id=exercise['id']: self.confirm_delete_exercise(e_id))
            self.ids.exercise_list_in_plan.add_widget(item)

    def rename_plan(self, new_name):
        app = App.get_running_app()
        plan = next((p for p in app.data['plans'] if p['id'] == self.current_plan_id), None)
        if plan and new_name:
            plan['name'] = new_name
            app.save_data()

    def select_exercise(self, exercise_id):
        self.manager.current = 'active_workout_screen'
        self.manager.get_screen('active_workout_screen').load_exercise(self.current_plan_id, exercise_id)

    def confirm_delete_exercise(self, exercise_id):
        popup = DeleteConfirmationPopup(item_type='exercise', item_id=exercise_id, plan_id=self.current_plan_id)
        popup.ids.message_label.text = f"Delete exercise from this plan?"
        popup.open()

class ExerciseCreationScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        muscle_groups = app.data.get('muscle_groups', [])
        self.ids.primary_spinner.values = [m for m in muscle_groups if m != 'None']
        self.ids.secondary_spinner.values = muscle_groups
        self.ids.tertiary_spinner.values = muscle_groups
        self.ids.exercise_name_input.text = ''
        self.ids.primary_spinner.text = 'Primary Muscle'
        self.ids.secondary_spinner.text = 'Secondary Muscle (Optional)'
        self.ids.tertiary_spinner.text = 'Tertiary Muscle (Optional)'

    def save_exercise(self):
        app = App.get_running_app()
        plan_screen = self.manager.get_screen('workout_plan_screen')
        plan = next((p for p in app.data['plans'] if p['id'] == plan_screen.current_plan_id), None)

        if plan and self.ids.exercise_name_input.text and self.ids.primary_spinner.text != 'Primary Muscle':
            new_exercise = {
                "id": f"ex_{uuid.uuid4().hex[:6]}",
                "name": self.ids.exercise_name_input.text,
                "primary_muscle": self.ids.primary_spinner.text,
                "secondary_muscle": self.ids.secondary_spinner.text if self.ids.secondary_spinner.text != 'Secondary Muscle (Optional)' else 'None',
                "tertiary_muscle": self.ids.tertiary_spinner.text if self.ids.tertiary_spinner.text != 'Tertiary Muscle (Optional)' else 'None',
                "pb_total_volume": 0
            }
            plan['exercises'].append(new_exercise)
            app.save_data()
            plan_screen.load_plan(plan_id=plan['id'])
            self.manager.current = 'workout_plan_screen'

class ActiveWorkoutScreen(Screen):
    current_plan_id = StringProperty(None)
    current_exercise_id = StringProperty(None)
    pb_volume = NumericProperty(0)

    def load_exercise(self, plan_id, exercise_id):
        self.current_plan_id = plan_id
        self.current_exercise_id = exercise_id
        
        app = App.get_running_app()
        plan = next((p for p in app.data['plans'] if p['id'] == plan_id), None)
        if not plan: return
        exercise = next((e for e in plan['exercises'] if e['id'] == exercise_id), None)
        if not exercise: return

        self.ids.active_exercise_title.text = exercise['name']
        self.pb_volume = exercise.get('pb_total_volume', 0)
        self.ids.set_list.clear_widgets()
        for i in range(3):
            self.add_set(is_initial=True)
        self.update_workout_progress()

    def add_set(self, is_initial=False):
        set_count = len(self.ids.set_list.children)
        new_set = SetEntry(set_number=set_count + 1)
        self.ids.set_list.add_widget(new_set, index=0)
        self.update_set_numbers()
    
    def remove_set(self, set_widget):
        if len(self.ids.set_list.children) > 1:
            self.ids.set_list.remove_widget(set_widget)
            self.update_set_numbers()
            self.update_workout_progress()

    def update_set_numbers(self):
        for i, widget in enumerate(reversed(self.ids.set_list.children)):
            widget.set_number = i + 1
            widget.can_be_removed = len(self.ids.set_list.children) > 1

    def update_workout_progress(self):
        current_volume = 0
        for set_widget in self.ids.set_list.children:
            try:
                weight_text = set_widget.ids.weight_input.text
                reps_text = set_widget.ids.reps_input.text
                if weight_text and reps_text:
                    weight = float(weight_text)
                    reps = int(reps_text)
                    current_volume += weight * reps
            except (ValueError, AttributeError):
                pass
        
        max_bar_volume = self.pb_volume * 1.1 if self.pb_volume > 0 else 100
        
        self.ids.volume_label.text = f'Volume: {int(current_volume)} / {int(self.pb_volume)}'
        self.ids.workout_progress_bar.progress_percentage = min(current_volume / max_bar_volume, 1.0) if max_bar_volume > 0 else 0
    
    def finish_workout(self):
        current_volume = 0
        for set_widget in self.ids.set_list.children:
            try:
                weight_text = set_widget.ids.weight_input.text
                reps_text = set_widget.ids.reps_input.text
                if weight_text and reps_text:
                    weight = float(weight_text)
                    reps = int(reps_text)
                    current_volume += weight * reps
            except (ValueError, AttributeError):
                pass
        
        app = App.get_running_app()
        for i, p in enumerate(app.data['plans']):
            if p['id'] == self.current_plan_id:
                for j, e in enumerate(p['exercises']):
                    if e['id'] == self.current_exercise_id:
                        if current_volume > e['pb_total_volume']:
                            app.data['plans'][i]['exercises'][j]['pb_total_volume'] = current_volume
                            app.save_data()
                        break
                break
            
        plan_screen = self.manager.get_screen('workout_plan_screen')
        self.manager.current = 'workout_plan_screen'
        Clock.schedule_once(lambda dt: plan_screen.load_plan(plan_id=plan_screen.current_plan_id))

class GymApp(App):
    data = DictProperty(None)

    def build(self):
        self.load_data()
        Window.clearcolor = get_color_from_hex('#121212')
        
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(PlanSelectScreen(name='plan_select_screen'))
        sm.add_widget(WorkoutPlanScreen(name='workout_plan_screen'))
        sm.add_widget(ExerciseCreationScreen(name='exercise_creation_screen'))
        sm.add_widget(ActiveWorkoutScreen(name='active_workout_screen'))
        return sm

    def load_data(self):
        try:
            with open('data.json', 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"plans": [], "muscle_groups": ["None", "Chest", "Back", "Shoulders", "Biceps", "Triceps", "Quads", "Hamstrings", "Glutes", "Calves", "Abs"]}
            self.save_data()

    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_plan_name(self, plan_id):
        plan = next((p for p in self.data['plans'] if p['id'] == plan_id), None)
        return plan['name'] if plan else ''

    def delete_item(self, item_type, item_id, plan_id=None):
        if item_type == 'plan':
            self.data['plans'] = [p for p in self.data['plans'] if p['id'] != item_id]
            self.root.get_screen('plan_select_screen').populate_plans()
        
        elif item_type == 'exercise' and plan_id:
            for plan in self.data['plans']:
                if plan['id'] == plan_id:
                    plan['exercises'] = [e for e in plan['exercises'] if e['id'] != item_id]
                    break
            self.root.get_screen('workout_plan_screen').load_plan(plan_id=plan_id)
        
        self.save_data()

if __name__ == '__main__':
    GymApp().run()
