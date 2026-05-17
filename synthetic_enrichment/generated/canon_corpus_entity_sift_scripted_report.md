# Canon Corpus Entity Sift — Scripted Report

## 1. Input / Output

- Input: `synthetic_enrichment/generated/canon_corpus_raw.jsonl`
- Output: `synthetic_enrichment/generated/canon_corpus_entity_sift_scripted.jsonl`
- Records: 486
- NLP status: spaCy disabled
- Validation: PASS

## 2. Old counts by semantic_class

| semantic_class | count |
|---|---|
| UNCLASSIFIED | 2251 |

## 3. New counts by semantic_class

| semantic_class | count |
|---|---|
| CREATIVE_WORK | 236 |
| EVENT | 58 |
| IDEA | 36 |
| METADATA | 0 |
| PERSON | 78 |
| PLACE | 25 |
| PROCESS | 0 |
| RELATIONSHIP | 30 |
| THING | 23 |

## 4. Counts by semantic_confidence

| confidence | count |
|---|---|
| high | 31 |
| low | 0 |
| medium | 455 |

## 5. Weaver review count

- Records needing Weaver review: 42

## 6. PROCESS / UNKNOWN

- PROCESS count: 0
- UNKNOWN count: 0
- Records with dictionary matches: 31
- Records classified by fallback/heuristics: 455

## 7. Top 100 PROCESS records and why they remain PROCESS

| id | dominant_noun_phrase | confidence | reason | source |
|---|---|---|---|---|

## 8. Top 100 UNKNOWN records and why

| id | dominant_noun_phrase | confidence | reason | source |
|---|---|---|---|---|

## 9. Top PERSON candidates

