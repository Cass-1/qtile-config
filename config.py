from types import NoneType
from libqtile import bar, layout, widget, hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras import widget
import subprocess, os,time
from libqtile.utils import send_notification   # e.g. send_notification("qtile", "Startup") will send the notification *qtile*\n "startup"

# can't use hexidecimals w/ 0x bc it is different than the hexidecimal colors that start with #

# my fav color scheme
# accent_color = "#a68fdb"  # light purple
# secondary_accent_color = "#D17B8C" # maroonish pink (goes with purple)
# secondary_accent_color_dif = "#D17B8D" # maroonish pink (goes with purple)

accent_color = "#758D72"  # gray purple
secondary_accent_color = "#8A728D"  # mint
secondary_accent_color_dif = "#8A728E"  # mint

time_and_date_color = accent_color
power_color = secondary_accent_color
power_color2 = secondary_accent_color_dif

def get_current_group():
    """
    returns the name of the current group
    """
    return qtile.current_screen.group

# NOTE: Lazy functions or functions that call lazy functions are given the qtile argument, thats why i was
# getting find_or_run_current_group() takes 2 positional arguments but 3 were given
# NOTE: This code was partially inspired by https://www.reddit.com/r/qtile/comments/tmsgf8/custom_function_help_run_or_raise_application/
@lazy.function
def open_solitary_instance(qtile, app_name, wm_class, group_name=None):
    """
    opens a solitary instance of an application in the specified group, if no group is specified the current group is used
    Switches to specified group and if it is not open in that group, open it and focus it, if that application is open focus it
    TODO: The focusing on the window does work, but the highlight indicated doesn't change, I think I need a mouse warp to do this
    """

    # gets the current group
    if (group_name is None):
        current_group = get_current_group().name
    else:
        current_group = group_name

    # loops through the windows in the current group
    for window in qtile.groups_map[current_group].windows:

        # Check if the window matches your desired class
        if hasattr(window, "match") and window.match(Match(wm_class=wm_class)):

            # Switch to the group where the window is
            qtile.current_screen.set_group(window.group)

            # Focus the window.
            window.focus(True)

            return

    # If we're here, the app wasn't found in the group name, so switch to that group and spawn it
    qtile.current_screen.set_group(qtile.groups_map[current_group])
    qtile.spawn(app_name)

# to swith back to last group
def latest_group(qtile):
    qtile.current_screen.set_group(qtile.current_screen.previous_group)

@lazy.function
def latest_group_lazy(qtile):
    qtile.current_screen.set_group(qtile.current_screen.previous_group)

def remove_string(text):
    return ""

@lazy.function
def open_in_group(qtile, app_name, group=None):
    if group is None:
        group = get_current_group().name
    qtile.current_screen.set_group(qtile.groups_map[group])
    qtile.spawn(app_name)

# from the qtile FAQ
def go_to_group(name: str):
    def _inner(qtile ) -> None:
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return

        # the target group
        group = qtile.groups_map[name]

        # the index of the target group's prefered screen in the screens list
        num = qtile.groups_map[name].screen_affinity

        # save the index of the screen before the move to the target group
        old_screen_index = qtile.current_screen.index

        # set the screen
        qtile.screens[num].set_group(group)
        qtile.focus_screen(n=num, warp=True)

        # warp to screen always recenters the mouse, this way the mouse is only recentered
        # when changing screens
        if num is not old_screen_index:
            qtile.warp_to_screen()

    return _inner

@lazy.function
def lock_screen(qtile):
    qtile.spawn("sh /home/dahle/.config/qtile/scripts/i3lock-pixilate.sh")

@lazy.function
def toggle_group(qtile, group_name):
    if get_current_group().name is group_name:
        # go to previous group
        latest_group(qtile)
    else:
        # go to group
        qtile.groups_map[group_name].toscreen()

@lazy.function
def open_app_group_toggle(qtile, app_name, app_wmclass, group_name):
    """
        toggles back and forth between a specific group and opens an app in that group
        if that app is not already open
    """
    if get_current_group().name is group_name:
        # go to previous group
        # return lazy.function(lambda qtile: qtile.current_screen.set_group(qtile.current_screen.previous_group))
        latest_group(qtile)
    else:
        # go to group
        # loops through the windows in the current group
        for window in qtile.groups_map[group_name].windows:

            # Check if the window matches your desired class
            if hasattr(window, "match") and window.match(Match(wm_class=app_wmclass)):

                # Switch to the group where the window is
                qtile.current_screen.set_group(window.group)

                # Focus the window.
                window.focus(True)

                return

        # If we're here, the app wasn't found in the group name, so switch to that group and spawn it
        qtile.current_screen.set_group(qtile.groups_map[group_name])
        qtile.spawn(app_name)

