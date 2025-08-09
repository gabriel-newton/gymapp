# main.py
import kivy
import json
import uuid
from datetime import datetime, timedelta
import time

from kivy.config import Config

# --- Configuration for Window Size (9x16 aspect ratio) ---
Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty, DictProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.core.text import LabelBase

# --- Font Registration ---
# On EndeavourOS, you can install the font using: paru -S ttf-jetbrains-mono
try:
    LabelBase.register(name='JetBrainsMono',
                       fn_regular='JetBrainsMono-Regular.ttf',
                       fn_bold='JetBrainsMono-Bold.ttf')
    DEFAULT_FONT = 'JetBrainsMono'
except (OSError, IOError):
    print("WARNING: JetBrains Mono font not found. Falling back to default.")
    DEFAULT_FONT = 'Roboto'

# --- Color and Style Definitions (Dark Mode) ---
BG_COLOR = get_color_from_hex('#121212')
SURFACE_COLOR = get_color_from_hex('#1E1E1E')
PRIMARY_COLOR = get_color_from_hex('#2C2C2E')
TEXT_COLOR = get_color_from_hex('#E0E0E0')
MUTED_TEXT_COLOR = get_color_from_hex('#8A8A8E')
ACCENT_COLOR = get_color_from_hex('#0A84FF')
DANGER_COLOR = get_color_from_hex('#FF3B30')
SUCCESS_COLOR = get_color_from_hex('#34C759')
GREEN_COLOR = get_color_from_hex('#32D74B')
RED_COLOR = get_color_from_hex('#FF453A')
RADIUS = 20


