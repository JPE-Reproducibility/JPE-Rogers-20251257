## LLM API Usage & Reproducibility

⚠️ LLM API usage detected

### Cohere

- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py`:53 — `from gensim.models import CoherenceModel`

### OpenAI

- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py`:104 — `import openai`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`:301 — `from openai import OpenAI`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`:302 — `client = OpenAI(api_key=api_key)`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`:305 — `import openai`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py`:307 — `return (lambda **kw: openai.chat.completions.create(**kw)), "openai (legacy)"`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years/run_iy.py`:25 — `req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1.py`:90 — `req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/run_2_1b.py`:92 — `req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_band/run_band.py`:43 — `req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_outofband/gen.py`:45 — `req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links/run_pilot.py`:51 — `req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full.py`:51 — `req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,`
- `/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/price_links_full/run_full2.py`:67 — `req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,`

---

**A note on reproducibility.** LLM outputs are inherently non-deterministic, even when a temperature parameter is set to zero: doing so removes deliberate sampling, but proprietary APIs remain subject to silent model updates, floating-point rounding, and non-deterministic expert routing in mixture-of-experts architectures. Exact reproduction of results generated via a hosted LLM API is therefore generally not guaranteed, even by the original authors. Coqueret, Llull, Oswald, Pérignon, Scheuch & Vilhuber recommend: (1) preferring local, open-weight models where feasible, for full control over the inference environment; (2) documenting LLM implementation details per emerging reporting-guideline conventions; and (3) treating LLM outputs as draws from a distribution rather than as fixed, exactly-reproducible measurements.

See: <https://arxiv.org/abs/2607.24372>