# given an application name, search the current group's window list for that application name
# if found return 1, else return 0
# not working, seems to only run the conidtional that i put in the keybind when
# the config is reloaded (line 109)
def app_in_group(qtile, app: str):
    # f = open("/home/dahle/Desktop/Personal/qtile.txt","a")
    group_windows = qtile.current_screen.group.info()['windows']
    # f.write(str(len(group_windows)))
    for window in group_windows:
        if window is not None and app in window.lower():
            # f.write("fond ya")
            # f.close()
            qtile.cmd_spawn(app)
    # f.write("didn't finda ya")
    # f.close()
    qtile.cmd_spawn(terminal)

def warp_cursor_here_win(win):
    if win is not None:
        win.window.warp_pointer(win.width // 2, win.height // 2)

# https://www.reddit.com/r/qtile/comments/tmsgf8/custom_function_help_run_or_raise_application/
def find_or_run(app, wm_class):
    """
    Checks if an application is open in any of the windows, if it is focus the applicaiton, otherwise open the application.
    """
    def __inner(qtile):

        # Get the window objects from windows_map
        for window in qtile.windows_map.values():

            # Check if the window matches your desired class
            if hasattr(window, "match") and window.match(Match(wm_class=wm_class)):

                # Switch to the group where the window is
                qtile.current_screen.set_group(window.group)

                # Focus the window
                window.focus(False)

                # Exit the function
                return

        # If we're here, the app wasn't found so we launch it
        qtile.cmd_spawn(app)

    return __inner

#HACK: move_next_screen2(), cool function that when called swaps the groups on screens
def move_next_screen2():
    @lazy.function
    def _move_next_screen2(qtile):
        if len(qtile.screens) != 2: return
        i = qtile.screens.index(qtile.current_screen)
        j = 0 if i == 1 else 1

        if qtile.current_group:
            group = qtile.current_group
            # logger.warning(f'Move group "{group.name}" from screen {i}->{j}')
            qtile.focus_screen(j)
            time.sleep(2)
            group.cmd_toscreen()
            warp_cursor_here_win(group.current_window)
            time.sleep(2)

    return _move_next_screen2

mod = "Mod4"
terminal = guess_terminal()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html

    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    # Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod],
        "s",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),

    # Qtile
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),

    # Rofi
    Key([mod], "Backslash", lazy.spawn("rofi -theme mysidebar.rasi -show window")),
    Key([],"F4", lazy.spawn("rofi -theme mysidebar.rasi -show drun")),
    Key([],"F10", lazy.spawn("rofi -theme mysidebar.rasi -show window")),

    # App launchers
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "w", open_in_group("firefox","2")),
    # Key([mod], "Space", open_solitary_instance("discord","discord","4")),
    Key([mod], "Space", open_app_group_toggle("discord", "discord", "4")),
    Key([mod], "e", lazy.spawn("emacsclient -c -a ''")),


    # Screen navigation
    # Key([mod], "Backspace", lazy.function(go_to_group("5"))),
    Key([mod], "Backspace", toggle_group("5")),
    Key([mod], "p", lazy.function(latest_group)),

    # Window commands
    Key([mod], "f", lazy.window.toggle_floating()),
    Key([mod, "shift"], "tab", lazy.window.toggle_fullscreen()),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

    # Bar slider toggle
    Key([mod], "t", lazy.widget["tool_widgetbox"].toggle()),
    Key([mod], "o", lazy.widget["user_options_widgetbox"].toggle()),

    # Lock screen
    Key([mod, "mod1"], "l", lock_screen()),

    # Media keys
    Key([], "XF86AudioRaiseVolume", lazy.spawn("amixer -D pulse sset Master 5%+"), desc="Increace Volume by 5%"),
    Key([], "XF86AudioLowerVolume", lazy.spawn("amixer -D pulse sset Master 5%-"), desc="Decrease Volume by 5%"),
    Key(["shift"], "XF86AudioRaiseVolume", lazy.spawn("amixer -D pulse sset Master 1%+"), desc="Increace Volume by 1%"),
    Key(["shift"], "XF86AudioLowerVolume", lazy.spawn("amixer -D pulse sset Master 1%-"), desc="Decrease Volume by 1%"),
    Key([], "XF86AudioMute", lazy.spawn("amixer -D pulse sset Master toggle"), desc="Toggle Volume"),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 10%-"), desc="Decreace brightness by 10%"),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set 10%+"), desc="Increace brightness by 10%"),
]

