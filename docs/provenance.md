# provenance

The input is the user's supplied `ria.zip`, containing the previous 28/14/56 build, Python source, reference STEP models and timing-pulley profile references.

`ria/assets.py` selects the two original head objects, the hip nose clipped from the original local leg, and sixteen named existing/purchased hip components. Each retained compressed B-rep is accompanied by the source-relative path, SHA-256 of the source STEP bytes, SHA-256 of the cached B-rep, volume, bounds and solid count in `assets/reference/manifest.json`. No user-specific upload path is embedded in the application.

`ria/gears.py` rewrites the original Python's involute construction and sampling; it does not import or execute the archived SCAD. The timing groove polygon in `ria/belt.py` retains the archived `tooth_profile_GT2_3mm` coordinates, width allowance and depth offset without re-fitting. The archive attributes the timing-profile source to droftarts and rbuckland; its `pulley_profiles.scad` also credits Per Ivar Nerseth's modifications. This inherited groove is not asserted to be a manufacturer-certified GT3 profile.

Original third-party notices and ownership are not replaced by a new licence grant here. The supplied `involute_gears.scad` identifies GregFrost and a Creative Commons / GNU LGPL 2.1 licence, but that SCAD implementation is not required or distributed as runtime source by this rewrite. The original archive remains the provenance record for the supplied references. No licence for purchased/reference CAD is inferred from its presence in that archive.
