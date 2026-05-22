# -*- coding: utf-8 -*-
import gmsh
import argparse

# --- LIBRERÍA AÑADIDA: ARGPARSE ---
parser = argparse.ArgumentParser(description="PID reassignment tool for pre-curved high-order meshes.")
parser.add_argument("--mesh", required=True, help="Input curved mesh file (e.g., mesh_g2.msh)")
parser.add_argument("--output", required=True, help="Output mesh file name (e.g., mesh_g2_ready.msh)")
args = parser.parse_args()
# ----------------------------------

gmsh.initialize()

# ==============================================================================
# 2. Load the ANSA mesh
# ==============================================================================
print("Reading original mesh from ANSA...")
gmsh.merge(args.mesh)

# ==============================================================================
# 3. AUTOMATIC TAG DETECTION (CAD vs MESH) AND CREATION OF PHYSICAL GROUPS
# ==============================================================================
print("\nAutomatically detecting entities...")

surf_malla = []
vol_malla = []

# --- Surfaces ---
for dim, tag in gmsh.model.getEntities(2):
    entity_type = gmsh.model.getType(dim, tag).lower()
    elemTypes, elemTags, _ = gmsh.model.mesh.getElements(2, tag)
    num_elems = sum(len(t) for t in elemTags)

    print(f"[SURF] Tag: {tag} | Type: {entity_type} | Elements: {num_elems}")
    if num_elems > 0:
        surf_malla.append(tag)

# --- Volumes ---
for dim, tag in gmsh.model.getEntities(3):
    entity_type = gmsh.model.getType(dim, tag).lower()
    elemTypes, elemTags, _ = gmsh.model.mesh.getElements(3, tag)
    num_elems = sum(len(t) for t in elemTags)

    print(f"[VOL] Tag: {tag} | Type: {entity_type} | Elements: {num_elems}")
    if num_elems > 0:
        vol_malla.append(tag)


# For the current case (3D toroid), we assume 1-1 correspondence
tag_vol_malla = vol_malla

print("\nSummary:")
print(f"Mesh Surfaces: {surf_malla}")
print(f"Mesh Volume: {tag_vol_malla}")

# For PyHOPE, we remove previous physical names and create new Physical Groups with the detected tags. Think about how to automate this process for more complex cases. For the toroid, this works.
gmsh.model.removePhysicalGroups([])
gmsh.model.removePhysicalName("fluid")
gmsh.model.removePhysicalName("skin")
gmsh.model.addPhysicalGroup(3, vol_malla, name="fluid")
gmsh.model.addPhysicalGroup(2, surf_malla, name="skin")

# # ==============================================================================
# # 6. QUALITY REVIEW (JACOBIANS)
# # ==============================================================================
# print("\nAnalyzing the quality of the high-order mesh...")

# # We configure the AnalyseMeshQuality plugin of Gmsh [4]
# gmsh.plugin.setNumber("AnalyseMeshQuality", "JacobianDeterminant", 1)  # Evaluate Jacobian determinant
# gmsh.plugin.setNumber("AnalyseMeshQuality", "ICNMeasure", 1)           # Evaluate SICN condition
# gmsh.plugin.setNumber("AnalyseMeshQuality", "CreateView", 1)           # Create visual views (color maps)
# gmsh.plugin.setNumber("AnalyseMeshQuality", "DimensionOfElements", -1) # Analyze only the highest dimension (3D volume)

# # We execute the plugin
# gmsh.plugin.run("AnalyseMeshQuality")

# Force Gmsh to save all elements
gmsh.option.setNumber("Mesh.SaveAll", 1) 

output_name = args.output
print(f"\nSaving final mesh to: {output_name}")
gmsh.write(output_name)

# # View the result visually
# print("Opening the graphical interface...")
# gmsh.fltk.run() 
# gmsh.finalize()
