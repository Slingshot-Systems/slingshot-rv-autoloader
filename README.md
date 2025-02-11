# slingshot-autoloader

An [RV](https://help.autodesk.com/view/SGSUB/ENU/?guid=SG_RV_rv_osrv_html)/[OpenRV](https://github.com/AcademySoftwareFoundation/OpenRV) plugin that auto-loads plates, v000s, luts and CDLs.


## Development

When a plugin in loaded and installed in RV, you can directly edit or replace python files in `%AppData$\Roaming\RV\Python` for testing, instead of unloading/reloading new versions of the plugin.

### Testing
Testing is difficult outside of the RV environment, but you can run the few tests we have using `pytest`:

"""shell
poetry run pytest ./tests/
"""

---

This package is based off code by Autodesk, Inc., licensed under `Apache-2.0`.