| id | dominant_noun_phrase | confidence | reason | source |
|---|---|---|---|---|
| canon_characters_characters_md_character_note_preface_preface_238_b1c639b31a | canon_characters_characters_md_character_note_preface_preface_238_b1c639b31a | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_hildebrand_von_hooplehopper_full_239_83b5eebc1e | canon_characters_characters_md_character_note_hildebrand_von_hooplehopper_full_239_83b5eebc1e | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_conrad_von_hooplehopper_sketched_240_310722467b | canon_characters_characters_md_character_note_conrad_von_hooplehopper_sketched_240_310722467b | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_adelram_von_hooplehopper_sketched_241_380393b726 | canon_characters_characters_md_character_note_adelram_von_hooplehopper_sketched_241_380393b726 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_margarethe_von_hooplehopper_full_242_ef5bb9bc7d | canon_characters_characters_md_character_note_margarethe_von_hooplehopper_full_242_ef5bb9bc7d | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_benedict_the_ash_faced_moderate_243_0c345daaf7 | canon_characters_characters_md_character_note_benedict_the_ash_faced_moderate_243_0c345daaf7 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_velma_the_snake_in_silk_moderate_244_a90671fb0b | canon_characters_characters_md_character_note_velma_the_snake_in_silk_moderate_244_a90671fb0b | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_lysander_von_hooplehopper_moderate_245_d65cf340af | canon_characters_characters_md_character_note_lysander_von_hooplehopper_moderate_245_d65cf340af | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_theresia_von_hooplehopper_sketched_246_3c5d5dcf34 | canon_characters_characters_md_character_note_theresia_von_hooplehopper_sketched_246_3c5d5dcf34 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_yssenda_von_hooplehopper_moderate_247_a60bffd19b | canon_characters_characters_md_character_note_yssenda_von_hooplehopper_moderate_247_a60bffd19b | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_sigismund_von_hooplehopper_moderate_248_51942707f4 | canon_characters_characters_md_character_note_sigismund_von_hooplehopper_moderate_248_51942707f4 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_isolde_von_hooplehopper_moderate_249_868fc0e202 | canon_characters_characters_md_character_note_isolde_von_hooplehopper_moderate_249_868fc0e202 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_ludolf_von_hooplehopper_sketched_250_23f83ea9a8 | canon_characters_characters_md_character_note_ludolf_von_hooplehopper_sketched_250_23f83ea9a8 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_lisette_von_hooplehopper_full_251_4c062c8cd6 | canon_characters_characters_md_character_note_lisette_von_hooplehopper_full_251_4c062c8cd6 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_professor_von_hooplehopper_full_252_a18304f0ee | canon_characters_characters_md_character_note_professor_von_hooplehopper_full_252_a18304f0ee | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_doctor_vorst_full_253_7550c8f98d | canon_characters_characters_md_character_note_doctor_vorst_full_253_7550c8f98d | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_pop_full_254_000c6ceec1 | canon_characters_characters_md_character_note_pop_full_254_000c6ceec1 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_jake_mccullen_full_255_61520536ed | canon_characters_characters_md_character_note_jake_mccullen_full_255_61520536ed | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_eli_mccullen_hook_only_256_0a14090318 | canon_characters_characters_md_character_note_eli_mccullen_hook_only_256_0a14090318 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_miss_slaytonia_vuorse_full_257_3fda916bbb | canon_characters_characters_md_character_note_miss_slaytonia_vuorse_full_257_3fda916bbb | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_miss_slaytonia_verse_moderate_258_9e73f44169 | canon_characters_characters_md_character_note_miss_slaytonia_verse_moderate_258_9e73f44169 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_the_weaver_full_259_af3818ac84 | canon_characters_characters_md_character_note_the_weaver_full_259_af3818ac84 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_wylus_kalyndros_hook_only_260_e90122f657 | canon_characters_characters_md_character_note_wylus_kalyndros_hook_only_260_e90122f657 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_dr_mariah_slayton_moderate_261_ede38359e2 | canon_characters_characters_md_character_note_dr_mariah_slayton_moderate_261_ede38359e2 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_dj_parallax_hook_only_262_bb80cbf3cd | canon_characters_characters_md_character_note_dj_parallax_hook_only_262_bb80cbf3cd | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_mistress_euphoria_blaze_sketched_263_332717459c | canon_characters_characters_md_character_note_mistress_euphoria_blaze_sketched_263_332717459c | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_gpt_sketched_264_52dc98c5e3 | canon_characters_characters_md_character_note_gpt_sketched_264_52dc98c5e3 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_claude_sketched_265_9ce5db3478 | canon_characters_characters_md_character_note_claude_sketched_265_9ce5db3478 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_otter_hook_only_266_337d6d8407 | canon_characters_characters_md_character_note_otter_hook_only_266_337d6d8407 | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_characters_characters_md_character_note_grok_sketched_267_999f252feb | canon_characters_characters_md_character_note_grok_sketched_267_999f252feb | medium | source path hint indicates PERSON: canon/characters/characters.md | canon/characters/characters.md |
| canon_open_threads_open_threads_md_open_thread_wylus_kalyndros_hook_only_303_60e5d0c31c | Wylus Kalyndros | high | explicit Slayverse dictionary match in BODY: Wylus Kalyndros | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_eli_mccullen_hook_only_304_28d5b2bdee | Eli McCullen | high | explicit Slayverse dictionary match in BODY: Eli McCullen | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_lisette_s_unnamed_companion_hook_only_305_b545358d00 | Lisette | high | explicit Slayverse dictionary match in BODY: Lisette | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_dj_parallax_hook_only_306_3d23e64bb5 | DJ Parallax | high | explicit Slayverse dictionary match in BODY: DJ Parallax | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_forbidden_suitcase_hook_only_308_b171bbad42 | Lisette | high | explicit Slayverse dictionary match in BODY: Lisette | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_jake_as_temporal_echo_of_doctor_vorst_resol_520b45725a | Doctor Vorst | high | explicit Slayverse dictionary match in BODY: Doctor Vorst | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_doctor_vorst_s_relationship_to_pop_316_d8d5ec35b9 | Doctor Vorst | high | explicit Slayverse dictionary match in BODY: Doctor Vorst | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_professor_s_father_317_65d7456668 | Doctor Vorst | high | explicit Slayverse dictionary match in BODY: Doctor Vorst | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_jake_as_temporal_echo_of_doctor_vorst_318_56e42c7845 | Doctor Vorst | high | explicit Slayverse dictionary match in BODY: Doctor Vorst | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_gap_between_theresia_1754_and_lisette_1_d34f867e2d | Lisette | high | explicit Slayverse dictionary match in BODY: Lisette | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_vuorse_s_capabilities_in_full_321_743aabc06a | VUORSE | high | explicit Slayverse dictionary match in BODY: VUORSE | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_sixth_summit_322_3caa26e0c5 | VUORSE | high | explicit Slayverse dictionary match in BODY: VUORSE | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_what_happened_to_the_other_federstahl_resea_803b58179a | Doctor Vorst | high | explicit Slayverse dictionary match in BODY: Doctor Vorst | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_codex_prophecy_324_ba0b2341d4 | Jake | high | explicit Slayverse dictionary match in BODY: Jake | canon/open_threads/open_threads.md |
| canon_slayverse_index_json_character_record_idx_ent_hildebrand_von_hooplehopper_361_758ca24f7c | canon_slayverse_index_json_character_record_idx_ent_hildebrand_von_hooplehopper_361_758ca24f7c | medium | record_type/extraction_kind indicates PERSON | canon/slayverse_index.json |
| canon_slayverse_index_json_character_record_idx_ent_conrad_von_hooplehopper_362_b3b61ec2f7 | canon_slayverse_index_json_character_record_idx_ent_conrad_von_hooplehopper_362_b3b61ec2f7 | medium | record_type/extraction_kind indicates PERSON | canon/slayverse_index.json |
| canon_slayverse_index_json_character_record_idx_ent_adelram_von_hooplehopper_363_005da28f46 | canon_slayverse_index_json_character_record_idx_ent_adelram_von_hooplehopper_363_005da28f46 | medium | record_type/extraction_kind indicates PERSON | canon/slayverse_index.json |
| canon_slayverse_index_json_character_record_idx_ent_margarethe_von_hooplehopper_364_98b7ccaeb3 | canon_slayverse_index_json_character_record_idx_ent_margarethe_von_hooplehopper_364_98b7ccaeb3 | medium | record_type/extraction_kind indicates PERSON | canon/slayverse_index.json |
| canon_slayverse_index_json_character_record_idx_ent_benedict_the_ash_faced_365_d5dda440cc | canon_slayverse_index_json_character_record_idx_ent_benedict_the_ash_faced_365_d5dda440cc | medium | record_type/extraction_kind indicates PERSON | canon/slayverse_index.json |
| canon_slayverse_index_json_character_record_idx_ent_velma_the_snake_in_silk_366_17a9a74ea7 | canon_slayverse_index_json_character_record_idx_ent_velma_the_snake_in_silk_366_17a9a74ea7 | medium | record_type/extraction_kind indicates PERSON | canon/slayverse_index.json |