# --- Kivy Design Language String ---
KV = f'''
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import datetime datetime
#:import ACCENT_COLOR __main__.ACCENT_COLOR
#:import PRIMARY_COLOR __main__.PRIMARY_COLOR
#:import DANGER_COLOR __main__.DANGER_COLOR
#:import SUCCESS_COLOR __main__.SUCCESS_COLOR
#:import SURFACE_COLOR __main__.SURFACE_COLOR
#:import RADIUS __main__.RADIUS

# --- Base Widget Styles ---
<Label>:
    color: {TEXT_COLOR}
    font_size: '16sp'
    font_name: '{DEFAULT_FONT}'

<Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    color: {ACCENT_COLOR}
    font_size: '18sp'
    font_name: '{DEFAULT_FONT}'
    canvas.before:
        Color:
            rgba: {PRIMARY_COLOR}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [{RADIUS}]

<TextInput>:
    background_color: 0, 0, 0, 0
    foreground_color: {TEXT_COLOR}
    cursor_color: {ACCENT_COLOR}
    padding: [15, 10, 15, 10]
    font_name: '{DEFAULT_FONT}'
    canvas.before:
        Color:
            rgba: {PRIMARY_COLOR}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [{RADIUS}]
        Color:
            rgba: {ACCENT_COLOR} if self.focus else (0,0,0,0)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, {RADIUS})
            width: 1.5

<Spinner>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    color: {TEXT_COLOR}
    font_name: '{DEFAULT_FONT}'
    canvas.before:
        Color:
            rgba: {PRIMARY_COLOR}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [{RADIUS}]

# --- Custom Widgets ---
<ConfirmationPopup>:
    size_hint: 0.8, 0.4
    background_color: 0,0,0,0
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'
        canvas.before:
            Color:
                rgba: {SURFACE_COLOR}
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [{RADIUS}]
        Label:
            id: message_label
            text: 'Are you sure?'
            font_size: '18sp'
            halign: 'center'
        BoxLayout:
            spacing: '10dp'
            Button:
                text: 'Cancel'
                on_press: root.dismiss()
            Button:
                id: confirm_button
                text: 'Confirm'
                on_press: root.dispatch('on_confirm')
                canvas.before:
                    Color:
                        rgba: {DANGER_COLOR}
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [{RADIUS}]
                color: {get_color_from_hex('#FFFFFF')}

<RestTimerPopup>:
    size_hint: 0.8, 0.5
    background_color: 0,0,0,0
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '10dp'
        canvas.before:
            Color:
                rgba: SURFACE_COLOR
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [RADIUS]
        Label:
            text: 'Manage Rest Timer'
            font_size: '20sp'
            bold: True
            size_hint_y: 0.2
        GridLayout:
            cols: 2
            spacing: '10dp'
            Button:
                text: 'Resume'
                on_press: root.screen.resume_rest_timer(); root.dismiss()
            Button:
                text: '+15s'
                on_press: root.screen.add_to_rest_timer(15)
            Button:
                text: 'Restart'
                on_press: root.screen.start_rest_timer(); root.dismiss()
            Button:
                text: 'Skip Rest'
                on_press: root.screen.stop_rest_timer(); root.dismiss()
                canvas.before:
                    Color:
                        rgba: DANGER_COLOR
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [RADIUS]
                color: get_color_from_hex('#FFFFFF')

<PlanListItem>:
    size_hint_y: None
    height: '60dp'
    spacing: '10dp'
    Button:
        id: main_button
        text: 'Plan'
    Button:
        text: 'X'
        id: delete_button
        size_hint_x: 0
        width: 0
        opacity: 0
        disabled: True
        canvas.before:
            Color:
                rgba: {DANGER_COLOR}
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [{RADIUS}]
        color: {get_color_from_hex('#FFFFFF')}

<ExerciseListItem>:
    size_hint_y: None
    height: '60dp'
    spacing: '10dp'
    is_complete: False
    is_editing: False
    Button:
        id: main_button
        text: 'Exercise'
    Label:
        id: check_mark
        text: '✓' if root.is_complete else ''
        font_size: '28sp'
        color: {SUCCESS_COLOR}
        size_hint_x: 0.15 if not root.is_editing else 0
        width: self.texture_size[0] if not root.is_editing else 0
        opacity: 1 if not root.is_editing else 0
    
    BoxLayout:
        size_hint_x: 0.4 if root.is_editing else 0
        width: self.minimum_width if root.is_editing else 0
        opacity: 1 if root.is_editing else 0
        disabled: not root.is_editing
        spacing: '5dp'
        Button:
            id: move_up_button
            text: '▲'
        Button:
            id: move_down_button
            text: '▼'
        Button:
            id: delete_button
            text: 'X'
            canvas.before:
                Color:
                    rgba: {DANGER_COLOR}
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [{RADIUS}]
            color: {get_color_from_hex('#FFFFFF')}

<SetEntry>:
    size_hint_y: None
    height: '50dp'
    spacing: '10dp'
    set_number: 0
    can_be_removed: True
    Label:
        text: f"Set {{root.set_number}}"
        size_hint_x: 0.2
    TextInput:
        id: weight_input
        hint_text: 'Weight'
        input_filter: 'float'
        multiline: False
    Label:
        text: "x"
        size_hint_x: 0.1
    TextInput:
        id: reps_input
        hint_text: 'Reps'
        input_filter: 'int'
        multiline: False
    Button:
        text: '-'
        size_hint_x: 0.15
        on_press: app.root.get_screen('active_workout_screen').remove_set(root)
        canvas.before:
            Color:
                rgba: {DANGER_COLOR} if self.disabled == False else {PRIMARY_COLOR}
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [{RADIUS}]
        color: {get_color_from_hex('#FFFFFF')} if self.disabled == False else {MUTED_TEXT_COLOR}
        disabled: not root.can_be_removed

<PureKivyGraph>:
    padding: [dp(35), dp(20), dp(10), dp(30)] 
    dual_axis_padding: [dp(35), dp(35), dp(35), dp(35)]

# --- Screen Definitions ---
<Screen>:
    canvas.before:
        Color:
            rgba: {BG_COLOR}
        Rectangle:
            pos: self.pos
            size: self.size

<PlanSelectScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '10dp'
        Label:
            text: 'GymApp'
            font_size: '34sp'
            bold: True
            size_hint_y: 0.15
        ScrollView:
            bar_width: 0 
            effect_cls: 'ScrollEffect'
            BoxLayout:
                id: plan_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
        BoxLayout:
            size_hint_y: 0.15
            spacing: '10dp'
            Button:
                text: 'Stats'
            Button:
                text: 'Edit'
                on_press: root.toggle_edit_mode()
                id: edit_button
            Button:
                text: '+'
                font_size: '40sp'
                size_hint_x: 1 if root.is_editing else 0
                width: self.height if root.is_editing else 0
                opacity: 1 if root.is_editing else 0
                disabled: not root.is_editing
                on_press: root.manager.current = 'workout_plan_screen'; root.manager.get_screen('workout_plan_screen').load_plan(new_plan=True)

<WorkoutPlanScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        BoxLayout:
            size_hint_y: 0.15
            spacing: '10dp'
            Button:
                text: '<'
                size_hint_x: 0.2
                on_press: root.go_back_to_plans()
            TextInput:
                id: plan_title_input
                text: 'Workout Plan'
                font_size: '30sp'
                bold: True
                multiline: False
                disabled: not root.is_editing
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
        
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'bottom'
            size_hint_y: 0.2
            padding: ['0dp', '10dp', '0dp', '0dp']
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
                Button:
                    id: add_exercise_button
                    text: '+ Add Exercise'
                    font_size: '24sp'
                    size_hint_y: None
                    height: '50dp'
                    opacity: 1 if root.is_editing else 0
                    disabled: not root.is_editing
                    on_press: root.manager.current = 'exercise_creation_screen'

                BoxLayout:
                    size_hint_y: None
                    height: '50dp'
                    spacing: '10dp'
                    Button:
                        id: edit_mode_button
                        text: 'Edit Plan' if not root.is_editing else 'Done Editing'
                        on_press: root.toggle_edit_mode()
                    Button:
                        id: workout_control_button
                        text: 'Start Workout'
                        on_press: root.toggle_workout_mode()

<ExerciseCreationScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        BoxLayout:
            size_hint_y: 0.2
            Button:
                text: '<'
                font_size: '24sp'
                bold: True
                size_hint_x: 0.2
                on_press: root.manager.current = 'workout_plan_screen'
            Label:
                text: 'Add Exercise'
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
        TextInput:
            id: rest_time_input
            hint_text: 'Rest Time (seconds), e.g. 60'
            input_filter: 'int'
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

<ExerciseDetailScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '10dp'
        BoxLayout:
            size_hint_y: 0.1
            spacing: '10dp'
            Button:
                text: '<'
                size_hint_x: 0.2
                on_press: root.go_back()
            TextInput:
                id: exercise_title_input
                text: 'Exercise'
                font_size: '30sp'
                bold: True
                multiline: False
                disabled: not root.is_editing
        
        BoxLayout:
            size_hint_y: 0.8 if root.is_editing else 0
            height: self.minimum_height if root.is_editing else 0
            opacity: 1 if root.is_editing else 0
            disabled: not root.is_editing
            orientation: 'vertical'
            spacing: '15dp'
            padding: ['0dp', '15dp']
            Label:
                text: 'Primary Muscle'
                size_hint_y: None
                height: '20dp'
                halign: 'left'
            Spinner:
                id: primary_spinner
                text: 'Primary Muscle'
                size_hint_y: None
                height: '50dp'
            Label:
                text: 'Secondary Muscle'
                size_hint_y: None
                height: '20dp'
                halign: 'left'
            Spinner:
                id: secondary_spinner
                text: 'Secondary Muscle'
                size_hint_y: None
                height: '50dp'
            Label:
                text: 'Default Rest Time (s)'
                size_hint_y: None
                height: '20dp'
                halign: 'left'
            TextInput:
                id: rest_time_input
                hint_text: 'Rest Time (s)'
                input_filter: 'int'
                size_hint_y: None
                height: '50dp'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.8 if not root.is_editing else 0
            opacity: 1 if not root.is_editing else 0
            disabled: root.is_editing
            spacing: '5dp'
            Label:
                text: 'Avg. Weight (Red) & Reps (Green)'
                size_hint_y: 0.05
                font_size: '14sp'
                color: {MUTED_TEXT_COLOR}
            PureKivyGraph:
                id: weight_reps_graph
                is_dual_axis: True
            Label:
                text: 'Total Volume Progression'
                size_hint_y: 0.05
                font_size: '14sp'
                color: {MUTED_TEXT_COLOR}
            PureKivyGraph:
                id: volume_graph
        
        BoxLayout:
            size_hint_y: 0.15
            padding: ['0dp', '10dp', '0dp', '0dp']
            spacing: '10dp'
            Button:
                id: edit_button
                text: 'Edit Exercise' if not root.is_editing else 'Cancel'
                on_press: root.toggle_edit_mode()
            Button:
                id: save_button
                text: 'Save Changes'
                opacity: 1 if root.is_editing else 0
                disabled: not root.is_editing
                on_press: root.save_changes()
                canvas.before:
                    Color:
                        rgba: {SUCCESS_COLOR}
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [{RADIUS}]

<ActiveWorkoutScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '10dp'
        
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            Button:
                text: '<'
                size_hint_x: 0.2
                on_press: root.finish_exercise()
            Label:
                id: active_exercise_title
                text: 'Active Workout'
                font_size: '34sp'
                bold: True
        
        ScrollView:
            id: set_scroll
            bar_width: 0
            effect_cls: 'ScrollEffect'
            GridLayout:
                id: set_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: '10dp'
            padding: ['0dp', '10dp', '0dp', '0dp']

            TextInput:
                id: exercise_notes_input
                hint_text: 'Notes for this exercise...'
                size_hint_y: None
                height: '80dp'
                multiline: True
            
            Button:
                text: '+ Add Set'
                size_hint_y: None
                height: '50dp'
                on_press: root.add_set()

            BoxLayout:
                size_hint_y: None
                height: '50dp'
                spacing: '10dp'
                
                Button:
                    id: rest_timer_button
                    text: root.rest_timer_text
                    color: get_color_from_hex('#FFFFFF') if root.is_resting else ACCENT_COLOR
                    on_press: root.open_rest_timer_options() if root.is_resting else root.start_rest_timer()
                    canvas.before:
                        Color:
                            rgba: ACCENT_COLOR if root.is_resting else PRIMARY_COLOR
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [RADIUS]
                
                Button:
                    text: 'Finish Exercise'
                    on_press: root.finish_exercise()
                    canvas.before:
                        Color:
                            rgba: SUCCESS_COLOR
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [RADIUS]

<WorkoutSummaryScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '10dp'
        Label:
            text: 'Workout Summary'
            font_size: '34sp'
            bold: True
            size_hint_y: 0.15
        
        ScrollView:
            bar_width: 0
            GridLayout:
                id: summary_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: '15dp'
        
        BoxLayout:
            size_hint_y: 0.15
            spacing: '10dp'
            Button:
                text: 'Cancel'
                on_press: root.cancel_finish()
                canvas.before:
                    Color:
                        rgba: DANGER_COLOR
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [RADIUS]
                color: {get_color_from_hex('#FFFFFF')}
            Button:
                text: 'Confirm & Save'
                on_press: root.confirm_finish()
                canvas.before:
                    Color:
                        rgba: SUCCESS_COLOR
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [RADIUS]
                color: get_color_from_hex('#FFFFFF')

<StatisticsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        BoxLayout:
            size_hint_y: 0.1
            Button:
                text: '<'
                size_hint_x: 0.2
                on_press: root.manager.current = 'plan_select_screen'
            Label:
                text: 'Statistics & PRs'
                font_size: '30sp'
                bold: True
        
        ScrollView:
            bar_width: 0
            effect_cls: 'ScrollEffect'
            GridLayout:
                id: stats_layout
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: '10dp'
'''

