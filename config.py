# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from types import NoneType
from libqtile import bar, layout, widget, hook, qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras import widget
import subprocess, os,time

#NOTE: Helper Functions

# given an application name, search the current group's window list for that application name
# if found return 1, else return 0
# not working, seems to only run the conidtional that i put in the keybind when the config is reloaded (line 109)
def app_in_group(app: str):
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
    # check if current group has any windows, note i don't think that there is a "current" group in general, there may be one for each screen
        # could do this with group.info()
    # if not spawn an application

# checks if an application is open anywhere, if not opens it, if it is goes to it
# def get_current_group():
#     return qtile.current_screen.group

# def find_or_run_current_group(app, wm_class):
#     current_group = get_current_group()
#     current_group = current_group.name
#     f = open("/home/dahle/Desktop/Personal/qtile.txt","w")
#     f.write("hello there")
#     f.write(str(current_group))
#     f.close()
#     return find_or_run_group_based(app, wm_class, current_group)

# if an application is not in the specified group, go to that group and open the application, otherwise go to that group and focus that application
#TODO: Would like to add a mouse warping feature
# you can find the wm_class by using the xprop command in terminal
def find_or_run_group_based(app, wm_class,group_name):

    def __inner(qtile):

        # # Get the window objects from windows_map
        for window in qtile.groups_map[group_name].windows:

            # Check if the window matches your desired class
            if hasattr(window, "cmd_match") and window.cmd_match(Match(wm_class=wm_class)):

                # Switch to the group where the window is
                qtile.current_screen.set_group(window.group)

                # Focus the window
                #WARNING: I don't know if this value should be true or false, i switched it to true
                window.focus(True)
                return

        # If we're here, the app wasn't found in the group name, so switch to that screen and spawn it
        # qtile.current_screen.toggle_group(qtile.groups_map[group_name])
        qtile.current_screen.set_group(qtile.groups_map[group_name])
        qtile.cmd_spawn(app)

    return __inner

# https://www.reddit.com/r/qtile/comments/tmsgf8/custom_function_help_run_or_raise_application/
def find_or_run(app, wm_class):
    def __inner(qtile):

        # Get the window objects from windows_map
        for window in qtile.windows_map.values():

            # Check if the window matches your desired class
            if hasattr(window, "cmd_match") and window.cmd_match(Match(wm_class=wm_class)):

                # Switch to the group where the window is
                qtile.current_screen.set_group(window.group)

                # Focus the window
                window.focus(False)

                # Exit the function
                return

        # If we're here, the app wasn't found so we launch it
        qtile.cmd_spawn(app)

    return __inner

#NOTE: Keybindings

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
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
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
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    # Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    # Key([mod], "r", lazy.spawn("rofi -theme mysidebar.rasi -show drun")),
    Key([mod], "Backslash", lazy.spawn("rofi -theme mysidebar.rasi -show window")),
    Key([],"F4", lazy.spawn("rofi -theme mysidebar.rasi -show drun")),
    Key([],"F8", lazy.spawn("rofi -theme mysidebar.rasi -show window")),
    Key([mod], "f", lazy.window.toggle_floating()),
    # this is for a widget to call
    Key([mod, "control", "mod1"], "a", lazy.group["5"].toscreen(), lazy.spawn("discord")),
    # open firefox if not found in current group, called by widget
    # Key([mod, "control", "mod1"], "b", lazy.spawn(terminal) if(app_in_group("firefox") is 1) else lazy.spawn("firefox")),
    Key([mod, "control", "mod1"], "b", lazy.function(find_or_run_group_based("thunderbird","thunderbird", "4"))),
    Key([mod, "control", "mod1"], "c", lazy.function(find_or_run_group_based("code","code-oss", "2"))),
    Key([mod], "t", lazy.function(find_or_run_group_based("firefox","firefox", "2"))),
    # Key([mod], "b", lazy.function(find_or_run_current_group("firefox","firefox"))),
]
# to swith back to last group
def latest_group(qtile):
    qtile.current_screen.set_group(qtile.current_screen.previous_group)

keys += [Key([mod], "p", lazy.function(latest_group))]

#HACK: move_next_screen2(), cool function that when called swaps the groups on screens

# def warp_cursor_here_win(win):
#     if win is not None:
#         win.window.warp_pointer(win.width // 2, win.height // 2)

# def move_next_screen2():
#     @lazy.function
#     def _move_next_screen2(qtile):
#         if len(qtile.screens) != 2: return
#         i = qtile.screens.index(qtile.current_screen)
#         j = 0 if i == 1 else 1

