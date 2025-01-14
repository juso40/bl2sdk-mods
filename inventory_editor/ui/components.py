from imgui_bundle import imgui


def combo_with_title(
    title: str,
    current: int,
    items: list[str],
    spacing: bool = False,
) -> tuple[bool, int]:
    """Draws a combo box with a title above it."""
    if spacing:
        imgui.spacing()
        imgui.spacing()
    imgui.text(title)
    imgui.push_item_width(-1)
    clicked, current = imgui.combo(
        f"##{title}",
        current_item=current,
        items=items,
    )
    imgui.pop_item_width()
    return clicked, current
