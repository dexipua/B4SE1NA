# Graph Report - B4SE1NA  (2026-11-16)

## Corpus Check
- 24 files · ~19,286 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .csv 2, .toml 1)

## Summary
- 532 nodes · 1175 edges · 25 communities (13 shown, 12 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.87)
- Token cost: 159,110 input · 0 output

## Graph Freshness
- Built from commit: `a9f312aa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Streamlit App UI
- Normalization & Scoring Core
- Data360 Data Loader
- Plotly Charts
- decode
- App Smoke Tests
- Project Docs & Design Rules
- Translations & Country Names
- test_quiz.py
- Ngrok Public Launcher
- Presets, Query & Link Encoding
- settings.py
- quiz_settings
- answered_count
- Python Dependencies

## God Nodes (most connected - your core abstractions)
1. `t()` - 32 edges
2. `main()` - 25 edges
3. `label()` - 25 edges
4. `quiz_settings()` - 19 edges
5. `match()` - 18 edges
6. `sidebar()` - 17 edges
7. `profile_tab()` - 17 edges
8. `lang()` - 16 edges
9. `tr()` - 16 edges
10. `quiz_result()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `The 10 indicators (Data360 ids, WDI/WGI)` --semantically_similar_to--> `Dataset spec (iso3 index, Data360 indicator ids, year columns)`  [INFERRED] [semantically similar]
  docs/PROJECT_GUIDE.md → CLAUDE.md
- `Score = (1 - weighted RMS distance) x 100` --semantically_similar_to--> `match() reference implementation`  [INFERRED] [semantically similar]
  docs/PROJECT_GUIDE.md → CLAUDE.md
- `Module reference (every function)` --semantically_similar_to--> `One module per concern architecture`  [INFERRED] [semantically similar]
  docs/PROJECT_GUIDE.md → CLAUDE.md
- `rank()` --calls--> `t()`  [EXTRACTED]
  tests/test_app.py → i18n.py
- `open_quiz()` --calls--> `t()`  [EXTRACTED]
  tests/test_app.py → i18n.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Ranking pipeline: data -> normalize -> weights -> match -> points lost** — docs_project_guide_dataset_csv, docs_project_guide_normalization, docs_project_guide_weight_expansion, docs_project_guide_score_formula, docs_project_guide_points_lost [EXTRACTED 1.00]
- **Public ngrok access with local-only refresh** — readme_public_link_ngrok, claude_ngrok_launcher, docs_project_guide_local_only_refresh [INFERRED 0.85]
- **Sources that produce user settings (presets, quiz, shared link)** — claude_modes, docs_project_guide_preference_quiz, docs_project_guide_shareable_links, docs_project_guide_session_state [INFERRED 0.85]

## Communities (25 total, 12 thin omitted)

### Community 0 - "Streamlit App UI"
Cohesion: 0.06
Nodes (37): apply_preset(), apply_quiz(), bullet_list(), compare_tab(), dark(), explore_tab(), filter_regions(), init_state() (+29 more)

### Community 1 - "Normalization & Scoring Core"
Cohesion: 0.06
Nodes (25): min_max(), normalize(), winsorize(), category_levels(), expand_weights(), loss_by_category(), match(), points_lost() (+17 more)

### Community 2 - "Data360 Data Loader"
Cohesion: 0.06
Nodes (21): Indicator, download_dataset(), fetch_countries_metadata(), fetch_indicator(), fetch_indicators(), fetch_rows(), get_json(), load_dataset() (+13 more)

### Community 3 - "Plotly Charts"
Cohesion: 0.06
Nodes (31): category_profile(), category_scatter(), gap_bar(), hyphenate(), loss_bar(), palette(), Palette, radar() (+23 more)

### Community 4 - "decode"
Cohesion: 0.17
Nodes (5): decode(), _parse(), test_invalid_params_are_dropped(), test_preset_settings_cover_every_setting(), test_values_snap_to_slider_steps()

### Community 5 - "App Smoke Tests"
Cohesion: 0.06
Nodes (20): app(), open_quiz(), test_address_bar_follows_settings(), test_country_profile_and_data_info(), rank(), test_default_mode_shows_top_five(), test_download_and_values_table_render(), test_explore_tab_switches_axes() (+12 more)

### Community 6 - "Project Docs & Design Rules"
Cohesion: 0.07
Nodes (29): Country Matcher (project instructions), Dataset spec (iso3 index, Data360 indicator ids, year columns), match() reference implementation, Modes: best, my ideal, similar, presets, .ngrok/start.py launcher, Country Matcher Complete Project Guide, Big picture data flow (World Bank -> CSV -> normalize -> match -> explain/charts), data/dataset.csv and mock_dataset.csv (+21 more)

### Community 7 - "Translations & Country Names"
Cohesion: 0.06
Nodes (13): _alpha2(), country_names(), name(), load_locales(), page_text(), raw_frames(), test_domain_labels_covered(), test_every_country_is_localized() (+5 more)

### Community 8 - "test_quiz.py"
Cohesion: 0.09
Nodes (10): top_categories(), all_answer_combinations(), answers(), test_answers_shift_priorities(), test_every_effect_targets_a_known_criterion(), test_every_question_and_option_is_translated(), test_modest_dreams_only_lower_the_economy_target(), test_no_category_is_starved_or_dominant() (+2 more)

### Community 9 - "Ngrok Public Launcher"
Cohesion: 0.13
Nodes (5): find_token(), free_port(), main(), open_tunnel(), start_app()

### Community 10 - "Presets, Query & Link Encoding"
Cohesion: 0.16
Nodes (7): encode(), query(), test_quiz_settings_drive_the_ranking(), make_state(), test_only_relevant_settings_are_written(), test_query_uses_ideal_only_in_ideal_mode(), test_round_trip_restores_every_setting()

### Community 11 - "settings.py"
Cohesion: 0.17
Nodes (3): _join(), preset_settings(), profile_settings()

### Community 13 - "quiz_settings"
Cohesion: 0.12
Nodes (9): category_weights(), chosen_options(), desired_levels(), indicator_mults(), Option, Question, quiz_settings(), test_desired_level_is_the_most_modest_answer() (+1 more)

## Knowledge Gaps
- **6 isolated node(s):** `Python Dependencies (streamlit, pandas, numpy, plotly, requests, pytest, babel, pycountry, ngrok)`, `How to extend (indicator, language, preset, quiz question, chart)`, `Glossary`, `What happens on one page load (main() sequence)`, `Features list (15 languages, ranking, why-not, compare, share link, profile)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 252 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `Plotly Charts` to `Streamlit App UI`, `App Smoke Tests`, `Translations & Country Names`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **What connects `Python Dependencies (streamlit, pandas, numpy, plotly, requests, pytest, babel, pycountry, ngrok)`, `How to extend (indicator, language, preset, quiz question, chart)`, `Glossary` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Streamlit App UI` be split into smaller, more focused modules?**
  _Cohesion score 0.06392405063291139 - nodes in this community are weakly interconnected._
- **Why does `quiz_settings()` connect `quiz_settings` to `Streamlit App UI`, `test_quiz.py`, `Presets, Query & Link Encoding`, `settings.py`, `answered_count`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `Normalization & Scoring Core` be split into smaller, more focused modules?**
  _Cohesion score 0.06010230179028133 - nodes in this community are weakly interconnected._
- **Why does `load_dataset()` connect `Data360 Data Loader` to `Streamlit App UI`, `Normalization & Scoring Core`, `App Smoke Tests`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Should `Data360 Data Loader` be split into smaller, more focused modules?**
  _Cohesion score 0.06334841628959276 - nodes in this community are weakly interconnected._