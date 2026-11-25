# Unified format for sample-based activity data

*English below · [Français plus bas](#français)*

One notebook that reads survey exports of **Collect Earth** and **Collect Earth Online** (any form, any country) and puts
them in **one format, the same for every survey**: one row per plot and year, 41 columns. From that format it builds the
history of each plot, applies the country's rules, and gives the areas with their standard errors and the files for the
IPCC inventory software and mocaredd.

Nothing is decided by the code: what the interpreters recorded is kept as it is (*recorded*), and the country's choices
are written once and applied the same way (*reported*). Every choice is optional and does nothing when left empty.

## Steps

| Step | What it does | You get |
|:--|:--|:--|
| 1 | Reads one file, several files separated by `;`, or a folder (e.g. one Collect Earth CSV per operator) | |
| 2 | Describes the survey; shows how each land answer was read; the lexicon of the words read (land names, activity words) | `_step2_survey_structure_` HTML, `_step2_lexicon_` Excel |
| 2b | One sample, its answers and the years built from them (optional) | `_step2_sample_` HTML |
| 3 | Quality check: the same plot twice (always stops), the same place, gaps in the years, changes against the land | `_step3_errors_`, `_step3_to_correct_` CSV |
| 4 | The unified format, with the canopy before and after as recorded (nothing to fill) | `_step4_unified_format_` CSV |
| 5 | The pairs of years and the history (years side by side) | `_step5_pairs_`, `_step5_history_` CSV |
| 6 | The country's rules, only if needed, in one workbook: transitions between forest types, canopy cover transitions, reclassify, merge | `_step6_classes_recorded_` / `_reported_` CSV, `_step5_history_reported_` |
| 7 | Areas and standard errors (systematic or stratified): of each class per pair of years, of each land class per year, of each cell of the matrices; transitions for mocaredd | `_step7_` CSV and Excel (`_step7_matrices_`: sheets *Areas by year*, and each matrix in plots, hectares and SE) |
| 8 | Units of land for the IPCC inventory software | `_step8_` Excel |
| 9 | Review of a few complex samples, chosen at random (optional) | `_step9_review_samples_` HTML and CSV |
| 10 | The activity of a period (e.g. reference or monitoring): each plot gets one REDD+ activity from its history (history lookup table), then the area of each activity with its SE and 90% CI | `_step10_period_` Excel (sheets areas, plots, histories) |

## Try it with the demo data

The folder `demo_data/` holds **fake data only**: the exports are made by `tools/make_demo_data.py` (made-up classes,
coordinates and operators); the files of `country_choices/` are fake examples in the layout of a country's files. Nothing
comes from a country. The folder `tools/` also holds `land_names_built_in.csv`: the names of land the
notebook knows, for each IPCC category (the list `IPCC_NAMES` in Step 0 of the notebook, written out for transparency).
`tools/activity_words_built_in.csv`: the activity words read in the history lookup table of Step 10 (English, French,
Spanish, Portuguese); a country adds its own in the sheet `activities` of the lexicon.

| File | Used in |
|:--|:--|
| `exports/demo_collect_earth_operator_A.csv`, `..._B.csv` | Step 1: write the folder `demo_data/exports` in `file_path` (the two operator files are put together) |
| `country_choices/demo_lexicon.xlsx` | Step 2: `lexicon_file`. Sheet `lexicon` (land names: `name`, `IPCC category`) and sheet `activities` (words of the history lookup table: `word`, `activity`), each with the built-in words and a few fake words added by a country (e.g. monte, gain) |
| `country_choices/demo_country_rules.xlsx` | Step 6: the country rules workbook, *use my filled file*. One sheet per kind of rule, each optional (an empty sheet is not used): `lookup` (`from_sub`, `to_sub`, `classification`), `canopy` (`from_cc`, `to_cc`, `classification`, optional `forest_type`; the demo exports have no canopy, so it shows the layout only), `category changes` (`sub`, `new category`: reclassify), `subclass merges` (`sub`, `merged into`: merge); other columns are notes |
| `country_choices/demo_period_history_lookup.xlsx` | Step 10: *use my filled file*. Sheet `history_lookup` (`history`, `redd_activity`); `plots` and `comment` are notes |

Settings for the demo:

| Step | Field | Value |
|:--|:--|:--|
| 1 | `file_path` | `demo_data/exports` |
| 2 | `end_year`, `start_year`, `survey_name` | `2024`, `2013`, `Demo` |
| 2 | `lexicon_choice`, `lexicon_file` (optional) | *use my file*, `demo_data/country_choices/demo_lexicon.xlsx` |
| 6 | `lookup_choice`, `lookup_file` | *use my filled file*, `demo_data/country_choices/demo_country_rules.xlsx` (reclassify, merge and canopy are read from its sheets) |
| 7 | `total_area_ha`, `sampling_design` | `1000000`, *systematic* |
| 8 | `subcategory_choice` | *make the template*, then *use my filled file* with the template |
| 10 | `period_start`, `period_end`, `history_lookup_choice`, `history_lookup_file` | `2014`, `2024`, *use my filled file*, `demo_data/country_choices/demo_period_history_lookup.xlsx` |

The demo areas are not meaningful: the data are random.

## Run it

- **Colab:** open `unified_format_notebook.ipynb` from GitHub (File > Open notebook > GitHub). To use the demo files with the
  paths above, first get the repository into Colab: run `!git clone <repository url>` and `%cd <repository name>` in a
  new cell, then run the cells in order. Or leave a file field empty: the step shows a button to upload the file(s)
  (Step 1 accepts several files at once).
- **On a computer:** Python 3.10 or later, `pip install -r requirements.txt`, then Jupyter. Write the paths in the fields.
- Step 0 installs `xlsxwriter`, `reverse_geocoder` and `pycountry` if they are missing (the country is found from the
  location of the plots; `survey_name` replaces it).

## Your own data

Keep the survey exports in one folder and the country's files (lookups, lexicon, history lookup) in another: a folder given in `file_path` is read as exports (a file that is not a survey export is left out, with a message). Put them in a folder of your own (e.g. `data/`, which is ignored by git). **Do not commit survey data.**

## Main choices

- **Year** = the land at 31 December; a change in the pair 2016-2017 happened in 2017.
- **Include the year before a period**: the changes of 2020 are in the pair 2019-2020, so for a period 2020-2024 Step 2
  starts at 2019 (`start_year`).
- **No interpolation**: a year is either recorded (*raw*) or carried from the year recorded before (*filled*).
- **The same plot id twice** stops the notebook: the country decides which interpretation to keep.
- **Canopy before and after**: Step 4 records where the canopy changes from one year to the next (`tree_cover_before`,
  `tree_cover_after`, `tree_cover_change` = decrease / increase / stable), as the survey wrote it: classes, numbers or words.
  Nothing to fill there. What a canopy change means in stable forest is the country's choice, in the sheet `canopy` of the
  country rules workbook of Step 6, with the same words as the sheet `lookup` (Degradation, Enhancement, Stable forest, Not
  possible). Most countries do not record the canopy and leave that sheet empty.
- **One file per decision-maker and moment**: the land-name lexicon (Step 2), the country rules workbook (Step 6), the IPCC
  subcategories (Step 8), the history lookup (Step 10). Each is given the same way: a choice, and a path (in Colab: leave the
  path empty and an upload button appears).
- **Land names**: the six IPCC categories are recognised in several languages (e.g. *forest, forêt, bosque, floresta,
  F, FL*: `tools/land_names_built_in.csv`); a name not recognised is added by the country to the lexicon of Step 2
  (sheet `lexicon`, columns `name` and `IPCC category`, e.g. *monte | Forest land*), read together with the built-in names.
  The same lexicon holds the country's words for the activities of its history lookup table (sheet `activities`, e.g.
  *gain | Afforestation*), so a table written with its own words or in another language works as it is. A national class counted in another
  category is a choice of Step 6 (*reclassify*), only when needed.