## 10. Top PLACE candidates

| id | dominant_noun_phrase | confidence | reason | source |
|---|---|---|---|---|
| canon_open_threads_open_threads_md_open_thread_the_six_other_fissures_hook_only_310_86ebf06706 | Wyoming | high | explicit Slayverse dictionary match in BODY: Wyoming | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_six_other_fissures_as_counter_lineages__5a117a7e01 | Wyoming | high | explicit Slayverse dictionary match in BODY: Wyoming | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_velvet_underground_wyoming_hideaway_hoo_57b5fcc81b | McCullen Ranch | high | explicit Slayverse dictionary match in BODY: McCullen Ranch | canon/open_threads/open_threads.md |
| canon_open_threads_open_threads_md_open_thread_the_lattice_incident_timeline_315_f1fc4db62e | Berlin | high | explicit Slayverse dictionary match in BODY: Berlin | canon/open_threads/open_threads.md |
| canon_places_places_md_place_note_preface_preface_332_e464236be7 | canon_places_places_md_place_note_preface_preface_332_e464236be7 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_schloss_eisensang_moderate_333_8baa660032 | canon_places_places_md_place_note_schloss_eisensang_moderate_333_8baa660032 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_mirror_cavern_moderate_334_b7aacfff40 | canon_places_places_md_place_note_mirror_cavern_moderate_334_b7aacfff40 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_schloss_federstahl_full_335_8cda2317fb | canon_places_places_md_place_note_schloss_federstahl_full_335_8cda2317fb | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_mccullen_ranch_powder_river_basin_full_336_93f4b4e796 | canon_places_places_md_place_note_mccullen_ranch_powder_river_basin_full_336_93f4b4e796 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_the_wyoming_rift_full_337_d9456e3bb9 | canon_places_places_md_place_note_the_wyoming_rift_full_337_d9456e3bb9 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_the_velvet_archive_full_338_4c93022bc5 | canon_places_places_md_place_note_the_velvet_archive_full_338_4c93022bc5 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_club_cosmic_moderate_339_cb07abc604 | canon_places_places_md_place_note_club_cosmic_moderate_339_cb07abc604 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_federstahl_nebula_outpost_v_sketched_340_4994a6fa48 | canon_places_places_md_place_note_federstahl_nebula_outpost_v_sketched_340_4994a6fa48 | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_moonbase_opera_house_hook_only_341_dcf6be18ef | canon_places_places_md_place_note_moonbase_opera_house_hook_only_341_dcf6be18ef | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_places_places_md_place_note_the_velvet_underground_wyoming_hideaway_hook_only_342_bc26e51e2f | canon_places_places_md_place_note_the_velvet_underground_wyoming_hideaway_hook_only_342_bc26e51e2f | medium | source path hint indicates PLACE: canon/places/places.md | canon/places/places.md |
| canon_slayverse_index_json_place_record_idx_ent_schloss_eisensang_387_f0ea2faa7f | canon_slayverse_index_json_place_record_idx_ent_schloss_eisensang_387_f0ea2faa7f | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_slayverse_index_json_place_record_idx_ent_mirror_cavern_388_5f217e3f43 | canon_slayverse_index_json_place_record_idx_ent_mirror_cavern_388_5f217e3f43 | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_slayverse_index_json_place_record_idx_ent_schloss_federstahl_389_021efd506f | canon_slayverse_index_json_place_record_idx_ent_schloss_federstahl_389_021efd506f | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_slayverse_index_json_place_record_idx_ent_mcullen_ranch_390_cb8c409f55 | canon_slayverse_index_json_place_record_idx_ent_mcullen_ranch_390_cb8c409f55 | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_slayverse_index_json_place_record_idx_ent_velvet_archive_391_67ee7535a0 | canon_slayverse_index_json_place_record_idx_ent_velvet_archive_391_67ee7535a0 | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_slayverse_index_json_place_record_idx_ent_club_cosmic_392_ecae634ca9 | canon_slayverse_index_json_place_record_idx_ent_club_cosmic_392_ecae634ca9 | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_slayverse_index_json_place_record_idx_ent_wyoming_rift_393_9cdec3bb42 | canon_slayverse_index_json_place_record_idx_ent_wyoming_rift_393_9cdec3bb42 | medium | record_type/extraction_kind indicates PLACE | canon/slayverse_index.json |
| canon_story_arcs_story_arcs_md_story_arc_note_season_3_the_soul_line_opens_sketched_2220_8cd45210e4 | Velvet Archive | high | explicit Slayverse dictionary match in BODY: Velvet Archive | canon/story_arcs/story_arcs.md |
| canon_story_arcs_story_arcs_md_story_arc_note_the_federstahl_lattice_incident_full_2221_b7c76af514 | Wyoming Rift | high | explicit Slayverse dictionary match in BODY: Wyoming Rift | canon/story_arcs/story_arcs.md |
| canon_story_arcs_story_arcs_md_story_arc_note_the_six_other_fissures_hook_only_2224_1590324e85 | Wyoming | high | explicit Slayverse dictionary match in BODY: Wyoming | canon/story_arcs/story_arcs.md |

