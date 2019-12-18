import PySimpleGUIQt as sg
from aud import Dir

sg.change_look_and_feel("DarkAmber")  # Add a little color

frm_dir = sg.Frame(
    title="Working Directory:",
    layout=[
        [
            sg.InputText(key="_selected_dir_", size=(44, 1), disabled=True),
            sg.Button("Browse", size=(5, 1)),
        ]
    ],
)

frm_output_dir = sg.Frame(
    title="Output Directory:",
    layout=[
        [
            sg.InputText(key="_output_dir_", size=(44, 1), disabled=True),
            sg.Button("Browse", size=(5, 1)),
        ]
    ],
)

frm_config = sg.Frame(
    title="Config:",
    layout=[
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
    ],
)

frm_data = sg.Frame(
    title="Data:",
    layout=[
        [sg.Text("All Files:", size=(26, 1)), sg.Text("Filtered Files:", size=(26, 1))],
        [
            sg.Listbox(values=("one", "two", "three"), size=(24, 5)),
            sg.Listbox(values=("one", "two", "three"), size=(24, 5)),
        ],
    ],
)

tab_tools_convert = sg.Tab(
    "Convert",
    [
        [sg.Button("WAV", key="_convert_to_wav_", size=(47, 1))],
        [sg.Button("MP3", key="_convert_to_mp3_", size=(47, 1))],
        [sg.Button("OGG", key="_convert_to_ogg_", size=(47, 1))],
        [sg.Button("FLAC", key="_convert_to_flac_", size=(47, 1))],
        [sg.Button("RAW", key="_convert_to_raw_", size=(47, 1))],
    ],
)
tab_tools_export = sg.Tab(
    "Export", [[sg.Button("Amuse", key="_export_for_amuse_", size=(47, 1))],],
)
tab_tools_afx = sg.Tab(
    "AFX",
    [
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
        [
            sg.Frame(
                title="Pad",
                layout=[
                    [
                        sg.InputText(key="_afx_pad_in_", size=(21, 1)),
                        sg.InputText(key="_afx_pad_out_", size=(21, 1)),
                    ]
                ],
            )
        ],
        [
            sg.Frame(
                title="Normalize",
                layout=[
                    [
                        sg.InputText(key="_afx_normalize_target_level_", size=(21, 1)),
                        sg.InputText(key="_afx_normalize_passes_", size=(21, 1)),
                    ]
                ],
            )
        ],
        [
            sg.Frame(
                title="Join",
                layout=[
                    [
                        sg.InputText(key="_afx_join_location_", size=(21, 1)),
                        sg.InputText(key="_afx_join_format_", size=(21, 1)),
                    ]
                ],
            )
        ],
        [
            sg.Frame(
                title="Prepend",
                layout=[[sg.InputText(key="_afx_prepend_", size=(44, 1)),]],
            )
        ],
        [
            sg.Frame(
                title="Append",
                layout=[[sg.InputText(key="_afx_append_", size=(44, 1)),]],
            )
        ],
        [
            sg.Frame(
                title="Invert Stereo Phase",
                layout=[[sg.InputText(key="_afx_invert_phase_", size=(44, 1)),]],
            )
        ],
        [
            sg.Frame(
                title="Low Pass Filter",
                layout=[[sg.InputText(key="_afx_lpf_cutoff_", size=(44, 1)),]],
            )
        ],
        [
            sg.Frame(
                title="High Pass Filter",
                layout=[[sg.InputText(key="_afx_hpf_cutoff_", size=(44, 1)),]],
            )
        ],
        [
            sg.Frame(
                title="Gain", layout=[[sg.InputText(key="_afx_gain_", size=(44, 1)),]],
            )
        ],
        [
            sg.Frame(
                title="Watermark",
                layout=[
                    [
                        sg.InputText(key="_afx_watermark_file_", size=(25, 1)),
                        sg.InputText(key="_afx_watermark_min_", size=(7, 1)),
                        sg.InputText(key="_afx_watermark_max_", size=(7, 1)),
                    ]
                ],
            )
        ],
        [
            sg.Frame(
                title="Strip Silence",
                layout=[
                    [
                        sg.InputText(key="_afx_strip_silence_length_", size=(25, 1)),
                        sg.InputText(key="_afx_strip_silence_threshold_", size=(7, 1)),
                        sg.InputText(key="_afx_strip_silence_padding_", size=(7, 1)),
                    ]
                ],
            )
        ],
        [
            sg.Button("Clear", key="_afx_clear_"),
            sg.Button("Apply Changes", key="_afx_apply_changes_"),
        ],
    ],
)

tab_tools_name = sg.Tab(
    "Name",
    [
        [
            sg.Frame(
                title="Prepend",
                layout=[[sg.InputText(key="_name_prepend_", size=(45, 1))]],
            )
        ],
        [
            sg.Frame(
                title="Append",
                layout=[[sg.InputText(key="_name_append_", size=(45, 1))]],
            )
        ],
        [
            sg.Frame(
                title="Iterate",
                layout=[
                    [
                        sg.InputText(key="_name_iterate_zerofill_", size=(33, 1)),
                        sg.InputText(key="_name_iterate_separator_", size=(10, 1)),
                    ],
                ],
            )
        ],
        [
            sg.Frame(
                title="Replace",
                layout=[
                    [
                        sg.InputText(key="_name_replace_target_", size=(22, 1)),
                        sg.InputText(key="_name_replace_replacement_", size=(21, 1)),
                    ],
                ],
            )
        ],
        [
            sg.Frame(
                title="Replace Spaces",
                layout=[[sg.InputText(key="_name_replace_spaces_", size=(45, 1)),],],
            )
        ],
        [
            sg.Button("Clear", key="_name_clear_"),
            sg.Button("Apply Changes", key="_name_apply_changes_"),
        ],
    ],
)

frm_tools = sg.Frame(
    title="Tools:",
    layout=[
        [
            sg.TabGroup(
                [[tab_tools_afx, tab_tools_name, tab_tools_convert, tab_tools_export,]]
            )
        ]
    ],
)

tab_main = sg.Tab("Main", [[frm_dir], [frm_tools]])

tab_config = sg.Tab(
    "Config",
    [
        [frm_config],
        [
            sg.Button("Reset", key="_config_reset_"),
            sg.Button("Apply", key="_config_apply_"),
        ],
    ],
)

tab_data = sg.Tab("Data", [[frm_data]])

layout = [[sg.TabGroup([[tab_main, tab_config, tab_data,]])]]

# Create the Window
window = sg.Window("aud", layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, "Cancel"):  # if user closes window or clicks cancel
        break
    elif event == "Apply":
        print("You entered ", values["_dir_"])
    elif event == "Reset":
        print("Resetting all values")
        window["_dir_"].update("")
    elif event == "Browse":
        print("Browsing from", values["_selected_dir_"])


window.close()
