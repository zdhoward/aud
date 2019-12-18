import PySimpleGUIQt as sg

### MENU ###
menu_def = [
    [
        "&File",
        [
            "Change Theme",
            [
                "Green::_change_theme_GreenMono",
                "Topanga::_change_theme_Topanga",
                "Dark Amber::_change_theme_Dark Amber",
            ],
            "Exit",
        ],
    ],
    [
        "&Tools",
        [
            "Name::_tools_name_",
            "AFX::_tools_afx_",
            "Convert::_tools_convert_",
            "Export::_tools_export_",
        ],
    ],
    ["&Help", ["About"]],
]

### FORMS ###
frm_layout_main = [
    [
        sg.Text("Directory: "),
        sg.InputText(key="_selected_dir_", default_text="", disabled=True),
        sg.FolderBrowse("Browse", key="_selected_dir_browse_", size=(8, 1)),
    ],
    [
        sg.InputText(key="_backup_location_", visible=False, enable_events=True),
        sg.FolderBrowse("Backup", key="_main_backup_"),
        sg.InputText(key="_move_location_", visible=False, enable_events=True),
        sg.FolderBrowse("Move", key="_main_move_"),
        sg.InputText(key="_copy_location_", visible=False, enable_events=True),
        sg.FolderBrowse("Copy", key="_main_copy_"),
        sg.InputText(key="_zip_location_", visible=False, enable_events=True),
        sg.FolderBrowse("Zip", key="_main_zip_"),
    ],
]
frm_layout_config = [
    [
        sg.Button("Set Extensions", key="_config_set_extensions_"),
        sg.Button("Set Blacklist", key="_config_set_blacklist_"),
        sg.Button("Set Whitelist", key="_config_set_whitelist_"),
        sg.Button("Set Logfile", key="_config_set_logfile_"),
    ]
]

### FRAMES ###
frm_main = sg.Frame(
    title="Main", layout=frm_layout_main, key="_frm_main_", visible=True
)

frm_config = sg.Frame(
    title="Config", layout=frm_layout_config, key="_frm_config_", visible=True
)

frm_tools_name = sg.Frame(
    title="Change Filenames",
    layout=[[sg.T("Tools_Name")]],
    key="_frm_tools_name_",
    visible=False,
)
frm_tools_afx = sg.Frame(
    title="Apply Audio FX",
    layout=[[sg.T("Tools AFX")]],
    key="_frm_tools_afx_",
    visible=False,
)
frm_tools_convert = sg.Frame(
    title="Convert File Types",
    layout=[[sg.T("Tools Convert")]],
    key="_frm_tools_convert_",
    visible=False,
)
frm_tools_export = sg.Frame(
    title="Export For Platform",
    layout=[[sg.T("Tools Export")]],
    key="_frm_tools_export_",
    visible=False,
)

layout = [
    [sg.Menu(menu_def)],
    [frm_main],
    [frm_config],
    [frm_tools_name],
    [frm_tools_afx],
    [frm_tools_convert],
    [frm_tools_export],
]