#         if qtile.current_group:
#             group = qtile.current_group
#             # logger.warning(f'Move group "{group.name}" from screen {i}->{j}')
#             qtile.focus_screen(j)
#             time.sleep(2)
#             group.cmd_toscreen()
#             warp_cursor_here_win(group.current_window)
#             time.sleep(2)

#     return _move_next_screen2

#NOTE: Groups
group_names = [
   ("1", {"label": ""}), # Hack Nerd Font
   ("2", {"label": ""}), # Hack Nerd Font
   ("3", {"label": "•"}), # Hack Nerd Font
   ("4", {"label": "󰨲"}), # Hack Nerd Font
   ("5", {"label": "󰙯"}), # Hack Nerd Font
   ("6", {"label": "•"}), # Hack Nerd Font
   ("7", {"label": "•"}), # Not Sure, but was from a nerd font
   ("8", {"label": "•"}), # Hack Nerd Font
   ("9", {"label": "•"}), # Hack Nerd Font
   ("0", {"label": "•"}), # Hack Nerd Font
   # ("1",  {"label": ""}),
   # ("2 ", {"label": ""}),
   # ("3 ", {"label": ""}),
   # ("4 ", {"label": ""}),
   # ("5 ", {"label": ""}),
   # ("6 ", {"label": ""}),
   # ("7 ", {"label": ""}),
   # ("8 ", {"label": ""}),
   # ("9 ", {"label": ""}),
   # ("1",  {"label": ""}),
   # ("2 ", {"label": ""}),
   # ("3 ", {"label": ""}),
   # ("4 ", {"label": ""}),
   # ("5 ", {"label": ""}),
   # ("6 ", {"label": ""}),
   # ("7 ", {"label": ""}),
   # ("8 ", {"label": ""}),
   # ("9 ", {"label": ""}),
   # ("1",  {"label": "ﯶ"}),
   # ("2 ", {"label": "ﯶ"}),
   # ("3 ", {"label": "ﯶ"}),
   # ("4 ", {"label": "ﯶ"}),
   # ("5 ", {"label": "ﯶ"}),
   # ("6 ", {"label": "ﯶ"}),
   # ("7 ", {"label": "ﯶ"}),
   # ("8 ", {"label": "ﯶ"}),
   # ("9 ", {"label": "ﯶ"}),
   # ("1",  {"label": ""}),
   # ("2 ", {"label": ""}),
   # ("3 ", {"label": ""}),
   # ("4 ", {"label": ""}),
   # ("5 ", {"label": ""}),
   # ("6 ", {"label": ""}),
   # ("7 ", {"label": ""}),
   # ("8 ", {"label": ""}),
   # ("9 ", {"label": ""}),
]

#HACK: Hack For Groups
codeoss_wn = 2
discord_wn = 6
groups = [Group(name, **kwargs) for name, kwargs in group_names]
for g in groups:
    keys.append(
        Key([mod], g.name, lazy.group[g.name].toscreen())
    )
    keys.append(
        Key([mod, "shift"], g.name, lazy.window.togroup(g.name))
    )

# for i, (name, kwargs) in enumerate(group_names, 1):
#     # mod1 + letter of group = switch to group
#     keys.append(
#         Key([mod], str(i), lazy.group[name].toscreen())
#     )
#     # mod1 + shift + letter of group = switch to & move focused window to group
#     keys.append(
#         Key([mod, "shift"], str(i), lazy.window.togroup(name))
#     )


# groups = [Group(i) for i in "123456789"]

# for i in groups:
#     keys.extend(
#         [
#             # mod1 + letter of group = switch to group
#             Key(
#                 [mod],
#                 i.name,
#                 lazy.group[i.name].toscreen(),
#                 desc="Switch to group {}".format(i.name),
#             ),
#             # mod1 + shift + letter of group = switch to & move focused window to group
#             Key(
#                 [mod, "shift"],
#                 i.name,
#                 lazy.window.togroup(i.name, switch_group=True),
#                 desc="Switch to & move focused window to group {}".format(i.name),
#             ),
#             # Or, use below if you prefer not to switch to that group.
#             # # mod1 + shift + letter of group = move focused window to group
#             # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
#             #     desc="move focused window to group {}".format(i.name)),
#         ]
#     )

