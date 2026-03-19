# Case Study 1: High-Order Mesh Generation for a Spherical Domain

## 1. Geometry and Base Meshing (ANSA)
The process begins with defining the geometry of a sphere and its surrounding outer domain. ]ANSA detects two volumes: the interior of the sphere and the fluid volume comprised between the side walls and the spherical outer wall. Batch Mesh is employed for this task, utilizing first-order triangular elements (Trias) for the surfaces and tetrahedral elements (TetraRapid) for the outer fluid volume.

## 2. Conversion to Hexahedra (Split to Hexas)
Tetrahedra generate numerical diffusion because the flow crosses their faces diagonally. To avoid this and improve the solver's mathematical accuracy, the tetrahedral mesh undergoes a conversion process (Split to Hexas). Hexahedra allow the blocks to be aligned with the flow direction, achieving a more stable calculation and practically zero diffusion error.

## 3. Export (CGNS Format)
The hexahedral mesh is exported using the aerodynamic industry standard, CGNS. The critical parameters configured are:
* **HDF5 Format:** Selected over ADF because it has no size limit and allows for parallel read/write operations in supercomputing clusters.
* **Library Version 3.2.0:** Chosen for its extreme stability and strict compatibility with research codes like PyHOPE.
* **Scale (Target: meter):** Fundamental to scale the geometry to the International System to ensure the physics of the problem remain unaltered in the solver.

## 4. Order Elevation and Translation (PyHOPE)
The `.cgns` file is processed in a Linux environment using PyHOPE to obtain an Order 2 mesh, which increases the computational time by approximately 47% compared to the linear mesh. 

The critical step here is the **mathematical conversion of elements**: PyHOPE converts the Serendipity-type hexahedra (HEXA20, with nodes only on vertices and edges) exported by ANSA into Lagrange-type hexahedra (HEXA27). The code injects the missing nodes in the center of the faces and the internal volume, an essential requirement for the solver's polynomial equations to function correctly.
