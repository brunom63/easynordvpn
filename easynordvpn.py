#!/usr/bin/env python


import subprocess
import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # type: ignore


class MyWindow(Gtk.ApplicationWindow):
    def __init__(self):
        super().__init__()

        self.nordvpn: dict[str, str] = {'Status': 'Disconnected'}

        self.notebook: Gtk.Notebook = Gtk.Notebook()
        self.disconnect_box: Gtk.Box = Gtk.Box(spacing=6)
        self.connection_status: Gtk.Label = Gtk.Label()
        self.disconnect_button: Gtk.Button = Gtk.Button.new_with_label("Disconnect")
        self.error_label: Gtk.Label = Gtk.Label()
        self.connect_button: Gtk.Button = Gtk.Button.new_with_label("Connect")
        self.connect_grid: Gtk.Grid = Gtk.Grid()
        self.status_grid: Gtk.Grid = Gtk.Grid()
        self.settings_grid: Gtk.Grid = Gtk.Grid()
        self.combo_groups: Gtk.ComboBoxText = Gtk.ComboBoxText()
        self.combo_countries: Gtk.ComboBoxText = Gtk.ComboBoxText()
        self.combo_cities: Gtk.ComboBoxText = Gtk.ComboBoxText()

        self.options = {}
        self.row_space = 14
        self.col_space = 40

        self.set_init()
        self.init()
        self.init_checkup()

    def set_init(self):
        self.connect("destroy", Gtk.main_quit)
        self.set_title("Easy NordVPN")
        self.set_border_width(3)
        self.set_position(Gtk.WindowPosition.CENTER)

    def init(self):
        win_scroll = Gtk.ScrolledWindow(propagate_natural_height=True,
                                        propagate_natural_width=True)
        self.add(win_scroll)

        win_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        win_scroll.add(win_box)

        win_box.add(self.disconnect_box)
        # win_box.add(self.error_label)
        self.notebook.set_vexpand(True)
        win_box.add(self.notebook)

        self.set_disconnect_box()
        self.set_connect_grid()
        self.set_status_grid()
        self.set_settings_grid()
        print('Init')

    def init_checkup(self):
        self.options = self.get_connect_options()
        for item in self.options['groups']:
            self.combo_groups.append_text(item)
        for item in self.options['countries']:
            self.combo_countries.append_text(item)
        print('Init Checkup')
        self.revalidate(is_init=True)

    def set_disconnect_box(self):
        self.disconnect_box.set_margin_top(self.row_space)
        self.disconnect_box.set_margin_bottom(self.row_space)
        self.connection_status.set_margin_top(10)
        self.connection_status.set_margin_bottom(10)
        self.disconnect_box.pack_start(self.connection_status, True, True, 10)
        self.disconnect_box.pack_start(self.disconnect_button, True, True, 50)

    def set_connect_grid(self):
        self.connect_grid.set_column_spacing(self.col_space)
        self.connect_grid.set_row_spacing(self.row_space)
        self.connect_grid.set_margin_top(self.row_space)
        self.connect_grid.set_margin_bottom(self.row_space)
        self.connect_grid.set_margin_start(self.row_space)
        self.connect_grid.set_margin_end(self.row_space)
        self.notebook.append_page(self.connect_grid, Gtk.Label(label="Connect"))
        self.connect_items_grid()

    def set_status_grid(self):
        self.status_grid.set_column_spacing(self.col_space)
        self.status_grid.set_row_spacing(self.row_space)
        self.status_grid.set_margin_top(self.row_space)
        self.status_grid.set_margin_bottom(self.row_space)
        self.status_grid.set_margin_start(self.row_space)
        self.status_grid.set_margin_end(self.row_space)
        self.notebook.append_page(self.status_grid, Gtk.Label(label="Status"))

    def set_settings_grid(self):
        self.settings_grid.set_column_spacing(self.col_space)
        self.settings_grid.set_row_spacing(self.row_space)
        self.settings_grid.set_margin_top(self.row_space)
        self.settings_grid.set_margin_bottom(self.row_space)
        self.settings_grid.set_margin_start(self.row_space)
        self.settings_grid.set_margin_end(self.row_space)
        self.notebook.append_page(self.settings_grid, Gtk.Label(label="Settings"))

    def revalidate(self, is_init=False):
        self.check_nordvpn()

        self.toggle_button_box()
        self.set_connect_toggle()
        self.status_box()
        self.settings_box()

        if is_init and self.is_connected():
            self.notebook.set_current_page(self.notebook.page_num(self.status_grid))

        self.show_all()
        print('Revalidate')

    def connect_items_grid(self):
        self.add_connect_row(0, "Groups",
                             self.combo_groups,
                             self.action_connect_groups)
        self.add_connect_row(1, "Countries",
                             self.combo_countries,
                             self.action_connect_countries)
        self.add_connect_row(2, "Cities",
                             self.combo_cities)
        self.add_connect_toggle()

    def toggle_button_box(self):
        if self.is_connected():
            self.disconnect_button.connect("clicked", self.disconnect_now)
            self.disconnect_button.set_no_show_all(False)
            self.connection_status.set_markup(
                "<span foreground=\"green\" size=\"large\">Connected!</span>")
        else:
            self.disconnect_button.set_no_show_all(True)
            self.disconnect_button.set_visible(False)
            self.connection_status.set_markup(
                "<span foreground=\"red\" size=\"large\">Not Connected</span>")

    def status_box(self):
        self.clear_grid(self.status_grid)
        for indx, (i_k, i_v) in enumerate(self.nordvpn.items()):
            self.add_status_row(indx, i_k, i_v)

    def settings_box(self):
        self.clear_grid(self.settings_grid)

        try:
            cmd = self.execute_command(['settings'])
        except Exception as e:
            self.settings_grid.attach(Gtk.Label(label=f"Error: {e}"), 0, 0, 1, 1)
            return

        n_sett = self.format_command(cmd)
        for indx, (i_k, i_v) in enumerate(n_sett.items()):
            form_widget = self.get_settings_form(i_k, i_v)
            if not form_widget:
                continue

            lbl = Gtk.Label(label=i_k, halign=Gtk.Align.START)
            lbl.set_hexpand(True)
            self.settings_grid.attach(lbl, 0, indx, 1, 1)
            form_widget.set_halign(Gtk.Align.END)

            self.settings_grid.attach_next_to(form_widget, lbl, Gtk.PositionType.RIGHT, 1, 1)

    def add_status_row(self, pos, i_k, i_v):
        lbl = Gtk.Label(label=i_k, halign=Gtk.Align.START)
        lbl.set_hexpand(True)
        self.status_grid.attach(lbl, 0, pos, 1, 1)

        vlab = Gtk.Label(label=i_v.replace(', ', "\n"))
        vlab.set_halign(Gtk.Align.END)
        vlab.set_justify(Gtk.Justification.RIGHT)

        self.status_grid.attach_next_to(vlab, lbl, Gtk.PositionType.RIGHT, 1, 1)

    def add_connect_row(self, pos: int, title: str, item_combo: Gtk.ComboBoxText, item_func=None):
        lbl = Gtk.Label(label=title, halign=Gtk.Align.START)
        lbl.set_hexpand(True)
        self.connect_grid.attach(lbl, 0, pos, 1, 1)

        if item_func is not None:
            item_combo.connect("changed", item_func)
        item_combo.append_text('')
        item_combo.set_entry_text_column(0)
        item_combo.set_halign(Gtk.Align.FILL)

        self.connect_grid.attach_next_to(item_combo, lbl, Gtk.PositionType.RIGHT, 1, 1)

    def add_connect_toggle(self):
        self.connect_grid.attach(self.connect_button, 0, 3, 2, 1)
        self.connect_button.connect("clicked", self.connection_new)

    def set_connect_toggle(self):
        self.connect_button.set_label("Reconnect" if self.is_connected() else "Connect")
        self.populate_combos()

    def check_nordvpn(self):
        try:
            cmd = self.execute_command(['status'])
            self.nordvpn = self.format_command(cmd)
        except Exception as e:
            self.nordvpn = {'Status': str(e)}

    def get_settings_form(self, f_key: str, f_val: str):
        f_skip = []  # ['Technology', 'Firewall Mark']
        f_bool, widg = {'enabled': True, 'disabled': False}, None
        if f_key in f_skip:
            return widg
        if f_val in f_bool:
            widg = Gtk.Switch()
            widg.set_active(f_bool[f_val])
            widg.connect("notify::active", self.action_settings_switch)
        else:
            widg = Gtk.Entry()
            widg.set_text(f_val)
            widg.set_editable(False)
            widg.set_alignment(1)
        widg.set_name(self.format_settings(f_key))
        return widg

    def connection_new(self, _):
        self.execute_command(self.new_connection())
        self.execute_command(['set', 'killswitch', 'on'])
        self.notebook.set_current_page(self.notebook.page_num(self.status_grid))
        self.revalidate()
    def disconnect_now(self, _):
        self.execute_command(['set', 'killswitch', 'off'])
        self.execute_command(['disconnect'])
        self.notebook.set_current_page(self.notebook.page_num(self.connect_grid))
        self.disconnect_button.disconnect_by_func(self.disconnect_now)
        self.revalidate()

    def populate_combos(self):
        if not self.is_connected():
            return
        if 'Country' in self.nordvpn:
            country = self.nordvpn['Country'].replace(' ', '_')
            if country in self.options["countries"]:
                self.combo_countries.set_active(
                    list(self.options["countries"].keys()).index(country) + 1)

                if 'City' in self.nordvpn:
                    city = self.nordvpn['City'].replace(' ', '_')
                    if city in self.options["countries"][country]:
                        self.combo_cities.set_active(
                            self.options["countries"][country].index(city) + 1)

    def action_connect_groups(self, _):
        self.combo_countries.set_active(0)

    def action_connect_countries(self, combo):
        item = combo.get_active_text()
        self.combo_cities.remove_all()
        self.combo_cities.append_text('')
        if item != "":
            if len(self.options['countries'][item]) == 0:
                self.options['countries'][item] = self.format_list(
                    self.execute_command(["cities", item]))
            for city in self.options['countries'][item]:
                self.combo_cities.append_text(city)

    def action_settings_switch(self, switch, _):
        self.execute_command(['set',
                              switch.get_name(),
                              'on' if switch.get_active() else 'off'])
        self.revalidate()

    def new_connection(self):
        opts = ["connect"]
        opts.extend(self.build_connection())
        return opts

    def build_connection(self):
        ret = []
        group, country, city = self.get_combos_values()
        if group is not None:
            ret.append('--group')
            ret.append(group)
        if country is not None:
            ret.append(country)
        if group is None and city is not None:
            ret.append(city)
        return ret

    def get_combos_values(self):
        group = self.combo_groups.get_active_text()
        country = self.combo_countries.get_active_text()
        city = self.combo_cities.get_active_text()
        return (
            None if not group else group,
            None if not country else country,
            None if not city else city
        )

    def get_connect_options(self):
        opts = {
            "countries": {},
            "groups": self.format_list(self.execute_command(["groups"]))
        }
        for cn in self.format_list(self.execute_command(["countries"])):
            opts['countries'][cn] = []
        return opts

    def is_connected(self):
        return self.nordvpn['Status'] == 'Connected'

    def set_error(self, msg):
        n_label = self.error_label.get_label()
        self.error_label.set_label(msg if n_label == "" else f'{n_label}\n{msg}')
        self.error_label.set_no_show_all(False)
        self.error_label.show_now()

    def clear_error(self):
        self.error_label.set_label("")
        self.error_label.set_no_show_all(True)
        self.error_label.show_now()

    @staticmethod
    def clear_grid(box):
        for item in box:
            item.destroy()

    # @staticmethod
    def execute_command(self, cmd: list):
        nord_cmd = ['nordvpn']
        nord_cmd.extend(cmd)
        proc = subprocess.run(nord_cmd, capture_output=True, check=False, text=True)
        if proc.stderr:
            raise Exception(proc.stderr)
        return str(proc.stdout)

    @staticmethod
    def format_command(cmd: str) -> dict:
        return {a[0]: a[1] for a in
                [item.split(': ') for item in cmd.split("\n") if ': ' in item]}

    @staticmethod
    def format_list(cmd: str) -> list:
        ccd = re.sub(r'\s{2,}|\t{1,}|\r?\n{1,}', ',', cmd.strip()).strip()
        fin = [c.strip() for c in ccd.split(',')]
        return sorted(fin) if len(fin) > 0 else [cmd]

    @staticmethod
    def format_settings(name: str):
        if name == 'Firewall Mark':
            ret = 'fwmark'
        elif name == 'Lan Discovery':
            ret = 'lan-discovery'
        else:
            ret = name.lower().replace('-', '').replace(' ', '')
        return ret


def main():
    MyWindow()
    Gtk.main()


if __name__ == '__main__':
    main()