# --- Python Logic ---

class ConfirmationPopup(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_confirm')

    def on_confirm(self):
        pass

class RestTimerPopup(ModalView):
    screen = ObjectProperty(None)

class PlanListItem(BoxLayout):
    pass

class ExerciseListItem(BoxLayout):
    is_complete = BooleanProperty(False)
    is_editing = BooleanProperty(False)

class SetEntry(BoxLayout):
    set_number = NumericProperty(0)
    can_be_removed = BooleanProperty(True)

class PureKivyGraph(FloatLayout):
    points1 = ListProperty([])
    points2 = ListProperty([])
    is_dual_axis = BooleanProperty(False)
    y_min1 = NumericProperty(0)
    y_max1 = NumericProperty(100)
    y_min2 = NumericProperty(0)
    y_max2 = NumericProperty(10)
    x_max = NumericProperty(4)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw_graph, size=self.draw_graph)

    def update_plot(self, **kwargs):
        self.points1 = kwargs.get('points1', [])
        self.y_min1 = kwargs.get('y_min1', 0)
        self.y_max1 = kwargs.get('y_max1', 100)
        self.x_max = kwargs.get('x_max', 4)

        if self.is_dual_axis:
            self.points2 = kwargs.get('points2', [])
            self.y_min2 = kwargs.get('y_min2', 0)
            self.y_max2 = kwargs.get('y_max2', 10)

        self.draw_graph()

    def draw_graph(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()
        self.clear_widgets()

        pad_l, pad_t, pad_r, pad_b = self.padding
        if self.is_dual_axis:
            pad_l1, pad_r1, pad_l2, pad_r2 = self.dual_axis_padding
            pad_l = pad_l1
            pad_r = pad_r1

        graph_x = self.x + pad_l
        graph_y = self.y + pad_b
        graph_w = self.width - pad_l - pad_r
        graph_h = self.height - pad_t - pad_b

        if graph_w <= 1 or graph_h <= 1: return

        with self.canvas.before:
            Color(*PRIMARY_COLOR)
            Rectangle(pos=(graph_x, graph_y), size=(graph_w, graph_h))
            Color(*MUTED_TEXT_COLOR)
            Line(rectangle=(graph_x, graph_y, graph_w, graph_h), width=1.1)

        self._draw_y_axis(graph_x, graph_y, graph_w, graph_h, 1)
        if self.is_dual_axis:
            self._draw_y_axis(graph_x, graph_y, graph_w, graph_h, 2)
        
        self._draw_x_axis(graph_x, graph_y, graph_w, graph_h)
        
        with self.canvas.after:
            self._draw_plot_line(graph_x, graph_y, graph_w, graph_h, 1)
            if self.is_dual_axis:
                self._draw_plot_line(graph_x, graph_y, graph_w, graph_h, 2)

    def _draw_y_axis(self, gx, gy, gw, gh, axis_index):
        y_min = getattr(self, f'y_min{axis_index}')
        y_max = getattr(self, f'y_max{axis_index}')
        color = RED_COLOR if axis_index == 1 else GREEN_COLOR
        
        y_range = y_max - y_min
        if y_range == 0: y_range = 1
        num_y_ticks = 4
        
        for i in range(num_y_ticks + 1):
            val = y_min + (y_range / num_y_ticks) * i
            y = gy + (i / num_y_ticks) * gh
            
            if axis_index == 1:
                with self.canvas.before:
                    Color(0.3, 0.3, 0.3, 0.5)
                    Line(points=[gx, y, gx + gw, y], width=1, dash_offset=2, dash_length=2)
            
            label_x = self.x if axis_index == 1 else self.right - self.dual_axis_padding[3]
            halign = 'right' if axis_index == 1 else 'left'
            
            label = Label(
                text=f"{val:.1f}", font_size='10sp', color=color,
                size_hint=(None, None), size=(dp(35), dp(20)),
                pos=(label_x, y - dp(10)), halign=halign, valign='center', font_name=DEFAULT_FONT
            )
            self.add_widget(label)

    def _draw_x_axis(self, gx, gy, gw, gh):
        x_range = self.x_max
        if x_range == 0: x_range = 1
        num_x_ticks = int(self.x_max) + 1
        
        for i in range(num_x_ticks):
            x = gx + (i / x_range) * gw if x_range > 0 else gx
            label = Label(
                text=f"#{i+1}", font_size='12sp', color=MUTED_TEXT_COLOR,
                size_hint=(None, None), size=(dp(40), dp(20)),
                pos=(x - dp(20), self.y), halign='center', valign='top', font_name=DEFAULT_FONT
            )
            self.add_widget(label)

    def _draw_plot_line(self, gx, gy, gw, gh, axis_index):
        points = getattr(self, f'points{axis_index}')
        y_min = getattr(self, f'y_min{axis_index}')
        y_max = getattr(self, f'y_max{axis_index}')
        color = RED_COLOR if axis_index == 1 else GREEN_COLOR
        if not self.is_dual_axis: color = ACCENT_COLOR

        if points:
            Color(*color)
            x_range = self.x_max
            if x_range == 0: x_range = 1
            y_range = y_max - y_min
            if y_range == 0: y_range = 1

            plot_points = []
            for x_val, y_val in points:
                px = gx + (x_val / x_range) * gw if x_range > 0 else gx
                py = gy + ((y_val - y_min) / y_range) * gh
                plot_points.extend([px, py])
            
            Line(points=plot_points, width=1.8)

class PlanSelectScreen(Screen):
    is_editing = BooleanProperty(False)

    def on_enter(self, *args):
        self.is_editing = False
        self.ids.edit_button.text = 'Edit'
        self.populate_plans()

    def populate_plans(self):
        self.ids.plan_list.clear_widgets()
        for plan in App.get_running_app().data['plans']:
            item = PlanListItem()
            item.ids.main_button.text = plan['name']
            item.ids.main_button.bind(on_press=lambda instance, p_id=plan['id']: self.select_plan(p_id))
            item.ids.delete_button.bind(on_press=lambda instance, p_id=plan['id']: self.confirm_delete_plan(p_id))
            self.ids.plan_list.add_widget(item)

    def select_plan(self, plan_id):
        self.manager.current = 'workout_plan_screen'
        self.manager.get_screen('workout_plan_screen').load_plan(plan_id=plan_id)

    def confirm_delete_plan(self, plan_id):
        popup = ConfirmationPopup()
        popup.ids.message_label.text = f"Delete plan '{App.get_running_app().get_plan_name(plan_id)}'?"
        
        def confirm_handler(*args):
            App.get_running_app().delete_item('plan', plan_id)
            popup.dismiss()
            
        popup.bind(on_confirm=confirm_handler)
        popup.open()

    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        self.ids.edit_button.text = 'Done' if self.is_editing else 'Edit'
        for child in self.ids.plan_list.children:
            child.ids.delete_button.size_hint_x = 0.15 if self.is_editing else 0
            child.ids.delete_button.width = child.height if self.is_editing else 0
            child.ids.delete_button.opacity = 1 if self.is_editing else 0
            child.ids.delete_button.disabled = not self.is_editing


class WorkoutPlanScreen(Screen):
    current_plan_id = StringProperty(None)
    is_editing = BooleanProperty(False)
    is_workout_active = BooleanProperty(False)
    active_session_data = DictProperty({})
    workout_timer_event = ObjectProperty(None, allownone=True)
    start_time = NumericProperty(0)

    def load_plan(self, plan_id=None, new_plan=False):
        app = App.get_running_app()
        if new_plan:
            # FIX: Use a longer, more unique ID
            new_id = f"plan_{uuid.uuid4().hex[:16]}"
            new_plan_data = {"id": new_id, "name": f"New Plan", "exercises": []}
            app.data['plans'].append(new_plan_data)
            app.save_data()
            self.current_plan_id = new_id
            self.is_editing = True
        else:
            self.current_plan_id = plan_id
            self.is_editing = False
        
        self.is_workout_active = False
        self.update_view()

    def update_view(self):
        plan = next((p for p in App.get_running_app().data['plans'] if p['id'] == self.current_plan_id), None)
        if not plan: 
            self.manager.current = 'plan_select_screen'
            return

        self.ids.plan_title_input.text = plan['name']
        self.ids.exercise_list_in_plan.clear_widgets()
        for exercise in plan['exercises']:
            item = ExerciseListItem(is_editing=self.is_editing)
            item.ids.main_button.text = f"{exercise['name']}"
            item.ids.main_button.bind(on_press=lambda instance, ex=exercise: self.select_exercise(ex))
            item.ids.delete_button.bind(on_press=lambda instance, ex_id=exercise['id']: self.confirm_delete_exercise(ex_id))
            item.ids.move_up_button.bind(on_press=lambda instance, ex_id=exercise['id']: self.move_exercise(ex_id, -1))
            item.ids.move_down_button.bind(on_press=lambda instance, ex_id=exercise['id']: self.move_exercise(ex_id, 1))
            self.ids.exercise_list_in_plan.add_widget(item)
        
        self.ids.workout_control_button.text = 'Start Workout'
        self.ids.workout_control_button.canvas.before.clear()
        with self.ids.workout_control_button.canvas.before:
            Color(*PRIMARY_COLOR)
            RoundedRectangle(pos=self.ids.workout_control_button.pos, size=self.ids.workout_control_button.size, radius=[RADIUS])

    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing
        self.update_view()

    def rename_plan(self, new_name):
        app = App.get_running_app()
        plan = next((p for p in app.data['plans'] if p['id'] == self.current_plan_id), None)
        if plan and new_name:
            plan['name'] = new_name
            app.save_data()

    def select_exercise(self, exercise_data):
        if self.is_workout_active:
            self.manager.current = 'active_workout_screen'
            self.manager.get_screen('active_workout_screen').load_exercise(exercise_data, self.active_session_data)
        else:
            self.manager.current = 'exercise_detail_screen'
            self.manager.get_screen('exercise_detail_screen').load_exercise(self.current_plan_id, exercise_data['id'])

    def toggle_workout_mode(self):
        if self.is_workout_active:
            summary_screen = self.manager.get_screen('workout_summary_screen')
            summary_screen.load_summary(self.active_session_data, self)
            self.manager.current = 'workout_summary_screen'
        else:
            self.is_workout_active = True
            self.start_workout()
    
    def start_workout(self):
        self.active_session_data = {
            'plan_id': self.current_plan_id,
            'date': datetime.today().strftime('%Y-%m-%d'),
            'exercises': {}
        }
        self.start_time = time.time()
        self.workout_timer_event = Clock.schedule_interval(self.update_timer_display, 1)
        self.ids.workout_control_button.canvas.before.clear()
        with self.ids.workout_control_button.canvas.before:
            Color(*DANGER_COLOR)
            RoundedRectangle(pos=self.ids.workout_control_button.pos, size=self.ids.workout_control_button.size, radius=[RADIUS])
        self.ids.edit_mode_button.disabled = True

    def stop_workout(self, session_data, save=True):
        if self.workout_timer_event:
            self.workout_timer_event.cancel()
            self.workout_timer_event = None
        
        if save and session_data:
            final_session = {
                # FIX: Use a longer, more unique ID
                'session_id': f"sess_{uuid.uuid4().hex[:16]}",
                'date': session_data.get('date', ''),
                'plan_id': session_data.get('plan_id', ''),
                'exercises': [ex for ex in session_data.get('exercises', {}).values() if ex.get('sets')],
            }
            if final_session['exercises']:
                app = App.get_running_app()
                app.data['workout_sessions'].append(final_session)
                app.save_data()

        self.is_workout_active = False
        self.ids.edit_mode_button.disabled = False
        self.active_session_data = {}
        self.update_view()

    def update_timer_display(self, dt):
        elapsed = time.time() - self.start_time
        mins, secs = divmod(elapsed, 60)
        self.ids.workout_control_button.text = f'Finish Workout ({int(mins):02}:{int(secs):02})'

    def update_exercise_status(self, exercise_id, is_complete):
        ex_data = self.active_session_data.get('exercises', {}).get(exercise_id)
        if not ex_data:
            return

        for item in self.ids.exercise_list_in_plan.children:
            if isinstance(item, ExerciseListItem) and item.ids.main_button.text == ex_data['name']:
                item.is_complete = is_complete
                break
    
    def go_back_to_plans(self):
        if self.is_workout_active:
            popup = ConfirmationPopup()
            popup.ids.message_label.text = 'Cancel current workout? Progress will be lost.'
            
            def confirm_handler(*args):
                self._confirm_go_back()
                popup.dismiss()

            popup.bind(on_confirm=confirm_handler)
            popup.open()
        else:
            self.manager.current = 'plan_select_screen'

    def _confirm_go_back(self):
        self.stop_workout(self.active_session_data, save=False)
        self.manager.current = 'plan_select_screen'
    
    def confirm_delete_exercise(self, exercise_id):
        popup = ConfirmationPopup()
        popup.ids.message_label.text = f"Delete exercise from this plan?"
        
        def confirm_handler(*args):
            self.delete_exercise(exercise_id)
            popup.dismiss()
            
        popup.bind(on_confirm=confirm_handler)
        popup.open()

    def delete_exercise(self, exercise_id):
        app = App.get_running_app()
        for plan in app.data['plans']:
            if plan['id'] == self.current_plan_id:
                plan['exercises'] = [e for e in plan['exercises'] if e['id'] != exercise_id]
                break
        app.save_data()
        self.update_view()

    def move_exercise(self, exercise_id, direction):
        app = App.get_running_app()
        for plan in app.data['plans']:
            if plan['id'] == self.current_plan_id:
                exercises = plan['exercises']
                idx = next((i for i, ex in enumerate(exercises) if ex['id'] == exercise_id), -1)
                
                if idx != -1:
                    new_idx = idx + direction
                    if 0 <= new_idx < len(exercises):
                        exercises.insert(new_idx, exercises.pop(idx))
                        app.save_data()
                        self.update_view()
                break


class ExerciseCreationScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        muscle_groups = app.data.get('muscle_groups', [])
        self.ids.primary_spinner.values = [m for m in muscle_groups if m != 'None']
        self.ids.secondary_spinner.values = muscle_groups
        self.ids.exercise_name_input.text = ''
        self.ids.primary_spinner.text = 'Primary Muscle'
        self.ids.secondary_spinner.text = 'Secondary Muscle (Optional)'
        self.ids.rest_time_input.text = '60'

    def save_exercise(self):
        app = App.get_running_app()
        plan_screen = self.manager.get_screen('workout_plan_screen')
        plan = next((p for p in app.data['plans'] if p['id'] == plan_screen.current_plan_id), None)

        if plan and self.ids.exercise_name_input.text and self.ids.primary_spinner.text != 'Primary Muscle':
            new_exercise = {
                # FIX: Use a longer, more unique ID
                "id": f"ex_{uuid.uuid4().hex[:16]}",
                "name": self.ids.exercise_name_input.text,
                "primary_muscle": self.ids.primary_spinner.text,
                "secondary_muscle": self.ids.secondary_spinner.text if self.ids.secondary_spinner.text != 'Secondary Muscle (Optional)' else 'None',
                "rest_time": int(self.ids.rest_time_input.text or 60)
            }
            plan['exercises'].append(new_exercise)
            app.save_data()
            plan_screen.load_plan(plan_id=plan['id'])
            self.manager.current = 'workout_plan_screen'

class ExerciseDetailScreen(Screen):
    current_plan_id = StringProperty(None)
    current_exercise_id = StringProperty(None)
    is_editing = BooleanProperty(False)

    def load_exercise(self, plan_id, exercise_id):
        self.current_plan_id = plan_id
        self.current_exercise_id = exercise_id
        self.is_editing = False
        self.update_view()
        self.plot_progress()

    def update_view(self):
        app = App.get_running_app()
        plan = next((p for p in app.data['plans'] if p['id'] == self.current_plan_id), None)
        if not plan: return
        exercise = next((e for e in plan['exercises'] if e['id'] == self.current_exercise_id), None)
        if not exercise: return
        
        self.ids.exercise_title_input.text = exercise['name']
        muscle_groups = app.data.get('muscle_groups', [])
        self.ids.primary_spinner.values = [m for m in muscle_groups if m != 'None']
        self.ids.secondary_spinner.values = muscle_groups
        self.ids.primary_spinner.text = exercise.get('primary_muscle', 'Primary Muscle')
        self.ids.secondary_spinner.text = exercise.get('secondary_muscle', 'Secondary Muscle')
        self.ids.rest_time_input.text = str(exercise.get('rest_time', 60))

    def plot_progress(self):
        app = App.get_running_app()
        sessions = app.data.get('workout_sessions', [])
        
        weight_data, reps_data, volume_data = [], [], []
        for sess in sorted(sessions, key=lambda x: x['date']):
            for ex in sess['exercises']:
                ex_id_key = 'id' if 'id' in ex else 'exercise_id'
                if ex[ex_id_key] == self.current_exercise_id and ex.get('sets'):
                    avg_weight = sum(s['weight'] for s in ex['sets']) / len(ex['sets'])
                    avg_reps = sum(s['reps'] for s in ex['sets']) / len(ex['sets'])
                    total_volume = sum(s['weight'] * s['reps'] for s in ex['sets'])
                    weight_data.append(avg_weight)
                    reps_data.append(avg_reps)
                    volume_data.append(total_volume)
        
        last_5_weights = weight_data[-5:]
        last_5_reps = reps_data[-5:]
        last_5_vols = volume_data[-5:]
        
        x_max = len(last_5_weights) - 1 if len(last_5_weights) > 1 else 1

        if last_5_weights:
            self.ids.weight_reps_graph.update_plot(
                points1=[(i, w) for i, w in enumerate(last_5_weights)],
                y_min1=min(last_5_weights) * 0.9, y_max1=max(last_5_weights) * 1.1,
                points2=[(i, r) for i, r in enumerate(last_5_reps)],
                y_min2=min(last_5_reps) * 0.9, y_max2=max(last_5_reps) * 1.1,
                x_max=x_max
            )
        else:
            self.ids.weight_reps_graph.update_plot()

        if last_5_vols:
            self.ids.volume_graph.update_plot(
                points1=[(i, v) for i, v in enumerate(last_5_vols)],
                y_min1=min(last_5_vols) * 0.9, y_max1=max(last_5_vols) * 1.1,
                x_max=x_max
            )
        else:
            self.ids.volume_graph.update_plot()


    def toggle_edit_mode(self):
        self.is_editing = not self.is_editing

    def save_changes(self):
        app = App.get_running_app()
        for plan in app.data['plans']:
            if plan['id'] == self.current_plan_id:
                for ex in plan['exercises']:
                    if ex['id'] == self.current_exercise_id:
                        ex['name'] = self.ids.exercise_title_input.text
                        ex['primary_muscle'] = self.ids.primary_spinner.text
                        ex['secondary_muscle'] = self.ids.secondary_spinner.text
                        ex['rest_time'] = int(self.ids.rest_time_input.text or 60)
                        break
                break
        app.save_data()
        self.is_editing = False
        self.update_view()

    def go_back(self):
        self.manager.current = 'workout_plan_screen'
        self.manager.get_screen('workout_plan_screen').load_plan(plan_id=self.current_plan_id)

class ActiveWorkoutScreen(Screen):
    exercise_data = DictProperty({})
    session_data = DictProperty({})
    
    rest_time_remaining = NumericProperty(0)
    is_resting = BooleanProperty(False)
    timer_event = ObjectProperty(None, allownone=True)
    rest_timer_text = StringProperty('Start Rest')

    def on_leave(self, *args):
        self.stop_rest_timer()

    def load_exercise(self, exercise_data, session_data):
        self.exercise_data = exercise_data
        self.session_data = session_data
        self.ids.active_exercise_title.text = self.exercise_data['name']
        self.ids.set_list.clear_widgets()
        self.stop_rest_timer()
        
        ex_id = self.exercise_data['id']
        if ex_id in self.session_data.get('exercises', {}):
            ex_log = self.session_data['exercises'][ex_id]
            self.ids.exercise_notes_input.text = ex_log.get('notes', '')
            for i, s in enumerate(ex_log['sets']):
                set_entry = SetEntry(set_number=i + 1)
                set_entry.ids.weight_input.text = str(s['weight'])
                set_entry.ids.reps_input.text = str(s['reps'])
                self.ids.set_list.add_widget(set_entry)
            self.update_set_numbers()
        else:
            self.ids.exercise_notes_input.text = ''
            for _ in range(3): self.add_set()

    def add_set(self):
        new_set = SetEntry()
        self.ids.set_list.add_widget(new_set)
        self.update_set_numbers()
        Clock.schedule_once(lambda dt: self.ids.set_scroll.scroll_to(new_set))
    
    def remove_set(self, set_widget):
        if len(self.ids.set_list.children) > 1:
            self.ids.set_list.remove_widget(set_widget)
            self.update_set_numbers()

    def update_set_numbers(self):
        for i, widget in enumerate(reversed(self.ids.set_list.children)):
            widget.set_number = i + 1
            widget.can_be_removed = len(self.ids.set_list.children) > 1

    def start_rest_timer(self, restart=True):
        if restart:
            total_time = self.exercise_data.get('rest_time', 60)
            self.rest_time_remaining = total_time
        
        self.is_resting = True
        self.rest_timer_text = f"{int(self.rest_time_remaining)}s Remaining"
        
        if self.timer_event: self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_rest_timer, 1)

    def update_rest_timer(self, dt):
        self.rest_time_remaining -= 1
        self.rest_timer_text = f"{int(self.rest_time_remaining)}s Remaining"
        if self.rest_time_remaining <= 0:
            self.stop_rest_timer()
            
    def stop_rest_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        self.is_resting = False
        self.rest_time_remaining = 0
        self.rest_timer_text = 'Start Rest'

    def pause_rest_timer(self):
        if self.timer_event:
            self.timer_event.cancel()

    def resume_rest_timer(self):
        self.start_rest_timer(restart=False)

    def add_to_rest_timer(self, seconds):
        self.rest_time_remaining += seconds
        self.rest_timer_text = f"{int(self.rest_time_remaining)}s Remaining"

    def open_rest_timer_options(self):
        self.pause_rest_timer()
        popup = RestTimerPopup(screen=self)
        popup.open()

    def finish_exercise(self):
        self.stop_rest_timer()
        sets = []
        for set_widget in reversed(self.ids.set_list.children):
            try:
                weight = float(set_widget.ids.weight_input.text or 0)
                reps = int(set_widget.ids.reps_input.text or 0)
                if weight > 0 and reps > 0:
                    sets.append({'weight': weight, 'reps': reps})
            except (ValueError, AttributeError): continue
        
        ex_id = self.exercise_data['id']
        self.session_data['exercises'][ex_id] = {
            'exercise_id': ex_id,
            'name': self.exercise_data['name'],
            'sets': sets,
            'notes': self.ids.exercise_notes_input.text
        }

        plan_screen = self.manager.get_screen('workout_plan_screen')
        plan_screen.update_exercise_status(ex_id, is_complete=bool(sets))
        self.manager.current = 'workout_plan_screen'

