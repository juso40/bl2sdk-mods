from mods_base import options

ping_duration = options.SliderOption(
    "Ping Duration",
    5.0,
    0.5,
    20.0,
    0.5,
    False,
    description="How long the ping should be displayed in seconds.",
)


ping_color_1 = options.NestedOption(
    "Your Ping Color",
    children=[
        options.SliderOption("Text R", value=103, min_value=0, max_value=255),
        options.SliderOption("Text G", value=215, min_value=0, max_value=255),
        options.SliderOption("Text B", value=255, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)


ping_color_2 = options.NestedOption(
    "Ping Color 2",
    children=[
        options.SliderOption("Text R", value=255, min_value=0, max_value=255),
        options.SliderOption("Text G", value=204, min_value=0, max_value=255),
        options.SliderOption("Text B", value=0, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)

ping_color_3 = options.NestedOption(
    "Ping Color 3",
    children=[
        options.SliderOption("Text R", value=20, min_value=0, max_value=255),
        options.SliderOption("Text G", value=255, min_value=0, max_value=255),
        options.SliderOption("Text B", value=169, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)

ping_color_4 = options.NestedOption(
    "Ping Color 4",
    children=[
        options.SliderOption("Text R", value=204, min_value=0, max_value=255),
        options.SliderOption("Text G", value=83, min_value=0, max_value=255),
        options.SliderOption("Text B", value=250, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)