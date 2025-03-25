# voynich_agent.py

import requests
import os
from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain.prompts import PromptTemplate

# ============ CONFIGURATION ============
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0.3, model="gpt-4", openai_api_key=OPENAI_API_KEY)

FOLIOS = [
    "https://voynich.nu/q02/f015v_tr.txt",
    "https://voynich.nu/q02/f016v_tr.txt"
]

# ============ STATE DEFINITION ============
class State(dict):
    """Agent state containing framework, folio content, and logs"""
    pass

# ============ UTILITIES ============
def fetch_framework_text():
    url = "https://raw.githubusercontent.com/arieradle/voynich/main/voynich.md"
    response = requests.get(url)
    return response.text.strip() if response.status_code == 200 else ""

def fetch_folio_text(url):
    resp = requests.get(url)
    return resp.text.strip() if resp.status_code == 200 else ""

# ============ NODES ============
def load_framework_node(state):
    print("[1] Loading framework")
    framework_text = fetch_framework_text()
    return {**state, "framework_text": framework_text, "folio_index": 0, "translations": []}

def load_folio_node(state):
    print("[2] Loading folio")
    i = state["folio_index"]
    if i >= len(FOLIOS):
        return {**state, "done": True}
    folio_text = fetch_folio_text(FOLIOS[i])
    return {**state, "folio_text": folio_text, "folio_id": FOLIOS[i].split("/")[-1]}

def translate_folio_node(state):
    print("[3] Translating folio")
    prompt = PromptTemplate(
        input_variables=["framework", "text"],
        template="""
You are a translator of the Voynich Manuscript using a custom constructed language system. Apply the full framework below to translate the given EVA transliteration.

### Framework:
{framework}

### EVA Input:
{text}

Provide a clear translated version in the Herbalis language voice. Then briefly explain which rules or new patterns you found.
"""
    )
    prompt_text = prompt.format(
        framework=state.get("framework_text", ""),
        text=state["folio_text"]
    )
    result = llm.predict(prompt_text)
    return {**state, "translation_output": result}

def analyze_and_learn_node(state):
    print("[4] Analyzing translation output")
    output = state["translation_output"]
    summary_prompt = f"""
From the translation output below, identify any NEW words or meanings that seem consistent and could be added to the framework. Format them as markdown additions.

---
{output}
"""
    analysis = llm.predict(summary_prompt)
    return {**state, "framework_update": analysis}

def update_framework_node(state):
    print("[5] Updating framework")
    update = state.get("framework_update", "")
    framework = state["framework_text"]
    updated_framework = framework + "\n\n# Updates\n" + update
    return {**state, "framework_text": updated_framework}

def log_and_next_node(state):
    print("[6] Logging translation and moving to next folio")
    translations = state["translations"]
    translations.append({
        "folio": state["folio_id"],
        "translation": state["translation_output"],
        "framework_update": state.get("framework_update", "")
    })
    return {
        **state,
        "translations": translations,
        "folio_index": state["folio_index"] + 1
    }

# ============ BUILD GRAPH ============
graph = StateGraph(State)

graph.add_node("LoadFramework", load_framework_node)
graph.add_node("LoadFolio", load_folio_node)
graph.add_node("TranslateFolio", translate_folio_node)
graph.add_node("AnalyzeTranslation", analyze_and_learn_node)
graph.add_node("UpdateFramework", update_framework_node)
graph.add_node("LogAndAdvance", log_and_next_node)

# Edges
graph.set_entry_point("LoadFramework")
graph.add_edge("LoadFramework", "LoadFolio")
graph.add_conditional_edges("LoadFolio", lambda state: "END" if state.get("done") else "TranslateFolio")
graph.add_edge("TranslateFolio", "AnalyzeTranslation")
graph.add_edge("AnalyzeTranslation", "UpdateFramework")
graph.add_edge("UpdateFramework", "LogAndAdvance")
graph.add_edge("LogAndAdvance", "LoadFolio")

graph.set_finish_point("LogAndAdvance")

app = graph.compile()

if __name__ == "__main__":
    final_state = app.invoke({})
    print("\n================== FINAL OUTPUT ==================")
    for t in final_state["translations"]:
        print(f"\n### {t['folio']}\n")
        print(t['translation'])
        print("\n--- Framework Update ---\n")
        print(t['framework_update'])