class WorkoutSummaryScreen(Screen):
    session_data = DictProperty({})
    plan_screen = ObjectProperty(None)

    def load_summary(self, session_data, plan_screen):
        self.session_data = session_data
        self.plan_screen = plan_screen
        layout = self.ids.summary_layout
        layout.clear_widgets()

        logged_exercises = [ex for ex in session_data.get('exercises', {}).values() if ex.get('sets')]

        if not logged_exercises:
            layout.add_widget(Label(text="No sets were logged in this workout.", italic=True))
            return

        for exercise in logged_exercises:
            ex_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing='5dp')
            ex_box.bind(minimum_height=ex_box.setter('height'))
            
            ex_box.add_widget(Label(
                text=f"[b]{exercise['name']}[/b]",
                markup=True,
                size_hint_y=None,
                height='30dp'
            ))
            
            for s in exercise['sets']:
                set_label = Label(
                    text=f"  - {s['weight']} kg x {s['reps']} reps",
                    size_hint_y=None,
                    height='25dp'
                )
                ex_box.add_widget(set_label)
            
            layout.add_widget(ex_box)
    
    def confirm_finish(self):
        self.plan_screen.stop_workout(self.session_data, save=True)
        self.manager.current = 'plan_select_screen'

    def cancel_finish(self):
        self.manager.current = 'workout_plan_screen'


