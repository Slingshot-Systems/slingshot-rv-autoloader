# slingshot-autoloader

An [RV](https://help.autodesk.com/view/SGSUB/ENU/?guid=SG_RV_rv_osrv_html)/[OpenRV](https://github.com/AcademySoftwareFoundation/OpenRV) plugin that auto-loads plates, v000s, luts and CDLs.

## Configuration
Configuration can be loaded from a `.cfg` file. See the `slingshot_rv_autoloader.EXAMPLE.cfg` file for an example.

The config file is copied to your home folder, where you can also edit it directly if you prefer:

```
Windows: C:\Users\<user>\.slingshot_rv_autoloader.cfg
Mac: /Users/<user>/.slingshot_rv_autoloader.cfg
Linux: ~/.slingshot_rv_autoloader.cfg
```

## Development

When a plugin in loaded and installed in RV, you can directly edit or replace python files in `%AppData$\Roaming\RV\Python` for testing, instead of unloading/reloading new versions of the plugin.

### Testing
Testing is difficult outside of the RV environment, but you can run the few tests we have using `pytest`:

```shell
poetry run pytest ./tests/
```

---

This package is based off code by Autodesk, Inc., licensed under `Apache-2.0`.
