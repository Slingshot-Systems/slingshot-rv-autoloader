# slingshot-autoloader

An [RV](https://help.autodesk.com/view/SGSUB/ENU/?guid=SG_RV_rv_osrv_html)/[OpenRV](https://github.com/AcademySoftwareFoundation/OpenRV) plugin that auto-loads plates, v000s, luts and CDLs.

## Getting started

Slingshot Auto Loader is an open source project that is free to download and use.

 If you would like assistance with set up or configuration, feel free to reach out to [Slingshot Systems](https://www.slingshotsystems.io) to get a quote for paid support.

### Download
Download the latest release from [https://github.com/Slingshot-Systems/slingshot-rv-autoloader/releases/latest](https://github.com/Slingshot-Systems/slingshot-rv-autoloader/releases/latest)

### Install
Add the .rvpkg file from the `RV -> Preferences -> Packages` screen, using the `Add Packages...` button. Make sure to click both the `Installed` and `Load` checkboxes.

Restart RV.

### Configure
Configuration can be loaded from a `.cfg` file via the `Slingshot Auto Loader -> Current Configuration -> Load config from file...` menu.

See the `slingshot_rv_autoloader.EXAMPLE.cfg` file for an example.

Once loaded, you can verify your configuration in the `Slingshot Auto Loader -> Current Configuration` menu.

The config file is copied to your home folder, where you can also edit it directly if you prefer:

```
Windows: C:\Users\<user>\.slingshot_rv_autoloader.cfg
Mac: /Users/<user>/.slingshot_rv_autoloader.cfg
Linux: ~/.slingshot_rv_autoloader.cfg
```

Restart RV to apply any changes made by manually editing these files.

## Features

### Auto load media

When media is added to RV, Slingshot Auto Loader can look on the disk for associated files and automatically add them as media sources.

For example, it can:
- Automatically add Plate video or image sequences when a comp version is loaded.
- Automatically add Prores or EXR media when an h264 file is loaded.

### Auto load LUTs/CDLs

Slingshot Auto Loader can automatically set ocio colorspaces when loading EXR frames. It embeds aces-v1.3 / ocio-v2.2 configurations so you don't have to manually set up ocio in RV. 

It can also look on the disk for associated LUT or CDL files and automatically apply them as Look LUTs.

## Development

When a plugin in loaded and installed in RV, you can directly edit or replace python files in `%AppData$\Roaming\RV\Python` for testing, instead of unloading/reloading new versions of the plugin.

### Testing
Testing is difficult outside of the RV environment, but you can run the few tests we have using `pytest`:

```shell
poetry run pytest ./tests/
```

---

## License

Copyright 2025 Slingshot Systems Inc.
Licensed under `Apache-2.0`. See the `LICENSE` file for more information.

OpenRV is Copyright Autodesk, Inc., licensed under `Apache-2.0`.