class StatisticsScreen(Screen):
    pass

class GymApp(App):
    data = DictProperty(None)

    def build(self):
        self.load_data()
        Window.clearcolor = BG_COLOR
        
        sm = ScreenManager()
        sm.add_widget(PlanSelectScreen(name='plan_select_screen'))
        sm.add_widget(WorkoutPlanScreen(name='workout_plan_screen'))
        sm.add_widget(ExerciseCreationScreen(name='exercise_creation_screen'))
        sm.add_widget(ExerciseDetailScreen(name='exercise_detail_screen'))
        sm.add_widget(ActiveWorkoutScreen(name='active_workout_screen'))
        sm.add_widget(WorkoutSummaryScreen(name='workout_summary_screen'))
        sm.add_widget(StatisticsScreen(name='statistics_screen'))
        return sm

    def load_data(self):
        try:
            with open('data.json', 'r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {
                "plans": [], 
                "muscle_groups": ["None", "Chest", "Back", "Shoulders", "Biceps", "Triceps", "Quads", "Hamstrings", "Glutes", "Calves", "Abs"],
                "workout_sessions": []
            }
            self.save_data()
        
        if 'workout_sessions' not in self.data:
            self.data['workout_sessions'] = []
        for plan in self.data.get('plans', []):
            for ex in plan.get('exercises', []):
                if 'rest_time' not in ex:
                    ex['rest_time'] = 60
        self.save_data()


    def save_data(self):
        with open('data.json', 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_plan_name(self, plan_id):
        plan = next((p for p in self.data['plans'] if p['id'] == plan_id), None)
        return plan['name'] if plan else ''

    def delete_item(self, item_type, item_id, plan_id=None):
        if item_type == 'plan':
            # FIX: Also delete associated workout sessions
            self.data['plans'] = [p for p in self.data['plans'] if p['id'] != item_id]
            self.data['workout_sessions'] = [s for s in self.data['workout_sessions'] if s.get('plan_id') != item_id]
            if self.root.current == 'plan_select_screen':
                self.root.get_screen('plan_select_screen').populate_plans()
        
        elif item_type == 'exercise' and plan_id:
            for plan in self.data['plans']:
                if plan['id'] == plan_id:
                    plan['exercises'] = [e for e in plan['exercises'] if e['id'] != item_id]
                    break
            if self.root.current == 'workout_plan_screen':
                self.root.get_screen('workout_plan_screen').update_view()
        
        self.save_data()

if __name__ == '__main__':
    Builder.load_string(KV)
    GymApp().run()
