import PySimpleGUI as sg

sg.change_look_and_feel("DarkAmber")  # Add a little color

# All the stuff inside your window.
frm_dir = [
    [
        sg.InputText(key="_selected_dir_", size=(44, 1)),
        sg.Button("Browse", size=(5, 1)),
    ]
]

frm_config = [
    [sg.Text("Directory:", size=(15, 1)), sg.InputText(key="_dir_", size=(37, 1))],
    [sg.Text("Extensions:", size=(15, 1)), sg.InputText(key="_ext_", size=(37, 1))],
    [sg.Text("Blacklist:", size=(15, 1)), sg.InputText(key="_bl_", size=(37, 1))],
    [
        sg.Text("Blacklist Regex:", size=(15, 1)),
        sg.InputText(key="_bl_regex_", size=(37, 1)),
    ],
    [sg.Text("Whitelist:", size=(15, 1)), sg.InputText(key="_wl_", size=(37, 1))],
    [
        sg.Text("Whitelist Regex:", size=(15, 1)),
        sg.InputText(key="_wl_regex_", size=(37, 1)),
    ],
    [sg.Text("Logfile:", size=(15, 1)), sg.InputText(key="_log_", size=(37, 1))],
]

frm_data = [
    [
        sg.Listbox(values=("one", "two", "three"), size=(24, 5)),
        sg.Listbox(values=("one", "two", "three"), size=(24, 5)),
    ]
]

tab_tools_convert = [[]]
tab_tools_export = [[]]
tab_tools_afx = [
    [
        sg.Frame(
            title="Fade",
            layout=[
                [
                    sg.InputText(key="_afx_fade_in_", size=(21, 1)),
                    sg.InputText(key="_afx_fade_out_", size=(21, 1)),
                ]
            ],
        )
    ],
]
tab_tools_name = [
    [
        sg.Frame(
            title="Prepend", layout=[[sg.InputText(key="_name_prepend_", size=(45, 1))]]
        )
    ],
    [
        sg.Frame(
            title="Append", layout=[[sg.InputText(key="_name_append_", size=(45, 1))]]
        )
    ],
]

frm_tools = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("AFX", tab_tools_afx),
                    sg.Tab("Name", tab_tools_name),
                    sg.Tab("Convert", tab_tools_convert),
                    sg.Tab("Export", tab_tools_export),
                ]
            ]
        )
    ]
]

tab_main = [
    [sg.Frame(title="Directory:", layout=frm_dir)],
    [sg.Frame(title="Tools:", layout=frm_tools)],
]

tab_config = [
    [sg.Frame(title="Config:", layout=frm_config)],
    [sg.Button("Reset"), sg.Button("Apply")],
]
tab_data = [[sg.Frame(title="Data", layout=frm_data)]]

layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("Main", tab_main),
                    sg.Tab("Config", tab_config),
                    sg.Tab("Data", tab_data),
                ]
            ]
        )
    ]
]

# Create the Window
window = sg.Window("aud", layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, "Cancel"):  # if user closes window or clicks cancel
        break
    elif event == "Ok":
        print("You entered ", values["_IN_"])
        window["_IN_"].update("")


window.close()