groups = [
    # Screen affinity here is used to make
    # sure the groups startup on the right screens
    Group(name="1", label="prim", screen_affinity=0),
    Group(name="2", label="www", screen_affinity=0),
    Group(name="3", label="term", screen_affinity=0),
    Group(name="4", label="comm", screen_affinity=0),
    Group(name="5", label="extra", screen_affinity=0, spawn="thunderbird"),
    Group(name="0", label="scrn", screen_affinity=1),
]


for i in groups:
    keys.append(Key([mod], i.name, lazy.function(go_to_group(i.name))))
    # keys.append(Key([mod], i.name, lazy.group[i.name].toscreen()))
    keys.append(Key([mod, "shift"], i.name, lazy.window.togroup(i.name)))

# fun color (mint): #B4F8C8
layouts = [
    layout.Columns(name="colums-m", border_focus_stack=[accent_color],border_focus=accent_color,border_width=1),
    # layout.MonadTall(border_focus="#edd6ff",border_normal="#14023b", border_width=4, margin=4),
    # layout.Max(border_focus="#a68fdb",border_normal="#14023b",border_width=6, margin=6),
    layout.Max(),
    # layout.Columns(margin_on_single=6, insert_position=1, border_focus_stack=[accent_color],border_focus=accent_color,border_normal=accent_color, border_width=4, margin=6),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

#NOTE: Floating Layouts
# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class="yad")  # yad
    ],
    border_focus = accent_color,border_normal=accent_color,border_width=6
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"


# Don't use tweak_float in a client_new hook. It will crash qtile.
#window.tweak_float(x=660, y=400, w=600, h=20)
# fix to get plank working
# https://forum.garudalinux.org/t/qtile-and-plank-doesnt-work-well-together/19891/5
# @hook.subscribe.startup_once
# def plank_start():
#     subprocess.Popen(["/home/dahle/.local/bin/plank-launcher", "start"])

# @hook.subscribe.client_new
# def plank_reload(_window):
#     subprocess.Popen(["/home/dahle/.local/bin/plank-launcher", "show"])

# when a new window is made, go to that window
# @hook.subscribe.group_window_add
# def switchtogroup(group, window):
#   group.cmd_toscreen()

barscaler = 18

widget_defaults = dict(
    font= "Hack",
    fontsize=20 ,
)

extension_defaults = widget_defaults.copy()

