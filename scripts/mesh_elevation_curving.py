# -*- coding: utf-8 -*-
"""
Script: mesh_elevation_curving.py
Description: A versatile CLI tool to map and project a linear/low-order mesh 
             onto an analytical CAD geometry. It automatically injects nodes to 
             elevate the topological order and applies High-Order Fast Curving.
"""

import gmsh
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Mesh curving and order elevation tool via Gmsh API.")
    parser.add_argument("--cad", required=True, help="Input CAD file (e.g., model.step)")
    parser.add_argument("--mesh", required=True, help="Input mesh file (e.g., mesh_g1.msh)")
    parser.add_argument("--output", required=True, help="Output mesh file name (e.g., mesh_g2.msh)")
    parser.add_argument("--target_order", type=int, required=True, help="Target geometric order (e.g., 2, 3, 4)")
    return parser.parse_args()

def main():
    args = parse_arguments()
    gmsh.initialize()

    # ==============================================================================
    # 1. Load CAD and Mesh dynamically
    # ==============================================================================
    print(f"Loading CAD model: {args.cad}...")
    gmsh.model.occ.importShapes(args.cad)
    gmsh.model.occ.synchronize()

    print(f"Reading original mesh: {args.mesh}...")
    gmsh.merge(args.mesh)

    # ==============================================================================
    # 2. AUTOMATIC TAG DETECTION & PHYSICAL GROUPS
    # ==============================================================================
    print("\nAutomatically detecting entities...")
    surf_cad, surf_malla = [], []
    vol_cad, vol_malla = [], []

    for dim, tag in gmsh.model.getEntities(2):
        entity_type = gmsh.model.getType(dim, tag).lower()
        elemTypes, elemTags, _ = gmsh.model.mesh.getElements(2, tag)
        num_elems = sum(len(t) for t in elemTags)
        if "discrete" not in entity_type: surf_cad.append(tag)
        if num_elems > 0: surf_malla.append(tag)

    for dim, tag in gmsh.model.getEntities(3):
        entity_type = gmsh.model.getType(dim, tag).lower()
        elemTypes, elemTags, _ = gmsh.model.mesh.getElements(3, tag)
        num_elems = sum(len(t) for t in elemTags)
        if "discrete" not in entity_type: vol_cad.append(tag)
        if num_elems > 0: vol_malla.append(tag)

    if not surf_cad or not surf_malla or not vol_cad or not vol_malla:
        raise RuntimeError("Failed to properly identify CAD/mesh entities.")

    # Remove previous names and create standardized PIDs for PyHOPE
    gmsh.model.removePhysicalGroups([])
    gmsh.model.removePhysicalName("fluid")
    gmsh.model.removePhysicalName("skin")
    gmsh.model.addPhysicalGroup(3, vol_cad, name="fluid")
    gmsh.model.addPhysicalGroup(2, surf_cad, name="skin")

    # ==============================================================================
    # 3. SURFACE & VOLUME TRANSFER (Mapping to exact CAD)
    # ==============================================================================
    print("\nReconstructing surfaces and volumes onto CAD...")
    
    # Surfaces mapping using (u, v) parametrization
    for tag_surf_malla in surf_malla:
        nodeTags, coords, _ = gmsh.model.mesh.getNodes(2, tag_surf_malla)
        elemTypes2D, elemTags2D, elemNodeTags2D = gmsh.model.mesh.getElements(2, tag_surf_malla)
        if len(nodeTags) == 0: continue
        tag_surf_cad = surf_cad[0] # Note: Assuming 1-1 correspondence
        uvs = gmsh.model.getParametrization(2, tag_surf_cad, coords)
        gmsh.model.mesh.clear([(2, tag_surf_malla)])
        gmsh.model.mesh.addNodes(2, tag_surf_cad, nodeTags, coords, uvs)
        gmsh.model.mesh.addElements(2, tag_surf_cad, elemTypes2D, elemTags2D, elemNodeTags2D)

    # Volumes mapping
    for tag_vol_malla in vol_malla:
        nodeTags3D, coords3D, _ = gmsh.model.mesh.getNodes(3, tag_vol_malla)
        elemTypes3D, elemTags3D, elemNodeTags3D = gmsh.model.mesh.getElements(3, tag_vol_malla)
        if len(elemTypes3D) == 0: continue
        tag_vol_cad = vol_cad[0]
        if tag_vol_malla == tag_vol_cad: continue
        gmsh.model.mesh.clear([(3, tag_vol_malla)])
        if len(nodeTags3D) > 0:
            gmsh.model.mesh.addNodes(3, tag_vol_cad, nodeTags3D, coords3D, [])
        gmsh.model.mesh.addElements(3, tag_vol_cad, elemTypes3D, elemTags3D, elemNodeTags3D)

    gmsh.model.mesh.removeDuplicateNodes()

    # ==============================================================================
    # 4. ORDER ELEVATION & FAST CURVING
    # ==============================================================================
    print(f"\nElevating topology to Order {args.target_order}...")
    gmsh.model.mesh.setOrder(args.target_order)

    print("Applying Fast Curving optimization...")
    gmsh.option.setNumber("General.NumThreads", 0)
    gmsh.option.setNumber("Mesh.HighOrderOptimize", 4)
    gmsh.option.setNumber("Mesh.HighOrderFastCurvingNewAlgo", 1)
    gmsh.option.setNumber("Mesh.HighOrderCurveOuterBL", 2)
    
    gmsh.model.mesh.optimize("HighOrderFastCurving")

    # ==============================================================================
    # 5. EXPORT
    # ==============================================================================
    gmsh.option.setNumber("Mesh.SaveAll", 1) 
    print(f"\nSaving final mesh to: {args.output}")
    gmsh.write(args.output)
    
    gmsh.finalize()

if __name__ == "__main__":
    main()
