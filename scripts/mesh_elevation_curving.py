# -*- coding: utf-8 -*-
import gmsh
import argparse

# --- LIBRERÍA AÑADIDA: ARGPARSE ---
parser = argparse.ArgumentParser(description="Mesh curving and order elevation tool via Gmsh API.")
parser.add_argument("--cad", required=True, help="Input CAD file (e.g., model.step)")
parser.add_argument("--mesh", required=True, help="Input mesh file (e.g., mesh_linear.msh)")
parser.add_argument("--output", required=True, help="Output mesh file name (e.g., mesh_g2.msh)")
parser.add_argument("--target_order", type=int, default=2, help="Target geometric order (e.g., 2, 3, 4)")
args = parser.parse_args()
# ----------------------------------

gmsh.initialize()

# ==============================================================================
# 1. Load the original CAD model
# ==============================================================================
print("Loading CAD model...")
gmsh.model.occ.importShapes(args.cad)
gmsh.model.occ.synchronize()

# ==============================================================================
# 2. Load the linear mesh from ANSA
# ==============================================================================
print("Reading original mesh from ANSA...")
gmsh.merge(args.mesh)

# ==============================================================================
# 3. AUTOMATIC TAG DETECTION (CAD vs MESH) AND CREATION OF PHYSICAL GROUPS
# ==============================================================================
print("\nAutomatically detecting entities...")

surf_cad = []
surf_malla = []
vol_cad = []
vol_malla = []

# --- Surfaces ---
for dim, tag in gmsh.model.getEntities(2):
    entity_type = gmsh.model.getType(dim, tag).lower()
    elemTypes, elemTags, _ = gmsh.model.mesh.getElements(2, tag)
    num_elems = sum(len(t) for t in elemTags)

    print(f"[SURF] Tag: {tag} | Type: {entity_type} | Elements: {num_elems}")

    # Condition 1: It is mathematical geometry (CAD) if it is not "discrete" type
    if "discrete" not in entity_type:
        surf_cad.append(tag)
        
    # Condition 2: It contains a mesh if it has elements (even if it's the same CAD entity)
    if num_elems > 0:
        surf_malla.append(tag)

# --- Volumes ---
for dim, tag in gmsh.model.getEntities(3):
    entity_type = gmsh.model.getType(dim, tag).lower()
    elemTypes, elemTags, _ = gmsh.model.mesh.getElements(3, tag)
    num_elems = sum(len(t) for t in elemTags)

    print(f"[VOL] Tag: {tag} | Type: {entity_type} | Elements: {num_elems}")

    if "discrete" not in entity_type:
        vol_cad.append(tag)
        
    if num_elems > 0:
        vol_malla.append(tag)

if not surf_cad or not surf_malla or not vol_cad or not vol_malla:
    raise RuntimeError("Could not properly identify CAD/mesh entities.")

# For the current case (3D toroid), we assume 1-1 correspondence
tag_vol_cad = vol_cad
tag_vol_malla = vol_malla

print("\nSummary:")
print(f"CAD Surfaces: {surf_cad}")
print(f"Mesh Surfaces: {surf_malla}")
print(f"CAD Volume: {tag_vol_cad}")
print(f"Mesh Volume: {tag_vol_malla}")

# For PyHOPE, we remove previous physical names and create new Physical Groups with the detected tags. Think about how to automate this process for more complex cases. For the toroid, this works.
gmsh.model.removePhysicalGroups([])
gmsh.model.removePhysicalName("fluid")
gmsh.model.removePhysicalName("skin")
gmsh.model.addPhysicalGroup(3, vol_cad, name="fluid")
gmsh.model.addPhysicalGroup(2, surf_cad, name="skin")

# ==============================================================================
# 4A. SURFACE TRANSFER AND RECONSTRUCTION (With U, V)
# ==============================================================================
print("\nReconstructing surfaces over the CAD...")

