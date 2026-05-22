# High-Order Mesh Generation Pipeline for CFD 🚀

This repository contains an automated, Python-based pipeline for the pre-processing and generation of high-order computational meshes. It is designed to map linear or low-order meshes onto exact analytical CAD geometries, elevating their topological order for use in high-order Computational Fluid Dynamics (CFD) solvers (such as HORSES3D).

This work was developed as part of a Final Degree Project (TFG) in Aerospace Engineering at the Universidad Politécnica de Madrid (UPM), focusing on Aerospace Vehicles and advanced CFD meshing techniques.

---

## 📂 Repository Structure

The project is modular, separating execution scripts from configuration templates and test environments:

```text
📁 high-order-mesh-pipeline/
├── 📁 scripts/                  
│   ├── 🐍 mesh_elevation_curving.py       # Injects nodes and curves mesh projecting onto exact CAD (u,v).
│   ├── 🐍 reassign_physical_groups.py     # Cleans topology and reassigns PIDs for pre-curved meshes.
│   └── 🐚 run_pyhope_cesvima.sh           # Standard SLURM job script for PyHOPE in HPC environments.
│
├── 📁 cases_templates/
│   ├── 📁 test_geometry/                  # Lightweight CAD (.step) and linear mesh (.msh) for testing.
│   ├── 📁 Gmsh/                           # PyHOPE parameter templates (.ini) for Gmsh inputs.
│   └── 📁 CGNS/                           # PyHOPE parameter templates (.ini) for CGNS inputs (e.g., NASA CRM).
