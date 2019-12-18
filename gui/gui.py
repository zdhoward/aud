import PySimpleGUIQt as sg
from layouts import menu_def, layout

# https://pbaumgarten.com/python/gui-with-pysimplegui.html

window = None
tray = None
theme = "GreenMono"  # "Topanga" #"Dark Amber"


def create_window():
    global window
    global theme

    window_pos_x, window_pos_y = (0, 0)
    if window != None:
        window_size_x, window_size_y = window.Size
        window_pos_x, window_pos_y = window.CurrentLocation()
        window.close()
        del window

    sg.change_look_and_feel(theme)
    window = sg.Window("aud", layout, location=(window_pos_x, window_pos_y - 29))
    # window.VisibilityChanged()
    return True


def create_system_tray_entry():
    global tray
    menu_def = [
        "BLANK",
        ["&Open", "---", "&Save", ["1", "2", ["a", "b"]], "&Properties", "E&xit"],
    ]
    tray = sg.SystemTray(menu=menu_def, filename=r"default_icon.ico")


def process_input():
    global window
    global tray
    global theme

    def process_window():
        global window
        global theme
        event, values = window.read()
        print("Event:", event)
        print("Values:", values)
        if event in (None, "Cancel", "Exit"):  # if user closes window or clicks cancel
            exit()
        elif event == "About":
            sg.Popup("About this software.")
        elif event == "_config_set_extensions_":
            ext_string = sg.PopupGetText("Extensions (separated by commas)")
            exts = ext_string.lower().replace(" ", "").replace(".", "").split(",")
            ## set extensions
        elif event == "_config_set_whitelist_":
            whitelist_string = sg.PopupGetText("Whitelist Files (separated by commas)")
            whitelist = whitelist_string.split(",")
            ## set whitelist
        elif event == "_config_set_blacklist_":
            blacklist_string = sg.PopupGetText("Blacklist Files (separated by commas)")
            blacklist = blacklist_string.split(",")
            ## set blacklist
        elif event == "_config_set_logfile_":
            logfile = sg.PopupGetText("Logfile", default_text=values["_selected_dir_"])
            ## set logfile
        elif event == "_backup_location_":
            if values[event]:
                sg.Popup(values[event])
            # run backup
        elif event == "_move_location_":
            if values[event]:
                sg.Popup(values[event])
            # run move
        elif event == "_copy_location_":
            if values[event]:
                sg.Popup(values[event])
            # run copy
        elif event == "_zip_location_":
            if values[event]:
                sg.Popup(values[event])
            # run zip
        elif event.find("::"):
            if event.split("::")[1].startswith("_change_theme_"):
                theme = event.split("::_change_theme_")[1]
                create_window()
            elif event.split("::")[1].startswith("_tools_"):
                if event.split("::_tools")[1] == "_afx_":
                    window.FindElement("_frm_tools_afx_").Update(visible=True)
                    window.FindElement("_frm_tools_name_").Update(visible=False)
                    window.FindElement("_frm_tools_convert_").Update(visible=False)
                    window.FindElement("_frm_tools_export_").Update(visible=False)
                    window.VisibilityChanged()
                    pass
                elif event.split("::_tools")[1] == "_name_":
                    window.FindElement("_frm_tools_afx_").Update(visible=False)
                    window.FindElement("_frm_tools_name_").Update(visible=True)
                    window.FindElement("_frm_tools_convert_").Update(visible=False)
                    window.FindElement("_frm_tools_export_").Update(visible=False)
                    window.VisibilityChanged()
                    pass
                elif event.split("::_tools")[1] == "_convert_":
                    window.FindElement("_frm_tools_afx_").Update(visible=False)
                    window.FindElement("_frm_tools_name_").Update(visible=False)
                    window.FindElement("_frm_tools_convert_").Update(visible=True)
                    window.FindElement("_frm_tools_export_").Update(visible=False)
                    window.VisibilityChanged()
                    pass
                elif event.split("::_tools")[1] == "_export_":
                    window.FindElement("_frm_tools_afx_").Update(visible=False)
                    window.FindElement("_frm_tools_name_").Update(visible=False)
                    window.FindElement("_frm_tools_convert_").Update(visible=False)
                    window.FindElement("_frm_tools_export_").Update(visible=True)
                    window.VisibilityChanged()
                    pass
        else:
            print("EVENT NOT FOUND: ", event)

    def process_tray():
        menu_item = tray.Read()
        if menu_item == "Exit":
            exit()
        elif menu_item == "Open":
            sg.Popup("Menu item chosen", menu_item)

    while True:
        process_window()
        # process_tray()

    return True


# PopupGetFolder
# PopupGetFile
# PopupGetText


def main():
    create_window()
    # create_system_tray_entry()
    process_input()


if __name__ == "__main__":
    main()