#NOTE: Layouts
layouts = [
    layout.Columns(margin_on_single=6, insert_position=1, border_focus_stack=["#a68fdb"],border_focus="#a68fdb",border_normal="#14023b", border_width=4, margin=6),
    # layout.MonadTall(border_focus="#edd6ff",border_normal="#14023b", border_width=4, margin=4),
    layout.Max(border_focus="#a68fdb",border_normal="#14023b",border_width=6, margin=6),
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


#HACK: My Colors
barscaler = 18
widget_defaults = dict(
    font="sans",
    fontsize=barscaler,
    padding=3,
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

# for some reason this script isn't working, refer to script
# def my_func():
#     script = os.path.expanduser('/home/dahle/Desktop/Scripts/test.sh')
#     subprocess.call(script)

#TODO: get this working
# i can't seem to figure out how to move to a screen based on a widget inside a function, if i can do this i can have a function
# that would switch to my "firefox" screen and then spawn a firefox instance
# widget.TextBox(text="a",fontsize=30,**decor_green, mouse_callbacks={"Button1": try_again()}),
def try_again():
    qtile.cmd_spawn("firefox")
    qtile.cmd_spawn("anki")


    # for window in group.info.windows:
    #   if app is a substring of window
    #       stop 
    # spawn app
    return  # placeholder

#NOTE: Screens
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.GroupBox(
                    hide_unused=False,
                    highlight_color = ['282828', 'a888f7'], # Active group highlight color when using 'line' highlight method. Gradient when two colors
                    fontsize=30,
                    active='FFFFFF', # color that active windows make the text
                    borderwidth=1,
                    highlight_method='line',
                    inactive='#666565', # color that inactive windows make the text
                    # this_current_screen_border='#714acf',
                    this_current_screen_border='#a888f7', # border or line color for group on this screen when unfocused
                    other_current_screen_border='#a68fdb',
                    other_screen_border='#FFFFFF',
                    this_screen_border='#a68fdb',


                    ),
                widget.Sep(),
                widget.CurrentLayout(**decor_pink),
                widget.Sep(linewidth=2),
                widget.TextBox(text="",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.spawn("firefox")}),
                widget.TextBox(text="",fontsize=30,**decor_green, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/builds/tor-browser/qtile-tor-script.sh")}),
                # widget.TextBox(text="󰕷",fontsize=30,**decor_green, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn([terminal, "-e", "nvim"])}),
                widget.TextBox(text="󰕷",fontsize=30,**decor_green, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("neovide")}),
                widget.TextBox(text="󰙯",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod,"control","mod1"],"a")}),
                widget.TextBox(text="󰨞",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod, "control","mod1"], "c")}),
                widget.TextBox(text="󰨲",fontsize=30,**decor_green, mouse_callbacks={"Button1": lazy.simulate_keypress([mod,"control","mod1"],"b")}),
                widget.TextBox(text="󰍺",fontsize=30,**decor_green2, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/Desktop/Scripts/Monitor-Left.sh")}),
                widget.TextBox(text="󰌵",fontsize=30,**decor_green2, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/Desktop/Scripts/redshift_clear.sh")}),
                widget.TextBox(text="󱩌",fontsize=30,**decor_green2, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/Desktop/Scripts/redshift_low.sh")}),
                widget.TextBox(text="󱩍",fontsize=30,**decor_green2, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/Desktop/Scripts/redshift_high.sh")}),
                widget.Prompt(),
                # widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                # widget.TextBox("default config", name="default"),
                # widget.TextBox("Press &lt;M-r&gt; to spawn", foreground="#d75f5f"),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
                widget.Spacer(),
                widget.Battery(
                    format='{char} {percent:2.0%} {hour:d}:{min:02d}',
                    **decor_pink,
                    ),
                widget.ThermalZone(**decor_pink),
                widget.TextBox(text="󰍶",fontsize=30,**decor_pink2, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/Desktop/Scripts/poweroff.sh")}),
                widget.TextBox(text="󰤄",fontsize=30,**decor_pink2, mouse_callbacks={"Button1": lambda: qtile.cmd_spawn("sh /home/dahle/Desktop/Scripts/sleep.sh")}),
                widget.Sep(linewidth=2),
                widget.Systray(),
                widget.Sep(linewidth=2),
                widget.CheckUpdates(distro='Arch', no_update_string='Update: 0', **decor_green),
                widget.Volume(**decor_green),
                widget.Sep(linewidth=2),
                widget.Clock(format="%Y-%m-%d    %I:%M %p",  **decor_purp),
            ],
            2*barscaler,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
            background='#3a383d',
        ),

        # right=bar.Gap(10),
        # left=bar.Gap(10),
        # bottom=bar.Gap(10)

    ),
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
    border_focus = "a68fdb",border_normal="#14023b",border_width=6
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
