# DPMKG: Digital-Physical Manufacturing Knowledge Graph

This repository provides an implementation of DPMKG described in the paper: A knowledge graph construction and causal
structure mining approach for non-stationary manufacturing systems.
<br>
*Declaration: Due to the lack of time, the documentation and code comments in this repository are still being refined.
More details will be provided in the future, with continuous updates as the research progresses.*

## Abstract

Knowledge graph (KG) is a method for managing multi-source heterogeneous data and forming knowledge for reasoning using
graph structure. It has been extensively utilized in manufacturing systems to promote the advancement of intelligent
manufacturing. In non-stationary manufacturing systems, the machining performance of individual elements demonstrates
variability and dynamic fluctuations. The significant dynamics and uncertainties of a manufacturing system bring great
challenges to KG's modeling, construction, and reasoning. To overcome these challenges, this paper proposes a
Digital-Physical Manufacturing Knowledge Graph (DPMKG) construction and reasoning method. Firstly, an ontology-based
knowledge representation model is developed to facilitate the integration of digital domain knowledge with the
description of physical domain performance fluctuations, thereby establishing the schema layer of DPMKG. Secondly, a
SysML model-driven construction pipeline is proposed to facilitate the correlation and integration of multi-source data
from both digital and physical domains, thereby establishing the instance layer of DPMKG. Thirdly, a causal structure
mining method for DPMKG is developed to enhance the analytical and reasoning capabilities in non-stationary
manufacturing systems. Finally, an aero-engine casing machining system is employed as a case study to establish the
DPMKG, and reasoning is performed on the process quality prediction task. The case study reveals that the proposed DPMKG
modeling, construction, and reasoning approach can effectively describe and analyze performance fluctuations in the
physical domain of a non-stationary manufacturing system. By integrating digital and physical domain knowledge, the
extensive data can be effectively leveraged to generate knowledge for reasoning, thereby facilitating intelligent and
refined control of non-stationary manufacturing systems.
<div align="center">
<img src="/figure/Fig1.png"  width="500" />
</div>

## DPMKG Construction

The attributes of machining elements within the physical domain undergo dynamic changes in real-time throughout the
process. Consequently, the information necessary to describe these variations is dispersed across various processes,
departments, and data sources. This fragmentation results in structural and semantic conflicts among the data,
complicating the establishment of dynamic associations between characterization data and individual machining elements.
This section presents a SysML model-driven construction pipeline for DPMKG that facilitates the efficient extraction,
integration, and graph construction of multi-source heterogeneous data instances.

<div align="center">
<img src="/figure/Fig4.png"  width="800" />
</div>

In the [construction](/construction) folder, we provide most of the code for the DPMKG build tool. It includes a
[prototype system](/construction/instance_extraction) for instance extraction and graph construction. The back-end is
built on springboot and the front-end is built on Vue. In addition, we provide [python scripts](/construction/KG_bulid)
for processing the case data in the paper and building the graph.
<br>
At present, the open source code contains the complete build pipeline framework, but some specific construction methods
are still under research and are not publicly available. We will update this repository as relevant research is
published publicly.

## Causal Structure Mining

By reconstructing each node's causal embeddings and the causal effects between nodes, a knowledge graph reasoning model
is established for the given task. This repository exposes two parts of the code
for [dataset construction](/reasoning/data_process) and [model structure](/reasoning/causal_model).

<div align="center">
<img src="/figure/Fig6.png" width="500" />
</div>

## Data

Due to corporate confidentiality requirements, we are only authorized to disclose a portion of the data that does not
involve specific process information and production information, and the disclosed data has been anonymized. It includes
part of the [original data tables](/data/database_table) extracted from the information system database and
the [processed instance data](/data/case_instance.xlsx) for training the KG inference model.

## Figure

The high score rate version of all the [figures](/figure) in the paper is provided.