for tag_surf_malla in surf_malla:

    nodeTags, coords, _ = gmsh.model.mesh.getNodes(2, tag_surf_malla)
    elemTypes2D, elemTags2D, elemNodeTags2D = gmsh.model.mesh.getElements(2, tag_surf_malla)

    if len(nodeTags) == 0:
        continue

    # For simple case (toroid): we use the first CAD surface
    # (in CRM it would need to be related)
    tag_surf_cad = surf_cad[0]

    print(f"Projecting surface {tag_surf_malla} over CAD {tag_surf_cad}")

    # Parametrization
    uvs = gmsh.model.getParametrization(2, tag_surf_cad, coords)

    # Clear only that surface
    gmsh.model.mesh.clear([(2, tag_surf_malla)])

    # Reconstruction
    gmsh.model.mesh.addNodes(2, tag_surf_cad, nodeTags, coords, uvs)
    gmsh.model.mesh.addElements(2, tag_surf_cad, elemTypes2D, elemTags2D, elemNodeTags2D)

# ==============================================================================
# 4B. VOLUME TRANSFER (Elements Only)
# ==============================================================================
print("\nReconstructing volume...")

for tag_vol_malla in vol_malla:

    # 1. We extract both internal Nodes and 3D Elements
    nodeTags3D, coords3D, _ = gmsh.model.mesh.getNodes(3, tag_vol_malla)
    elemTypes3D, elemTags3D, elemNodeTags3D = gmsh.model.mesh.getElements(3, tag_vol_malla)

    if len(elemTypes3D) == 0:
        continue

    tag_vol_cad = vol_cad[0]

    # Case: already in CAD
    if tag_vol_malla == tag_vol_cad:
        print(f"Volume {tag_vol_malla} is already in CAD: skipped")
        continue

    print(f"Reconstructing volume {tag_vol_malla} over CAD {tag_vol_cad}")

    gmsh.model.mesh.clear([(3, tag_vol_malla)])
    # 3. We inject internal nodes to CAD (we use [] because there is no u, v in 3D)
    if len(nodeTags3D) > 0:
        gmsh.model.mesh.addNodes(3, tag_vol_cad, nodeTags3D, coords3D, [])
    gmsh.model.mesh.addElements(3, tag_vol_cad, elemTypes3D, elemTags3D, elemNodeTags3D)

gmsh.model.mesh.removeDuplicateNodes()

# ==============================================================================
# 5. HIGH ORDER CURVING AND ELASTIC OPTIMIZATION
# ==============================================================================
print(f"\nElevating the topology to Order {args.target_order}...")
gmsh.model.mesh.setOrder(args.target_order)

print("Applying Fast Curving optimization...")

# Multithreading (uses all CPU cores), that's why we put "0"
gmsh.option.setNumber("General.NumThreads", 0)

# Activate Fast Curving
gmsh.option.setNumber("Mesh.HighOrderOptimize", 4)
gmsh.option.setNumber("Mesh.HighOrderFastCurvingNewAlgo", 1)
gmsh.option.setNumber("Mesh.HighOrderCurveOuterBL", 2)

# Execute
gmsh.model.mesh.optimize("HighOrderFastCurving")

## ==============================================================================
## 6. QUALITY REVIEW (JACOBIANS)
## ==============================================================================
#print("\nAnalyzing the quality of the high-order mesh...")
#
## We configure the AnalyseMeshQuality plugin of Gmsh [4]
#gmsh.plugin.setNumber("AnalyseMeshQuality", "JacobianDeterminant", 1)  # Evaluate Jacobian determinant
#gmsh.plugin.setNumber("AnalyseMeshQuality", "ICNMeasure", 1)           # Evaluate SICN condition
#gmsh.plugin.setNumber("AnalyseMeshQuality", "CreateView", 1)           # Create visual views (color maps)
#gmsh.plugin.setNumber("AnalyseMeshQuality", "DimensionOfElements", -1) # Analyze only the highest dimension (3D volume)
#
## We execute the plugin
#gmsh.plugin.run("AnalyseMeshQuality")

# Force Gmsh to save all elements
gmsh.option.setNumber("Mesh.SaveAll", 1) 

output_name = args.output
print(f"\nSaving final mesh to: {output_name}")
gmsh.write(output_name)

# # View the result visually
# print("Opening the graphical interface...")
# gmsh.fltk.run() 
# gmsh.finalize()
