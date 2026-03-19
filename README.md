# High-Order Mesh Generation Pipeline for Spectral Element Solvers

![Status](https://img.shields.io/badge/Status-Work_in_Progress-orange)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Format](https://img.shields.io/badge/Format-HDF5%20%7C%20CGNS-green)

## 📌 Overview
This repository contains the scripts, workflows, and documentation developed during my BSc Aerospace Engineering Thesis at UPM. The core objective is to create a robust pipeline to generate, translate, and optimize high-order computational meshes to achieve maximum accuracy in fluid studies. 

The workflow connects commercial meshing software (**ANSA**) with open-source high-order pre-processors (**PyHOPE**) to feed spectral element solvers (**HORSES3D**). 

## ⚙️ The Pipeline Architecture

1.  **Base Meshing (ANSA):** Generation of unstructured volumetric meshes. Elements are converted from Tetrahedra to Hexahedra (Split to Hexas) to align with the flow direction, significantly reducing numerical diffusion and calculation instability.
2.  **Geometric Order Elevation:** Upgrading linear meshes to quadratic (Order 2) to faithfully capture complex curvatures, such as spherical boundaries.
3.  **Data Translation (PyHOPE):** * Reading the `.cgns` file exported from ANSA using the robust 3.2.0 library version and HDF5 format for parallel processing efficiency.
    * Converting Serendipity elements (HEXA20) to Lagrange elements (HEXA27) by injecting internal nodes required for high-order polynomial equations.
    * Exporting the final geometry to `.h5` format.
4.  **Solver (HORSES3D):** Elevating the polynomial/solution order to solve Navier-Stokes equations with extreme resolution without further deforming the base mesh.

## 🔬 Current Research & Challenges
* **Mesh Curving Techniques:** Evaluating different curving methods for unstructured meshes, moving beyond standard Agglomeration (which is suited mostly for structured meshes).
* **Volumetric Deformation:** Analyzing *Mesh Deformation* strategies to prevent inverted elements (negative Jacobians) near boundaries. Currently comparing the computational efficiency of the **Laplace model** versus the superior mesh quality and deep deformation penetration of the **Neo-Hookean model**.

## 🛠️ Code & Utilities
* `scripts/`: Python utilities to automate topological order elevation via the Gmsh API and streamline the high-order pre-processing workflow.
* `config_files/`: Templates for `parameter.ini` files for PyHOPE execution.

---
*Note: This repository is part of an ongoing Bachelor's Thesis. Full scripts and detailed documentation will be updated progressively.*