## 11. Top THING candidates

| id | dominant_noun_phrase | confidence | reason | source |
|---|---|---|---|---|
| canon_artifacts_artifacts_md_artifact_note_preface_preface_222_906a2058d9 | canon_artifacts_artifacts_md_artifact_note_preface_preface_222_906a2058d9 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_hildebrand_s_ring_moderate_223_c6980df7f6 | canon_artifacts_artifacts_md_artifact_note_hildebrand_s_ring_moderate_223_c6980df7f6 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_thread_full_224_0116d6a8ed | canon_artifacts_artifacts_md_artifact_note_the_thread_full_224_0116d6a8ed | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_zerethium_quartz_moderate_225_baaa4a5b77 | canon_artifacts_artifacts_md_artifact_note_zerethium_quartz_moderate_225_baaa4a5b77 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_crystal_shard_federstahl_crystal_full_226_a41fef2b66 | canon_artifacts_artifacts_md_artifact_note_the_crystal_shard_federstahl_crystal_full_226_a41fef2b66 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_dustbrand_sigil_full_227_87d9c49ed5 | canon_artifacts_artifacts_md_artifact_note_the_dustbrand_sigil_full_227_87d9c49ed5 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_forbidden_suitcase_hook_only_228_53a64c223e | canon_artifacts_artifacts_md_artifact_note_the_forbidden_suitcase_hook_only_228_53a64c223e | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_collapsible_mirror_fan_hook_only_229_198fa06b38 | canon_artifacts_artifacts_md_artifact_note_the_collapsible_mirror_fan_hook_only_229_198fa06b38 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_double_hemline_dagger_pouch_hook_only_230_289c1e11b5 | canon_artifacts_artifacts_md_artifact_note_the_double_hemline_dagger_pouch_hook_only_230_289c1e11b5 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_slayton_particles_glamorons_full_231_61da20099f | canon_artifacts_artifacts_md_artifact_note_slayton_particles_glamorons_full_231_61da20099f | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_slayton_codex_moderate_232_2f89343864 | canon_artifacts_artifacts_md_artifact_note_the_slayton_codex_moderate_232_2f89343864 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_federkreis_devices_sketched_233_4456f47d6e | canon_artifacts_artifacts_md_artifact_note_federkreis_devices_sketched_233_4456f47d6e | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_brass_kaleidoscopes_hook_only_234_a66ad5969f | canon_artifacts_artifacts_md_artifact_note_brass_kaleidoscopes_hook_only_234_a66ad5969f | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_the_emotional_hemline_hook_only_235_a562b28753 | canon_artifacts_artifacts_md_artifact_note_the_emotional_hemline_hook_only_235_a562b28753 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_vuorse_s_mic_sketched_236_03d2e1f495 | canon_artifacts_artifacts_md_artifact_note_vuorse_s_mic_sketched_236_03d2e1f495 | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_artifacts_artifacts_md_artifact_note_seal_vi_the_slayton_loop_sketched_237_e516f55dde | canon_artifacts_artifacts_md_artifact_note_seal_vi_the_slayton_loop_sketched_237_e516f55dde | medium | source path hint indicates THING: canon/artifacts/artifacts.md | canon/artifacts/artifacts.md |
| canon_slayverse_index_json_artifact_record_idx_ent_the_thread_394_c4beeeed7b | canon_slayverse_index_json_artifact_record_idx_ent_the_thread_394_c4beeeed7b | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |
| canon_slayverse_index_json_artifact_record_idx_ent_crystal_shard_395_6737c1dbff | canon_slayverse_index_json_artifact_record_idx_ent_crystal_shard_395_6737c1dbff | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |
| canon_slayverse_index_json_artifact_record_idx_ent_dustbrand_sigil_396_33cbb0204d | canon_slayverse_index_json_artifact_record_idx_ent_dustbrand_sigil_396_33cbb0204d | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |
| canon_slayverse_index_json_artifact_record_idx_ent_zerethium_quartz_397_a9655a20d9 | canon_slayverse_index_json_artifact_record_idx_ent_zerethium_quartz_397_a9655a20d9 | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |
| canon_slayverse_index_json_artifact_record_idx_ent_hildebrands_ring_398_049e2b9b67 | canon_slayverse_index_json_artifact_record_idx_ent_hildebrands_ring_398_049e2b9b67 | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |
| canon_slayverse_index_json_artifact_record_idx_ent_glamorons_399_72f258daec | canon_slayverse_index_json_artifact_record_idx_ent_glamorons_399_72f258daec | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |
| canon_slayverse_index_json_artifact_record_idx_ent_slayton_codex_400_e195ec3931 | canon_slayverse_index_json_artifact_record_idx_ent_slayton_codex_400_e195ec3931 | medium | record_type/extraction_kind indicates THING | canon/slayverse_index.json |

