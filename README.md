# Shakespeare Persona LoRA — One Voice, Four Registers

A single-persona LoRA that speaks as William Shakespeare in four registers — **tragic**,
**comic**, **historical**, and **romantic** — chosen by which plays the question touches.
Built from eleven public-domain plays with the same pipeline as the
[biblical](https://github.com/beaudamore/biblical) and
[stoic](https://github.com/beaudamore/stoic) persona projects, reduced to its simplest
instance: one voice, no multi-persona switching, every step visible.

This is the teaching-sized version of the persona-LoRA pattern.

---

## What it demonstrates

| Area | Specifics |
| --- | --- |
| **Data engineering** | Regex cleaner that strips Project Gutenberg headers and footers, title pages, tables of contents and cast lists, keeping the play text from the Prologue or Act I onward. Originals are never modified. |
| **Synthetic data generation** | Sentence-aware 1,500-character chunks; 5 questions × 3 question angles per chunk, generated with Qwen3-235B via OpenRouter; voice-differentiation quality gate; raw-text continuation chunks (500 tokens, 60-token seed) that cost no API calls. |
| **Persona design** | A first-person brief (`prompts/shakespeare.md`) that defines biography, convictions, and the four registers with the plays that anchor each one. |
| **Fine-tuning** | Unsloth QLoRA on `unsloth/Qwen3-14B-unsloth-bnb-4bit`: r=32 / α=32, LR 2e-4, 4096-token sequences, inference test across all four registers, cold-reload verification of the saved adapter. |

---

## Corpus

Eleven plays from Project Gutenberg, cleaned and committed under `data/source-clean/`:

| Register | Plays |
| --- | --- |
| Tragic | *Hamlet*, *Macbeth*, *King Lear*, *Othello* |
| Comic | *A Midsummer Night's Dream*, *Much Ado about Nothing*, *Twelfth Night* |
| Historical | *King Henry V*, *King Richard III*, *Julius Caesar* |
| Romantic | *Romeo and Juliet* |

---

## Repo layout

```text
shakespeare/
├── README.md
├── prompts/shakespeare.md             Persona brief: biography, convictions, the four voices
├── data/
│   ├── scripts/clean_shakespeare.py   source-raw -> source-clean (Gutenberg boilerplate, cast lists)
│   ├── source-raw/*.txt               11 Gutenberg originals (committed)
│   ├── source-clean/*.txt             Cleaned play text (committed)
│   └── training-data/                 Generated JSONL (gitignored)
├── notebooks/
│   ├── datagen/
│   │   ├── shakespeare_datagen_v2.ipynb   Q&A + continuation, quality gate, 60/40 blend
│   │   └── shakespeare_datagen.ipynb      v1 (Q&A only), kept for diffing
│   └── loras/
│       ├── shakespeare_qwen3_14b_instruct_unsloth_4bit_v2.ipynb   Training run for the v2 data
│       └── shakespeare_qwen3_14b_instruct_unsloth_4bit.ipynb      v1
└── output/<model_name>/{train,lora_adapters}/   (gitignored)
```

---

## Running it

Notebooks run in JupyterLab inside the `unsloth-notebook` container (host port 8889).

```bash
# 1. Clean the plays (host, seconds, no GPU)
python data/scripts/clean_shakespeare.py

# 2. Datagen. Needs OPENROUTER_API_KEY in the environment or a .env file.
#    notebooks/datagen/shakespeare_datagen_v2.ipynb
#      -> data/training-data/shakespeare_persona_v2/shakespeare_combined_sharegpt.jsonl

# 3. Train. Check the GPU is free first.
docker ps                                     # stop any vllm-* / sglang-* first
#    notebooks/loras/shakespeare_qwen3_14b_instruct_unsloth_4bit_v2.ipynb

# 4. Audit the adapter before shipping it
docker exec unsloth-notebook python /workspace/training/docs/audit_adapters.py shakespeare
```

---

## Status (2026-10-06)

- Corpus cleaned and committed; persona brief written; datagen v2 and training v2 notebooks
  complete and aligned with the workspace guidelines (sentence-boundary chunking added
  2026-07-01, corrections 2026-08-25).
- No generated dataset or trained adapter is on disk yet. The next step is the datagen run,
  then the Qwen3-14B training notebook.
- A DPO stage is not written for this project; the biblical and stoic repos show the pattern
  if one is wanted.

## Related

- [biblical](https://github.com/beaudamore/biblical) — the 26-voice project this pipeline was reduced from
- [stoic](https://github.com/beaudamore/stoic) — three-voice sister project with SFT + DPO
- [circle-of-speakers-pipeline](https://github.com/beaudamore/circle-of-speakers-pipeline) — Open WebUI runtime that can host this voice in a multi-speaker circle