- **Estimator**: stratified (one stratum when systematic): area = A · Σ W_h p_h, variance = Σ W_h² p_h (1 − p_h) / (n_h − 1)
  (Cochran 1977; Olofsson et al. 2014).

---

## Français

Un notebook qui lit les exports d'enquête de **Collect Earth** et **Collect Earth Online** (tout formulaire, tout pays)
et les met dans **un seul format, le même pour toutes les enquêtes** : une ligne par placette et par année, 41 colonnes.
À partir de ce format, il construit l'historique de chaque placette, applique les règles du pays et donne les superficies
avec leurs erreurs standard, ainsi que les fichiers pour le logiciel d'inventaire du GIEC et mocaredd.

Le code ne décide rien : ce que les interprètes ont enregistré est gardé tel quel (*recorded*), et les choix du pays sont
écrits une fois et appliqués de la même façon (*reported*). Chaque choix est facultatif ; laissé vide, il ne fait rien.

**Essayer avec les données de démonstration** : le dossier `demo_data/` ne contient que des **données fictives** (classes,
coordonnées et opérateurs inventés). Les réglages sont dans le tableau de la partie anglaise.

**Colab** : ouvrir le notebook depuis GitHub ; pour les fichiers de démonstration, exécuter d'abord `!git clone <adresse du dépôt>` puis `%cd <nom du dépôt>`, ou laisser un champ de fichier vide pour charger les fichiers. **Jupyter** : `pip install -r requirements.txt`.

**Vos données** : gardez les exports dans un dossier et les fichiers du pays (lookups, lexique, history lookup) dans un autre ; placez les exports dans votre propre dossier (par exemple `data/`, ignoré par git). **Ne publiez pas de
données d'enquête.**
