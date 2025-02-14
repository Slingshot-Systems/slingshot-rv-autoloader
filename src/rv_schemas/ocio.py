from typing import TypedDict

# OCIO Node Properties
# https://aswf-openrv.readthedocs.io/en/latest/rv-manuals/rv-user-manual/rv-user-manual-chapter-eleven.html#operation-of-the-ocio-node
OCIOProperties = TypedDict(
    "OCIOProperties",
    {
        "ocio.function": str,  # One of “color”, “look”, or “display”
        # "ocio.lut": list[float],  # Used internally to store the OCIO generated 3D LUT
        "ocio.active": int,  # Activates/deactivates the OCIO node
        "ocio.lut3DSize": int,  # The desired size of the OCIO generated 3D LUT (default=32)
        "ocio.inColorSpace": str,  # The OCIO name of the input color space
        "ocio_color.outColorSpace": str,  # The OCIO name of the output color space when ocio.function == “color”
        "ocio_look.look": str,  # The OCIO command string for the look when ocio.function == “look”
        "ocio_look.direction": int,  # 0=forward, 1=inverse
        "ocio_display.display": str,  # OCIO display name when ocio.function == “display”
        "ocio_display.view": str,  # OCIO view name when ocio.function == “display”
        # "ocio_context": dict[
        #     str, str
        # ],  # String properties in this component become OCIO config name/value pairs
    },
    total=False,
)