decor_purp = {
    "decorations": [
        RectDecoration(colour="#957bd1", radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding": barscaler/1.7142,
}
decor_pink = {
    "decorations": [
        RectDecoration(colour='#D17B8C', radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}
# the pink2 color is slightly changed so icons in it will have their own group
# if the color is the same as pink it is treated as the same gruop as pink
decor_pink2 = {
    "decorations": [
        RectDecoration(colour='#D17B8B', radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}
decor_green = {
    "decorations": [
        RectDecoration(colour='#83A439', radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}
decor_green2 = {
    "decorations": [
        RectDecoration(colour='#83A438', radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}
decor_gray = {
    "decorations": [
        RectDecoration(colour='#9B9B9B', radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}

decor_time_and_date= {
    "decorations": [
        RectDecoration(colour=time_and_date_color, radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding": barscaler/1.7142,
}

decor_power= {
    "decorations": [
        RectDecoration(colour=power_color, radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}

# if i want two same colored blocks next to eachother but don't want those two blocks to connect
decor_power2= {
    "decorations": [
        RectDecoration(colour=power_color2, radius=3, filled=True, padding=barscaler/4, group=True)
    ],
    "padding":  barscaler/1.7142,
}

widget_app_bar = widget.WidgetBox(fontshadow= "888888", text_closed='', text_open='',widgets=[widget.TaskList(parse_text=remove_string, border="3a383d" )])
clock_widget = widget.Clock(format="%Y-%m-%d    %I:%M %p",  **decor_time_and_date,font= "Hack")

groupbox_widget= widget.GroupBox(
                    hide_unused=False,
                    highlight_color = ['282828'], # Active group highlight color when using 'line' highlight method. Gradient when two colors
                    fontsize=15,
                    center_aligned=False,
                    active='FFFFFF', # color that active windows make the text
                    borderwidth=4,
                    margin_y = 2,
                    highlight_method='line',
                    inactive='#666565', # color that inactive windows make the text
                    # this_current_screen_border='#714acf',
                    # this_current_screen_border='#a888f7', # border or line color for group on this screen when unfocused
                    this_current_screen_border = accent_color,
                    other_current_screen_border= accent_color,
                    other_screen_border='#FFFFFF',  # screen boarder when unfocused
                    this_screen_border='#FFFFFF',  # screen boarder when unfocused
                    )


tool_widgetbox = widget.WidgetBox(name="tool_widgetbox",close_button_location='right', text_closed='', text_open='', widgets = [
                    widget.Pomodoro(fontsize=15,color_inactive="FFFFFF", color_active="FFFFFF", color_break="FFFFFF"),
                    widget.TextBox(text="󰍺",fontsize=30, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/Monitor-Left.sh")}),
                    widget.TextBox(text="󰌵",fontsize=30, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/redshift_clear.sh")}),
                    widget.TextBox(text="󱩌",fontsize=30, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/redshift_low.sh")}),
                    widget.TextBox(text="󱩍",fontsize=30, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/redshift_high.sh")}),
                    widget.Sep(linewidth=2),
                ])

user_options_widgetbox = widget.WidgetBox(name="user_options_widgetbox",close_button_location='right', text_closed='', text_open='', widgets = [
                            widget.Sep(linewidth=2),
                            widget.TextBox(text="󰍶",fontsize=30, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/poweroff.sh")}),
                            widget.TextBox(text="",fontsize=15, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/reboot.sh")}),
                            widget.TextBox(text="󰤄",fontsize=30, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/Desktop/Scripts/sleep.sh")}),
                            widget.TextBox(text="󰗽",fontsize=30, mouse_callbacks={"Button1": lazy.shutdown()}),
                            widget.TextBox(text="󰌾",fontsize=30, mouse_callbacks={"Button1": lock_screen()}),
                            widget.Sep(linewidth=2),
                        ])

screen0 = Screen(
        top=bar.Bar(
            [
                groupbox_widget,
                widget.CurrentLayout(fontsize=15),
                # widget.Sep(),
                # widget_script_box,
                # widget.Sep(),
                # widget.Sep(linewidth=2),
                # widget.TextBox(text="",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod, "control", "mod1"], "d")}),
                # widget.TextBox(text="",fontsize=30,**decor_green, mouse_callbacks={"Button1": lambda: qtile.spawn("sh /home/dahle/builds/tor-browser/qtile-tor-script.sh")}),
                # # widget.TextBox(text="󰕷",fontsize=30,**decor_green, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn([terminal, "-e", "nvim"])}),
                # widget.TextBox(text="",fontsize=30,**decor_green, mouse_callbacks={"Button1": lambda: qtile.spawn("emacsclient -c -a '' ")}),
                # widget.TextBox(text="󰙯",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod,"control","mod1"],"a")}),
                # widget.TextBox(text="󰨞",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod, "control","mod1"], "c")}),
                # widget.TextBox(text="󰨲",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod,"control","mod1"],"b")}),
                widget_app_bar,
                widget.Spacer(),
                widget.Battery(
                    format='{char} {percent:2.0%} ({hour:d}:{min:02d})',
                    **decor_power,
                    ),
                # widget.BatteryIcon(theme_path="/home/dahle/.icons/qtile/battery/"),
                widget.ThermalZone(**decor_power2),
                widget.Sep(linewidth=2),
                tool_widgetbox,
                user_options_widgetbox,
                # widget.WidgetBox(widgets=[
        # ]),
                widget.Systray(),
                widget.Sep(linewidth=2),
                clock_widget,
            ],
            2*barscaler,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
            background='#3a383d',
        ),

        # right=bar.Gap(10),
        # left=bar.Gap(10),
        # bottom=bar.Gap(10)

    )

screen1 = Screen(
    # bar
    top=bar.Bar([
        groupbox_widget,
        widget.Spacer(),
        clock_widget,
    ],
    2*barscaler,
    background='#3a383d',
    )

)

screens = [screen0, screen1]

@hook.subscribe.startup_once
def autostart():
    """Run at Qtile start"""
    # run my startup script
    startup = os.path.expanduser('~/Desktop/Scripts/startup.sh')
    subprocess.Popen([startup])

    # PROCESSES THAT DON'T WORK IN STARTUP SCRIPT
    # run the volume icon applet
    volume_icon = os.path.expanduser('~/Desktop/Scripts/volume.sh')
    subprocess.Popen([volume_icon])

    # start the emacs daemon
    emacs_daemon = os.path.expanduser('~/Desktop/Scripts/emacs_daemon.sh')
    subprocess.Popen([emacs_daemon])


@hook.subscribe.startup
def run_every_startup():
    send_notification("qtile", "Startup")


    # opens the application tray
    widget_app_bar.toggle()

unlocked = True

@hook.subscribe.resume
def lock_screen():
    global unlocked
    unlocked = True

@hook.subscribe.suspend
def lock_sceen():
    global unlocked
    if unlocked:
        qtile.spawn("sh /home/dahle/.config/qtile/scripts/i3lock-pixilate.sh")
        unlocked = False
    # qtile.spawn("firefox");
    # qtile.spawn("sh /home/dahle/.config/qtile/scripts/i3lock-pixilate.sh")
