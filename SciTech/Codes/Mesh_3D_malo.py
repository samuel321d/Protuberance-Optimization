"""Generate a 3D rocket mesh inside a bullet-shaped farfield domain."""

from math import pi
from pathlib import Path

import gmsh


def meshgen_3D(config=None):
    """Import the rocket STEP, build the fluid domain, and generate its mesh.

    The default boundary-layer construction follows the extrusion-based
    approach in BL.py. Lengths are interpreted in the same units as the STEP.
    """
    defaults = {
        "step file": "Rocket.step",
        "filename": "Mesh_3D.msh",
        "global size": 2000.0,
        "wall size": 25.0,
        "threshold distance": 1500.0,
        "BOI1": 1200.0,
        "BOI2": 600.0,
        "BOI3": 200.0,
        "use boundary layer": True,
        "number of layers": 15,
        "layer ratio": 1.15,
        "layer thickness": 0.1,
        "farfield radius factor": 12.0,
        "farfield downstream factor": 15.0,
        "show GUI": False,
    }
    config = {**defaults, **(config or {})}

    step_path = Path(config["step file"])
    if not step_path.is_absolute():
        step_path = Path(__file__).parent / step_path
    if not step_path.is_file():
        raise FileNotFoundError(f"Rocket STEP file not found: {step_path}")

    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add("Rocket_3D")
        occ = gmsh.model.occ
        mesh = gmsh.model.mesh

        imported = occ.importShapes(str(step_path), highestDimOnly=True)
        rocket_volumes = [(dim, tag) for dim, tag in imported if dim == 3]
        if not rocket_volumes:
            raise RuntimeError(f"No 3D solid was imported from {step_path}")
        occ.synchronize()

        rocket_boxes = [
            gmsh.model.getBoundingBox(dim, tag)
            for dim, tag in rocket_volumes
        ]
        x_min = min(box[0] for box in rocket_boxes)
        y_min = min(box[1] for box in rocket_boxes)
        z_min = min(box[2] for box in rocket_boxes)
        x_max = max(box[3] for box in rocket_boxes)
        y_max = max(box[4] for box in rocket_boxes)
        z_max = max(box[5] for box in rocket_boxes)
        length = x_max - x_min
        radial_size = max(y_max - y_min, z_max - z_min)
        if length <= 0 or radial_size <= 0:
            raise ValueError("The imported rocket has invalid dimensions.")

        # A hemispherical nose joined to a cylindrical downstream section.
        radius = config["farfield radius factor"] * length
        downstream_length = config["farfield downstream factor"] * length
        body_radial_extent = (
            max(abs(y_min), abs(y_max)) ** 2
            + max(abs(z_min), abs(z_max)) ** 2
        ) ** 0.5
        if radius <= body_radial_extent or downstream_length <= 0:
            raise ValueError(
                "The farfield radius and downstream length must enclose the rocket."
            )
        hemisphere = occ.addSphere(
            x_max, 0, 0, radius, -1, -pi / 2, 0
        )
        occ.rotate(
            [(3, hemisphere)], x_max, 0, 0, 0, 1, 0, pi / 2
        )
        downstream = occ.addCylinder(
            x_max, 0, 0, downstream_length, 0, 0, radius
        )
        domain, _ = occ.fuse([(3, hemisphere)], [(3, downstream)])
        if not domain:
            raise RuntimeError("Could not create the bullet-shaped farfield.")
        occ.synchronize()
        # Build one conformal OCC fluid volume; the boundary-layer field below
        # meshes prism layers on its wall faces without overlapping volumes.
        fluid, _ = occ.cut(domain, rocket_volumes)
        occ.synchronize()
        fluid_volume_tags = [tag for dim, tag in fluid if dim == 3]
        if not fluid_volume_tags:
            raise RuntimeError("The rocket cut produced no fluid volume.")
        fluid_boundary = gmsh.model.getBoundary(
            [(3, tag) for tag in fluid_volume_tags],
            combined=False,
            oriented=False,
        )
        farfield_surfaces = []
        wall_surfaces = []
        tolerance = max(length, radial_size) * 1e-6
        for dim, tag in fluid_boundary:
            if dim != 2:
                continue
            box = gmsh.model.getBoundingBox(dim, tag)
            is_wall = (
                box[0] >= x_min - tolerance
                and box[1] >= y_min - tolerance
                and box[2] >= z_min - tolerance
                and box[3] <= x_max + tolerance
                and box[4] <= y_max + tolerance
                and box[5] <= z_max + tolerance
            )
            (wall_surfaces if is_wall else farfield_surfaces).append(tag)

        # Physical groups for CFD boundary conditions and the fluid region.
        gmsh.model.addPhysicalGroup(
            3,
            fluid_volume_tags,
            name="Fluid",
        )
        gmsh.model.addPhysicalGroup(2, farfield_surfaces, name="FarField")
        gmsh.model.addPhysicalGroup(2, wall_surfaces, name="Walls")

        if config["use boundary layer"]:
            layer_count = int(config["number of layers"])
            first_height = float(config["layer thickness"])
            ratio = float(config["layer ratio"])
            if layer_count < 1:
                raise ValueError("'number of layers' must be at least 1.")
            if first_height <= 0:
                raise ValueError("'layer thickness' must be greater than 0.")
            if ratio < 1:
                raise ValueError("'layer ratio' must be at least 1.")

            total_thickness = sum(
                first_height * ratio**index for index in range(layer_count)
            )
            boundary_layer = mesh.field.add("BoundaryLayer")
            mesh.field.setNumbers(boundary_layer, "FacesList", wall_surfaces)
            mesh.field.setNumber(boundary_layer, "Size", first_height)
            mesh.field.setNumber(boundary_layer, "Ratio", ratio)
            mesh.field.setNumber(
                boundary_layer, "Thickness", total_thickness
            )
            mesh.field.setAsBoundaryLayer(boundary_layer)

        # Ignore point and curvature sizes; prescribe sizes through fields.
        gmsh.option.setNumber("Mesh.MeshSizeMin", config["wall size"])
        gmsh.option.setNumber("Mesh.MeshSizeMax", config["global size"])
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)

        # Three nested box fields give progressively finer near-field sizing.
        center_y = 0.5 * (y_min + y_max)
        center_z = 0.5 * (z_min + z_max)
        body_radius = 0.5 * radial_size
        boi_specs = [
            (
                config["BOI1"],
                x_min - 0.5 * length,
                x_max + 3.0 * length,
                4.0 * body_radius,
            ),
            (
                config["BOI2"],
                x_min - 0.25 * length,
                x_max + 1.5 * length,
                2.5 * body_radius,
            ),
            (
                config["BOI3"],
                x_min - 0.05 * length,
                x_max + 0.5 * length,
                1.5 * body_radius,
            ),
        ]
        size_fields = []
        for target_size, box_x_min, box_x_max, box_radius in boi_specs:
            box_field = mesh.field.add("Box")
            mesh.field.setNumber(box_field, "XMin", box_x_min)
            mesh.field.setNumber(box_field, "XMax", box_x_max)
            mesh.field.setNumber(box_field, "YMin", center_y - box_radius)
            mesh.field.setNumber(box_field, "YMax", center_y + box_radius)
            mesh.field.setNumber(box_field, "ZMin", center_z - box_radius)
            mesh.field.setNumber(box_field, "ZMax", center_z + box_radius)
            mesh.field.setNumber(box_field, "VIn", target_size)
            mesh.field.setNumber(box_field, "VOut", config["global size"])
            mesh.field.setNumber(box_field, "Thickness", target_size)
            size_fields.append(box_field)

        wall_distance = mesh.field.add("Distance")
        mesh.field.setNumbers(wall_distance, "SurfacesList", wall_surfaces)
        mesh.field.setNumber(wall_distance, "Sampling", 100)

        wall_threshold = mesh.field.add("Threshold")
        mesh.field.setNumber(wall_threshold, "IField", wall_distance)
        mesh.field.setNumber(wall_threshold, "LcMin", config["wall size"])
        mesh.field.setNumber(wall_threshold, "LcMax", config["global size"])
        mesh.field.setNumber(wall_threshold, "DistMin", 0.0)
        mesh.field.setNumber(
            wall_threshold, "DistMax", config["threshold distance"]
        )
        size_fields.append(wall_threshold)

        background = mesh.field.add("Min")
        mesh.field.setNumbers(background, "FieldsList", size_fields)
        mesh.field.setAsBackgroundMesh(background)

        mesh.generate(3)
        output_path = Path(config["filename"])
        if not output_path.is_absolute():
            output_path = Path(__file__).parent / output_path
        gmsh.write(str(output_path))
        print(f"3D mesh written to {output_path}")

        if config["show GUI"]:
            gmsh.fltk.run()
    finally:
        gmsh.finalize()


if __name__ == "__main__":
    meshgen_3D()