## 12. Top IDEA candidates

| id | dominant_noun_phrase | confidence | reason | source |
|---|---|---|---|---|
| canon_cosmology_cosmology_md_cosmology_note_preface_preface_268_fe450b6c7a | canon_cosmology_cosmology_md_cosmology_note_preface_preface_268_fe450b6c7a | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_thread_full_269_6a94fae143 | canon_cosmology_cosmology_md_cosmology_note_the_thread_full_269_6a94fae143 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_slayton_energy_the_slayton_force_full_270_c0f5b018a8 | canon_cosmology_cosmology_md_cosmology_note_slayton_energy_the_slayton_force_full_270_c0f5b018a8 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_glamorons_full_271_b0b93f13e3 | canon_cosmology_cosmology_md_cosmology_note_glamorons_full_271_b0b93f13e3 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_quantum_eleganza_moderate_272_be2e390ae7 | canon_cosmology_cosmology_md_cosmology_note_quantum_eleganza_moderate_272_be2e390ae7 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_cosmic_snap_sketched_273_704c70a7ce | canon_cosmology_cosmology_md_cosmology_note_the_cosmic_snap_sketched_273_704c70a7ce | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_original_experiment_274_963d7af33f | canon_cosmology_cosmology_md_cosmology_note_the_original_experiment_274_963d7af33f | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_seven_fissures_275_f710220bda | canon_cosmology_cosmology_md_cosmology_note_the_seven_fissures_275_f710220bda | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_blood_resonance_276_45cc19ce7c | canon_cosmology_cosmology_md_cosmology_note_blood_resonance_276_45cc19ce7c | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_corrective_chronogenesis_277_d90465e41e | canon_cosmology_cosmology_md_cosmology_note_corrective_chronogenesis_277_d90465e41e | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_soul_line_vs_the_bloodline_full_278_2eefefbf4f | canon_cosmology_cosmology_md_cosmology_note_the_soul_line_vs_the_bloodline_full_278_2eefefbf4f | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_vessel_concept_full_279_9af4e51b49 | canon_cosmology_cosmology_md_cosmology_note_the_vessel_concept_full_279_9af4e51b49 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_20_year_dormancy_moderate_280_bc5a3cf713 | canon_cosmology_cosmology_md_cosmology_note_the_20_year_dormancy_moderate_280_bc5a3cf713 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_temporal_diaspora_moderate_281_26f0485015 | canon_cosmology_cosmology_md_cosmology_note_temporal_diaspora_moderate_281_26f0485015 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_chronoline_fractures_moderate_282_33ec62f462 | canon_cosmology_cosmology_md_cosmology_note_chronoline_fractures_moderate_282_33ec62f462 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_temporal_echoes_moderate_283_c42219e38e | canon_cosmology_cosmology_md_cosmology_note_temporal_echoes_moderate_283_c42219e38e | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_quantum_silence_sketched_284_db88a01667 | canon_cosmology_cosmology_md_cosmology_note_quantum_silence_sketched_284_db88a01667 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_number_6_moderate_285_730ad1f863 | canon_cosmology_cosmology_md_cosmology_note_the_number_6_moderate_285_730ad1f863 | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_slayton_layer_sketched_286_8a0e23489c | canon_cosmology_cosmology_md_cosmology_note_the_slayton_layer_sketched_286_8a0e23489c | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_cosmology_cosmology_md_cosmology_note_the_mirror_metaphysics_full_287_2881c3a0eb | canon_cosmology_cosmology_md_cosmology_note_the_mirror_metaphysics_full_287_2881c3a0eb | medium | record_type/extraction_kind indicates IDEA | canon/cosmology/cosmology.md |
| canon_open_threads_open_threads_md_open_thread_preface_preface_302_917010b11b | Open Threads Undeveloped | medium | candidate names a doctrine/concept | canon/open_threads/open_threads.md |
| canon_organizations_organizations_md_organization_note_preface_preface_325_446104cf31 | canon_organizations_organizations_md_organization_note_preface_preface_325_446104cf31 | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_organizations_organizations_md_organization_note_golden_wingers_intergalactic_league_5903d420f0 | canon_organizations_organizations_md_organization_note_golden_wingers_intergalactic_league_5903d420f0 | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_organizations_organizations_md_organization_note_federstahl_institute_full_327_d53e9e75dd | canon_organizations_organizations_md_organization_note_federstahl_institute_full_327_d53e9e75dd | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_organizations_organizations_md_organization_note_order_of_the_seam_moderate_328_930091d133 | canon_organizations_organizations_md_organization_note_order_of_the_seam_moderate_328_930091d133 | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_organizations_organizations_md_organization_note_order_of_the_garter_s_secret_hem_sk_b021e37d2e | canon_organizations_organizations_md_organization_note_order_of_the_garter_s_secret_hem_sk_b021e37d2e | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_organizations_organizations_md_organization_note_the_veincallers_sketched_330_70e1ee6753 | canon_organizations_organizations_md_organization_note_the_veincallers_sketched_330_70e1ee6753 | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_organizations_organizations_md_organization_note_the_rustwoven_hook_only_331_a5d443ede2 | canon_organizations_organizations_md_organization_note_the_rustwoven_hook_only_331_a5d443ede2 | medium | source path hint indicates IDEA: canon/organizations/organizations.md | canon/organizations/organizations.md |
| canon_slayverse_index_json_organization_record_idx_ent_golden_wingers_401_12591150ea | canon_slayverse_index_json_organization_record_idx_ent_golden_wingers_401_12591150ea | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_organization_record_idx_ent_federstahl_institute_402_8f0e8d2695 | canon_slayverse_index_json_organization_record_idx_ent_federstahl_institute_402_8f0e8d2695 | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_organization_record_idx_ent_order_of_the_seam_403_274f21876b | canon_slayverse_index_json_organization_record_idx_ent_order_of_the_seam_403_274f21876b | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_organization_record_idx_ent_order_of_the_garters_secret_hem_404_74a9282fb7 | canon_slayverse_index_json_organization_record_idx_ent_order_of_the_garters_secret_hem_404_74a9282fb7 | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_cosmology_record_idx_ent_slayton_energy_410_c1bac1e441 | canon_slayverse_index_json_cosmology_record_idx_ent_slayton_energy_410_c1bac1e441 | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_cosmology_record_idx_ent_federstahl_lattice_411_9711245687 | canon_slayverse_index_json_cosmology_record_idx_ent_federstahl_lattice_411_9711245687 | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_cosmology_record_idx_ent_quantum_eleganza_412_913bb237c9 | canon_slayverse_index_json_cosmology_record_idx_ent_quantum_eleganza_412_913bb237c9 | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |
| canon_slayverse_index_json_cosmology_record_idx_ent_narrative_collapse_413_533af9160a | canon_slayverse_index_json_cosmology_record_idx_ent_narrative_collapse_413_533af9160a | medium | record_type/extraction_kind indicates IDEA | canon/slayverse_index.json |

## 13. Recommended next safe action

Review the UNKNOWN and [VUORSE_PRIVATE] / mythic-rumor-locked records first. Do not move anything to `synthetic_enrichment/validated/` until the Weaver reviews it. Do not deduplicate or compress until after semantic review.
