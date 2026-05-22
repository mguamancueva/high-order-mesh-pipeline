# -*- coding: utf-8 -*-
"""
Script: reassign_physical_groups.py
Description: A CLI tool to prepare an already curved/high-order mesh for PyHOPE ingestion.
             It bypasses CAD projection and focuses purely on detecting existing 
             mesh entities, cleaning previous tags, and reconstructing the Physical 
             Groups (PIDs) required by the CFD solver's boundary conditions.
"""

import gmsh
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="PID reassignment tool for pre-curved high-order meshes.")
    parser.add_argument("--mesh", required=True, help="Input curved mesh file (e.g., mesh_g2.msh)")
    parser.add_argument("--output", required=True, help="Output mesh file name (e.g., mesh_g2_ready.msh)")
    return parser.parse_args()

def main():
    args = parse_arguments()
    gmsh.initialize()

    # ==============================================================================
    # 1. Load the original high-order mesh
    # ==============================================================================
    print(f"Reading original mesh: {args.mesh}...")
    gmsh.merge(args.mesh)

    # ==============================================================================
    # 2. AUTOMATIC TAG DETECTION & PHYSICAL GROUP CREATION
    # ==============================================================================
    print("\nAutomatically detecting entities...")

    surf_malla = []
    vol_malla = []

    # --- Surfaces ---
    for dim, tag in gmsh.model.getEntities(2):
        entity_type = gmsh.model.getType(dim, tag).lower()
        elemTypes, elemTags, _ = gmsh.model.mesh.getElements(2, tag)
        num_elems = sum(len(t) for t in elemTags)

        if num_elems > 0:
            surf_malla.append(tag)
            print(f"[SURF] Tag: {tag} | Type: {entity_type} | Elements: {num_elems}")

    # --- Volumes ---
    for dim, tag in gmsh.model.getEntities(3):
        entity_type = gmsh.model.getType(dim, tag).lower()
        elemTypes, elemTags, _ = gmsh.model.mesh.getElements(3, tag)
        num_elems = sum(len(t) for t in elemTags)

        if num_elems > 0:
            vol_malla.append(tag)
            print(f"[VOL] Tag: {tag} | Type: {entity_type} | Elements: {num_elems}")

    if not surf_malla or not vol_malla:
        raise RuntimeError("Failed to properly identify mesh surfaces or volumes.")

    # Remove previous names and create standardized PIDs for PyHOPE
    gmsh.model.removePhysicalGroups([])
    gmsh.model.removePhysicalName("fluid")
    gmsh.model.removePhysicalName("skin")
    gmsh.model.addPhysicalGroup(3, vol_malla, name="fluid")
    gmsh.model.addPhysicalGroup(2, surf_malla, name="skin")

    # ==============================================================================
    # 3. EXPORT
    # ==============================================================================
    gmsh.option.setNumber("Mesh.SaveAll", 1) 
    
    print(f"\nSaving final mesh to: {args.output}")
    gmsh.write(args.output)
    
    gmsh.finalize()

if __name__ == "__main__":
    main()
